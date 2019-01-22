""" Tests for example data. """

import os
import pytest
import numpy as np
import rasterio as rio
import geopandas as gpd
from earthpy.io import path_to_example


def test_invalid_datasets_raise_errors():
    """ Raise errors when users provide nonexistent datasets. """
    with pytest.raises(KeyError):
        path_to_example("Non-existent dataset")


def test_missing_datasets_raise_errors():
    """ Raise errors when users forget to provide a dataset. """
    with pytest.raises(KeyError):
        path_to_example("")


def test_valid_datasets_get_returned():
    """ If users give a valid dataset name, return a valid path. """
    epsg_path = path_to_example("epsg.json")
    assert os.path.isfile(epsg_path)


def test_rgb():
    """ Check assumptions about rgb satellite imagery over RMNP. """
    with rio.open(path_to_example("rmnp-rgb.tif")) as src:
        rgb = src.read()
        rgb_crs = src.crs
    assert rgb.shape == (3, 373, 485)
    assert str(rgb_crs) == "+init=epsg:4326"


def test_rgb_single_channels():
    """ Check assumptions about single channel R, G, and B images. """
    fnames = [path_to_example(f) for f in ["red.tif", "green.tif", "blue.tif"]]
    rgb_parts = list()
    for f in fnames:
        with rio.open(f) as src:
            rgb_parts.append(src.read())
            assert str(src.crs) == "+init=epsg:4326"

    with rio.open(path_to_example("rmnp-rgb.tif")) as src:
        assert np.array_equal(src.read(), np.concatenate(rgb_parts))


def test_colorado_counties():
    """ Check assumptions about county polygons. """
    counties = gpd.read_file(path_to_example("colorado-counties.geojson"))
    assert counties.shape == (64, 13)
    assert counties.crs == {"init": "epsg:4326"}


def test_colorado_glaciers():
    """ Check assumptions about glacier point locations. """
    glaciers = gpd.read_file(path_to_example("colorado-glaciers.geojson"))
    assert glaciers.shape == (134, 2)
    assert glaciers.crs == {"init": "epsg:4326"}


def test_continental_divide_trail():
    """ Check assumptions about Continental Divide Trail path. """
    cdt = gpd.read_file(path_to_example("continental-div-trail.geojson"))
    assert cdt.shape == (1, 2)
    assert cdt.crs == {"init": "epsg:4326"}
