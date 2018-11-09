"""Tests for the plot module"""

import numpy as np
import pytest
import earthpy.spatial as es



""" General functions for matplotlib elements """


# Create tuple
tuups = (1, 2)

im = np.random.randint(10, size=(2, 4, 5))
single_band = im[0]


def test_arr_parameter():
    """Test that a bounding box returns error if the extents don't overlap"""
    with pytest.raises(AttributeError):
        es.plot_bands(arr=tuups)

def test_num_titles():
    """If a user provides two titles for a single band array, the function
    should raise an error"""

    with pytest.raises(AssertionError):
        es.plot_bands(arr=single_band,
                      title=["Title1", "Title2"])


def test_num_axes():
    """If provided with a 2 band array, plot_bands should return 3 axes by
    default"""
    fig, ax = es.plot_bands(im)
    assert len(fig.axes) == 3


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
