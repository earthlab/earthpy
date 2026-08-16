"""
Tests for appears module
"""

import logging


import geopandas as gpd
import pytest

import earthpy.api.appeears as etapi


@pytest.mark.slow
@pytest.mark.vcr()
def test_download_data():
    logging.basicConfig(level=logging.DEBUG)

    quotes_url = (
        "https://github.com/earthlab/earthpy/releases/download/v0.9.4"
        "/test-boundary.zip"
    )
    gdf = gpd.read_file(quotes_url)
    downloader = etapi.AppeearsDownloader(
        "MOD13Q1.061",
        "_250m_16_days_NDVI",
        "01-01-2021",
        "01-20-2021",
        gdf,
        download_key="earthpy-test",
        interactive=False,
    )
    downloader.download_files()


@pytest.mark.slow
@pytest.mark.vcr()
def test_download_recurring_data():
    logging.basicConfig(level=logging.DEBUG)

    quotes_url = (
        "https://github.com/earthlab/earthpy/releases/download/v0.9.4"
        "/test-boundary.zip"
    )
    gdf = gpd.read_file(quotes_url)
    downloader = etapi.AppeearsDownloader(
        product="MOD13Q1.061",
        layer="_250m_16_days_NDVI",
        start_date="01-01",
        end_date="01-20",
        recurring=True,
        year_range=[2021, 2022],
        polygon=gdf,
        download_key="earthpy-test-recurring",
        interactive=False,
    )
    downloader.download_files()
