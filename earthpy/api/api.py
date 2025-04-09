"""
earthpy.api
================

A module to download data using various APIs.

"""

import getpass
import json
import logging
import os
import pathlib
import re
import secrets
import time
from glob import glob

import keyring
import requests
import sqlite3

from ..io import HOME, DATA_NAME

class APIDownloader(object):
    """
    Parent class to download data from APIs

    Parameters
    ----------
    download_label : str, optional
        Label used in data_dir and as the API job label
    project_dir : pathlike, optional
        Replacement directory for ~/earth-analytics/data/
    date_template: pd.DatetimeIndex
        Match date range with an existing DatetimeIndex
    start_date : date-like, optional
        Start date, parseable by pd.to_datetime(). Default
        is the most recent
    end_date : date-like, optional
        End date, parseable by pd.to_datetime()
    start_doy : str, optional
        Day of the year to start a recurring date range
    end_doy : str, optional
        Day of the year to end a recurring date range
    months : iterable of str or int, optional
        Iterable of month names or numbers.
    seasons : str, optional
        Names of seasons to download on an annually recurring basis.
        Seasons correspond to pandas DateTimeOffset conventions.
    start_year : str or int
        Start year for annually recurring dates, as YYYY or 'YYYY'
    end_year : str or int
        End year for annually recurring dates, as YYYY or 'YYYY'
    area_of_interest : gpd.GeoDataFrame, shapely geometry, or bounding box, optional
        The spatial boundary to subset. Bounding boxes should
        match GeoDataFrame.total_bounds style.
        auth_method : 
        
    Attributes
    ----------
    base_url : str
        The API endpoint url
    data_dir : pathlike
        Path to store data in. Default: ~/earth-analytics/data/{project_dir}
    download_label : str
        Label used in data_dir and as the API job label.
    """
    
    base_url = NotImplemented
    
    def __init__(
            self, 
            download_label="earthpy-downloads",
            project_dir=os.path.join(HOME, DATA_NAME), 
            start_date=None, end_date=None, 
            start_doy=None, end_doy=None, months=None, seasons=None, 
            start_year=None, end_year=None,
            area_of_interest=None,
            resubmit_in_progress=False,
            auth_method='keyring'):
            
        # Initialize file structure
        self.download_label = download_label
        self.project_dir = project_dir
        self.download_dir = os.path.join(self.project_dir, self.download_label)
        os.makedirs(self.download_dir, exist_ok=True)
        self.db_path = os.path.join(self.download_dir, 'db.sqlite')

        # Initialize database
        self._init_database()

        # Find any identical submissions in progress
        

        # Initialize universal parameters
        self.start_date = start_date
        self.end_date = end_date
        self.start_doy = start_doy
        self.end_doy = end_doy
        self.months = months
        self.seasons = seasons
        self.start_year = start_year
        self.end_year = end_year
        self.area_of_interest = area_of_interest



        self.auth_method = auth_method
        
        # Set up task id
        self.task_id_path = os.path.join(
            pathlib.Path.home(), '.appeears_taskid')
        if os.path.exists(self.task_id_path):
            with open(self.task_id_path, 'r') as task_id_file:
                self._task_id = task_id_file.readline()
        else:
            self._task_id = None
        
        # Set up download path
        self.download_key = download_key
    
        self.data_dir = os.path.join(ea_dir, download_key)

    def _init_public_api_attributes(self):
        pass

    def _init_private_api_attributes(self):
        pass

    def _init_database(self):
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Create the download_requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS download_requests (
                    request_id INTEGER PRIMARY KEY,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
            ''')
            # Create the file_downloads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_downloads (
                    download_id INTEGER PRIMARY KEY,
                    request_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    status TEXT NOT NULL,
                    size INTEGER,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(request_id) REFERENCES download_requests(request_id)
                );
            ''')
            conn.commit()

        
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
        
        logging.info('Submitting {} request...'.format(endpoint))
        
        kwargs = {
            'url': self.base_url + endpoint.format(**parameters),
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
        
    
    def login(self, service='NASA_EARTHDATA', username_id='NED_USERNAME'):
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
        # Get username and password from keyring
        try:
            username = keyring.get_password(service, username_id)
            password = keyring.get_password(service, username)
        except:
            username = None
            password = None
            
        # Get username and password from environment
        try:
            username = os.environ['EARTHDATA_USERNAME']
            password = os.environ['EARTHDATA_PASSWORD']
        except:
            username = None
            password = None
        
        # Prompt user if no username or password is stored
        if (username is None) or (password is None):
            # Ask for the user's username and password
            username = input('NASA Earthdata Username: ')
            password = getpass.getpass('NASA Earthdata Password: ')
            try:
                keyring.set_password(service, username_id, username)
                keyring.set_password(service, username, password)
            except:
                pass
            
        logging.info('Logging into AppEEARS API...')
        
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
            self.login()
        return self._auth_header
    
    @property
    def task_id(self):
        if not self._task_id:
            self.submit_task_request()
        return self._task_id
    
    @property
    def task_status(self):
        if self._status != 'done':
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
        status = self.task_status
        logging.info('Current task status: {}'.format(status))
        
        # Get file download information
        bundle_response = self.appeears_request(
            'bundle/{task_id}', 
            method='GET',
            task_id=self.task_id)
        
        files = bundle_response.json()['files']
        
        '{} files available for download'.format(len(files))
        
        # Download files
        for file_info in files:
            # Get a stream to the bundle file
            response = self.appeears_request(
                'bundle/{task_id}/{file_id}',
                method='GET', task_id=self.task_id, stream=True,
                file_id=file_info['file_id'])
            
            # Create a destination directory to store the file in
            filepath = os.path.join(self.data_dir, file_info['file_name'])
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
                
            # Write the file to the destination directory
            if os.path.exists(filepath) and cache:
                logging.info(
                    'File at {} alreading exists. Skipping...'
                    .format(filepath))
            else:
                logging.info('Downloading file {}'.format(filepath))
                with open(filepath, 'wb') as f:
                    for data in response.iter_content(chunk_size=8192):
                        f.write(data)
        
        # Remove task id file when download is complete
        os.remove(self.task_id_path)