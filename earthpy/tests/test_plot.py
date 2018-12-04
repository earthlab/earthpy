"""Tests for the plot module"""

import numpy as np
import pytest
import earthpy.spatial as es
# For builds on travis to avoid plot display errors
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
plt.show = lambda: None



""" General functions for matplotlib elements """


# Create tuple
tuups = (1, 2)
im = np.random.randint(10, size=(2, 4, 5))

def test_arr_parameter():
    """Raise an AttributeError if an array is not provided."""
    with pytest.raises(AttributeError):
        es.plot_bands(arr=tuups)

def test_num_titles():
    """If a user provides two titles for a single band array, the function
    should raise an error OR if the title list is a different length than
    the array it should also raise an errors"""

    single_band = im[0]

    with pytest.raises(ValueError):
        es.plot_bands(arr=single_band,
                      title=["Title1", "Title2"])
    with pytest.raises(ValueError):
        es.plot_bands(arr=im,
                      title=["Title1", "Title2", "Title3"])

def test_num_axes():
    """If provided with a 2 band array, plot_bands should return 3 axes by
    default"""
    fig, ax = es.plot_bands(im)
    assert len(fig.axes) == 3


def test_two_plot_title():
    """Test that the default title is provided for a 2 band array plot"""
    fig, ax = es.plot_bands(im)
    ax = fig.axes
    num_plts = im.shape[0]
    # Get titles
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ['Band 1', 'Band 2']


def test_custom_plot_title():
    """Test that the custom title is applied for a 2 band array plot"""
    im = np.indices((4, 4))
    fig, ax = es.plot_bands(im, title=["Red Band", "Green Band"])
    ax = fig.axes
    num_plts = im.shape[0]
    # Get titles
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ['Red Band', 'Green Band']


def test_single_band_3dims():
    """If you provide a single band array with 3 dimensions (shape[0]==1
    test that it still plots and only returns a single axis"""

    single_band_3dims = np.random.randint(10, size=(1, 4, 5))
    fig, ax = es.plot_bands(single_band_3dims)
    # Get array from mpl figure
    arr = fig.axes[0].get_images()[0].get_array()
    assert arr.ndim == 2
    assert len(fig.axes[0].get_images()) == 1


def test_single_band_2dims():
    """If you provide a single band array with 3 dimensions (shape[0]==1
    test that it still plots and only returns a single axis"""

    single_band_2dims = np.random.randint(10, size=(4, 5))
    fig, ax = es.plot_bands(single_band_2dims)
    # Get array from mpl figure
    arr = fig.axes[0].get_images()[0].get_array()
    assert arr.ndim == 2
    assert len(fig.axes[0].get_images()) == 1

