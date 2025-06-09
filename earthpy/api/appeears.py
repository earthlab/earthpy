"""
earthpy.appeears
================

A module to download data using the APPPEARS API.

NOTE TO DEVS:
  - Allow the option to overwrite the keychain
  - Validate the year range parameter

"""

import getpass
import json
import logging
import os
import pathlib
import re
import time
from glob import glob

import keyring
import netrc
import requests

from earthpy import Project
from .api import APIDownloader
from .auth import Authenticator


class AppeearsDownloader(APIDownloader):
    """
    Class to download data using the appeears API
    
    appeears (Application for Extracting and Exploring Analysis 
    Ready Samples) offers a simple and efficient way to access 
    and transform geospatial data from a variety of federal (US)
    data archives. This class implements a subset of the API 
    features. Usage requires and Earthdata Login, available
    from https://urs.earthdata.nasa.gov/. More information 
    about the application is available at
    https://appeears.earthdatacloud.nasa.gov/.

    Parameters
    ----------
    download_key : str, optional
        Label used in the project directory and as the API job label
    project : earthpy.Project, optional
        An Earthpy Project object to use for data storage.
        If not provided, a default project is created.
    product : str
        A product code from 
        https://appeears.earthdatacloud.nasa.gov/products
    layer : str
        A layer code from 
        https://appeears.earthdatacloud.nasa.gov/products
    start_date : str
        Start date for data subset, as 'MM-DD-YYYY' 
        or 'MM-DD' if recurring
    end_date : str
        End date for data subset, as 'MM-DD-YYYY' 
        or 'MM-DD' if recurring
    recurring : bool
        Whether the date range recurs each year. 
        Requires year_range.
    year_range : str
        Year range for recurring dates, as '[YYYY,YYYY]'
    polygon: gpd.GeoDataFrame
        The spatial boundary to subset
        
    Attributes
    ----------
    base_url : str
        The appeears API url
    download_key : str
        Label used in project and as the API job label
    auth_header : str
        Authentication header to use for AppEEARS commands
    task_id : str
        Task ID assigned by AppEEARS
    """
    
    base_url = "https://appeears.earthdatacloud.nasa.gov/api/"
    login_service = "urs.earthdata.nasa.gov"
    download_key = "appeears"
    
    def __init__(
            self,
            product, layer, start_date, end_date, polygon, 
            recurring=False, year_range=None,
            download_key="appeears", project=None, 
            interactive=True, override=False):
            
        # Initialize attributes
        self._product = product
        self._layer = layer
        self._start_date = start_date
        self._end_date = end_date
        self._recurring = recurring
        self._year_range = year_range
        self._polygon = polygon
        self._interactive = interactive
        self._override = override
        
        self._auth_header = None
        self._status = None
        
        # Set up task id
        self.task_id_path = pathlib.Path.home() / '.appeears_taskid'
        if self.task_id_path.exists():
            with open(self.task_id_path, 'r') as task_id_file:
                self._task_id = task_id_file.readline()
        elif 'APPEEARS_TASKID' in os.environ:
            self._task_id = os.environ['APPEEARS_TASKID']
            with open(self.task_id_path, 'w') as task_id_file:
                task_id_file.write(self._task_id)
        else:
            self._task_id = None
        
        # Set up download path
        self.download_key = download_key
        self.project = project or Project()
        self.download_dir = self.project.project_dir / self.download_key
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def appeears_request(
            self, endpoint, 
            method='POST', req_json=None, stream=False,
            **parameters):
        """
        Submits a request to the AppEEARS API

        Parameters
        ----------
        endpoint : str
            The API endpoint from 
            https://appeears.earthdatacloud.nasa.gov/api/
        method : str
            HTTP method 'GET' or 'POST'
        json : dictlike, optional
            JSON to submit with the request (for the task endpoint)
        **parameters : dict, optional
            Named parameters to format into the endpoint
        """
        endpoint = endpoint.format(**parameters)
        logging.info('Submitting {} request...'.format(endpoint))
        
        kwargs = {
            'url': self.base_url + endpoint,
            'headers': {'Authorization': self.auth_header}
        }
        if req_json:
            logging.debug('Submitting task with JSON\n{}'.format(
                json.dumps(req_json)))
            kwargs['json'] = req_json
            
        # Stream file downloads
        if stream:
            kwargs['allow_redirects'] = True
            kwargs['stream'] = True
        
        # Submit request
        response = requests.request(method=method, **kwargs)
        logging.debug('RESPONSE TEXT: \n{}'.format(response.text))
        response.raise_for_status()
        
        logging.info('{} request successfully completed'.format(endpoint))
        
        return response
        
    
    def login(self, interactive=True, override=False):
        """
        Logs in to the AppEEARS API.

        Login happens automatically when self.auth_header is
        requested. Call this function to use a customized
        service name in the keyring, or set the self._auth_header
        value manually for other custom situations.

        Parameters
        ----------
        service : str, optional
            The name under which to store the credential in keyring
        """
        username, password = Authenticator(
            service=self.login_service,
            env_prefix='EARTHDATA'
        ).get_credentials(interactive=interactive, override=override)
        
        # Set up authentication and submit login request
        login_resp = requests.post(
            self.base_url + 'login', 
            auth=(username, password))
        login_resp.raise_for_status()
        
        self._auth_header = (
            '{token_type} {token}'.format(**login_resp.json()))
        
        logging.info(
            'Login successful. Auth Header: {}'.format(self._auth_header))
        
    @property
    def auth_header(self):
        if not self._auth_header:
            self.login(interactive=self._interactive, override=self._override)
        return self._auth_header
    
    @property
    def task_id(self):
        if not self._task_id:
            self.submit_task_request()
        return self._task_id
    
    @property
    def task_status(self):
        if self._status!='done':
            self.wait_for_task()
        return self._status

    def submit_task_request(self):
        """
        Submit task request for the object parameters

        This function is automatically called when self.task_id
        is requested. Set self._task_id to override.
        """
        # Task parameters
        task = {
            'task_type': 'area',
            'task_name': self.download_key,
            'params': {
                'dates': [
                    {
                        'startDate': self._start_date,
                        'endDate': self._end_date
                    }
                ],
                'layers': [
                    {
                        'product': self._product,
                        'layer': self._layer
                    }
                ],
                # Need subdivisions as json, not as a string
                "geo": json.loads(self._polygon.dissolve().envelope.to_json()), 
                "output": {
                    "format": {"type": "geotiff"}, 
                    "projection": "geographic"
                }
            }
        }
        
        if self._recurring:
            if self._year_range is None:
                raise ValueError(
                    'Must supply year range for recurring dates')
            task['params']['dates'][0]['recurring'] = True
            task['params']['dates'][0]['yearRange'] = self._year_range

        # Submit the task request
        task_response = self.appeears_request('task', req_json=task)
        
        # Save task ID for later
        self._task_id = task_response.json()['task_id']
        with open(self.task_id_path, 'w') as task_id_file:
            task_id_file.write(self._task_id)

    def wait_for_task(self):
        """
        Waits for the AppEEARS service to prepare data subset
        """
        self._status = 'initializing'
        while self._status != 'done':
            time.sleep(3)
            if self._status=='expired' or self._status=='deleted':
                self.submit_task_request()
            # Wait 20 seconds in between status checks
            if self._status != 'initializing':
                time.sleep(20)
                
            # Check status
            status_response = self.appeears_request(
                'status/{task_id}', method='GET', task_id=self.task_id)
            
            # Update status
            if 'progress' in status_response.json():
                self._status = status_response.json()['progress']['summary']
            elif 'status' in status_response.json():
                self._status = status_response.json()['status']
            
            logging.info(self._status)
        logging.info('Task completed - ready for download.')
    
    def download_files(self, cache=True):
        """
        Streams all prepared file downloads

        Parameters
        ----------
        cache : bool
            Use cache to avoid repeat downloads
        """
        if cache:
            existing_files = self.download_dir.rglob('*')
            if len(list(existing_files))>0:
                logging.info(
                    f'Files already exist in {self.download_dir}. '
                    'Set cache=False to overwrite.')
                return existing_files
        
        # Check task status
        status = self.task_status
        logging.info('Current task status: {}'.format(status))
        
        # Get file download information
        bundle_response = self.appeears_request(
            'bundle/{task_id}', 
            method='GET',
            task_id=self.task_id)
        
        files = bundle_response.json()['files']
        
        logging.info('{} files available for download'.format(len(files)))
        
        # Download files
        for file_info in files:
            # Get a stream to the bundle file
            response = self.appeears_request(
                'bundle/{task_id}/{file_id}',
                method='GET', task_id=self.task_id, stream=True,
                file_id=file_info['file_id'])
            
            # Create a destination directory to store the file in
            filepath = self.download_dir / file_info['file_name']
                
            # Write the file to the destination directory
            if filepath.exists() and cache:
                logging.info(
                    'File at {} alreading exists. Skipping...'
                    .format(filepath))
            else:
                logging.info('Downloading file {}'.format(filepath))
                # Ensure the parent directory exists
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'wb') as f:
                    for data in response.iter_content(chunk_size=8192):
                        f.write(data)
        
        # Remove task id file when download is complete
        os.remove(self.task_id_path)
