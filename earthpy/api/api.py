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

from ..project import Project

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
            start_date=None, end_date=None, 
            start_doy=None, end_doy=None, months=None, seasons=None, 
            start_year=None, end_year=None,
            area_of_interest=None,
            resubmit_in_progress=False,
            auth_method='keyring'):
        # Initialize project
        if 'EARTHPY_PROJECT_DATA_DIR' in os.environ:
            self.project_dir = os.environ['EARTHPY_PROJECT_DATA_DIR']
        else:
            self.project_dir = Project().project_dir
        
        # Initialize file structure
        self.download_label = download_label
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