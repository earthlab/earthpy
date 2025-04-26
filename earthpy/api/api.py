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
    download_key = NotImplemented