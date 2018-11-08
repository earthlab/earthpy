"""Tests for the plot module"""

import numpy as np
import pytest
from shapely.geometry import Polygon, Point, LineString
import shapely
import geopandas as gpd
import earthpy.spatial as es
import earthpy.clip as cl


""" General functions for matplotlib elements """


# Create tuple
tuups = (1, 2)

im = np.indices((3, 3))


def test_arr_parameter():
    """Test that a bounding box returns error if the extents don't overlap"""
    with pytest.raises(ValueError):
        es.plot_bands(arr=tuups)

def test_num_titles():
    """Test that a bounding box returns error if the extents don't overlap"""
    with pytest.raises(ValueError):
        es.plot_bands(arr=tuups, title=["Title1", "Title2"])

def test_num_axes():
    """If provided with a 2 band array, plot_bands should return 3 axes by
    default"""
    fig, ax = es.plot_bands(im)

    with pytest.raises(ValueError):
        len(fig.axes) == 3


def test_two_plot_title():
    """Test that the default title is provided for a 2 band array plot"""
    fig, ax = es.plot_bands(im)
    num_plts = im.shape[0]
    # Get titles
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ['Band 1', 'Band 2']


def test_custom_plot_title():
    """Test that the custom title is applied for a 2 band array plot"""
    im = np.indices((4, 4))
    fig, ax = es.plot_bands(im, title=["Red Band", "Green Band"])
    num_plts = im.shape[0]
    # Get titles
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ['Red Band', 'Green Band']
