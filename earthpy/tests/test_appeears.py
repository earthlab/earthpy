"""
Tests for appears module
"""

import os
import logging
import pathlib


import geopandas as gpd
import earthpy.api.appeears as etapi

def test_download_data():
	logging.basicConfig(level=logging.DEBUG)
	
	quotes_url = (
		"https://opendata.arcgis.com/datasets/955e7a0f5"
		"2474b60a9866950daf10acb_0.zip"
	)
	gdf = gpd.read_file(quotes_url)
	downloader = etapi.AppeearsDownloader(
		'MOD13Q1.061', '_250m_16_days_NDVI', '01-01-2021', '01-20-2021', gdf)
	downloader.download_files()
	
def test_download_recurring_data():
	logging.basicConfig(level=logging.DEBUG)
	
	quotes_url = (
		"https://opendata.arcgis.com/datasets/955e7a0f5"
		"2474b60a9866950daf10acb_0.zip"
	)
	gdf = gpd.read_file(quotes_url)
	downloader = etapi.AppeearsDownloader(
		product='MOD13Q1.061', 
		layer='_250m_16_days_NDVI', 
		start_date='01-01', 
		end_date='01-20', 
		recurring=True,
		year_range=[2021, 2022],
		polygon=gdf)
	downloader.download_files()