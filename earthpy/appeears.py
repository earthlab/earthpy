"""
earthpy.appeears
================

A module to download data using the APPPEARS API.

"""

import getpass
import json
import logging
import os
import pathlib
import re
import requests
import time
from glob import glob

import keyring

class AppeearsDownloader(object):
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
	download_key: str, optional
		Label used in data_dir and as the API job label
	ea_dir: pathlike, optional
		Replacement directory for ~/earth-analytics
	product: str
		A product code from 
		https://appeears.earthdatacloud.nasa.gov/products
	layer: str
		A layer code from 
		https://appeears.earthdatacloud.nasa.gov/products
	start_date: str
		Start date for data subset, as 'MM-DD-YYYY'
	end_date: str
		End date for data subset, as 'MM-DD-YYYY'
	polygon: gpd.GeoDataFrame
		The spatial boundary to subset
		
	Attributes
	----------
	base_url : str
		The appeears API url
	data_dir : pathlike
		Path to store data in. Default: ~/earth-analytics/appeears-data
	download_key : str
		Label used in data_dir and as the API job label
	auth_header : str
		Authentication header to use for AppEEARS commands
	task_id : str
		Task ID assigned by AppEEARS
	"""
	
	base_url = "https://appeears.earthdatacloud.nasa.gov/api/"
	
	def __init__(
			self,
			product, layer, start_date, end_date, polygon, 
			recurring=False, year_range=None,
			download_key="appeears", ea_dir=None):
		# Initialize attributes
		self._product = product
		self._layer = layer
		self._start_date = start_date
		self._end_date = end_date
		self._recurring = recurring
		self._year_range = year_range
		self._polygon = polygon
		
		self._task_id = None
		self._auth_header = None
		self._status = None
		
		# Set up file paths
		self.download_key = download_key
		if ea_dir is None:
			ea_dir = os.path.join(pathlib.Path.home(), 'earth-analytics')
		self.data_dir = os.path.join(ea_dir, download_key)
		
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
			kwargs['json'] = req_json
			
		# Stream file downloads
		if stream:
			kwargs['allow_redirects'] = True
			kwargs['stream'] = True
		
		# Submit request
		response = requests.request(method=method, **kwargs)
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
		username = keyring.get_password(service, username_id)
		password = keyring.get_password(service, username)
		
		# Prompt user if no username or password is stored
		if (username is None) or (password is None):
			# Ask for the user's username and password
			username = input('NASA Earthdata Username: ')
			password = getpass.getpass('NASA Earthdata Password: ')
			keyring.set_password(service, username_id, username)
			keyring.set_password(service, username, password)
			
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
			if self.year_range is None:
				raise ValueError(
					'Must supply year range for recurring dates')
			task['params']['dates'][0]['recurring'] = True
			task['params']['dates'][0]['yearRange'] = self._year_range

		# Submit the task request
		task_response = self.appeears_request('task', req_json=task)
		
		# Save task ID for later
		self._task_id = task_response.json()['task_id']


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
			if os.path.exits(filepath) and cache:
				logging.info(
					'File at {} alreading exists. Skipping...'
					.format(filepath))
			else:
				logging.info('Downloading file {}'.format(filepath))
				with open(filepath, 'wb') as f:
					for data in response.iter_content(chunk_size=8192):
						f.write(data)