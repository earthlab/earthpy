"""Tests for the plot bands function"""

import numpy as np
import pytest
import matplotlib as mpl

mpl.use("TkAgg")
import matplotlib.pyplot as plt
import earthpy.plot as ep

plt.show = lambda: None


def test_arr_parameter():
    """Raise an AttributeError if an array is not provided."""
    with pytest.raises(
        AttributeError, match="Input arr should be a numpy array"
    ):
        ep.plot_bands(arr=(1, 2))
    plt.close()


def test_num_titles(image_array_2bands):
    """Test the number of titles.

    If a user provides two titles for a single band array, the function
    should raise an error OR if the title list is a different length than
    the array it should also raise an errors.
    """
    single_band = image_array_2bands[0]

    with pytest.raises(
        ValueError,
        match="plot_bands expects one title for a single band array",
    ):
        ep.plot_bands(arr=single_band, title=["Title1", "Title2"])
    with pytest.raises(ValueError, match="plot_bands() expects the number"):
        ep.plot_bands(
            arr=image_array_2bands, title=["Title1", "Title2", "Title3"]
        )
    plt.close()


def test_str_for_title(image_array_2bands):
    """Test that a single string title renders properly """

    single_band = image_array_2bands[0]
    ax = ep.plot_bands(arr=single_band, title="my title")
    plot_title = ax.get_title()
    assert "my title" in plot_title
    plt.close()


def test_num_axes(image_array_2bands):
    """Test the number of axes.

    If provided with a 2 band array, plot_bands should return 3 axes.
    """
    ax = ep.plot_bands(image_array_2bands)
    assert len(ax) == 3
    plt.close()


def test_two_plot_title(image_array_2bands):
    """Test that the default title is provided for a 2 band array plot."""

    ax = ep.plot_bands(image_array_2bands)
    num_plts = image_array_2bands.shape[0]
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ["Band 1", "Band 2"]
    plt.close()


def test_custom_plot_title(image_array_2bands):
    """Test that the custom title is applied for a 2 band array plot."""
    ax = ep.plot_bands(image_array_2bands, title=["Red Band", "Green Band"])
    num_plts = image_array_2bands.shape[0]
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ["Red Band", "Green Band"]
    plt.close()


def test_single_band_3dims(one_band_3dims):
    """Test single band plot with three dimensions.

    If you provide a single band array with 3 dimensions (shape[0]==1
    test that it still plots and only returns a single axis.
    """
    ax = ep.plot_bands(one_band_3dims)
    arr = ax.get_images()[0].get_array()
    assert arr.ndim == 2
    assert len(ax.get_images()) == 1
    plt.close()


def test_single_band_2dims(one_band_3dims):
    """Test single band plot with two dimensions

    If you provide a single band array with 3 dimensions (shape[0] == 1)
    test that it still plots and only returns a single axis.
    """
    single_band_2dims = one_band_3dims[0]
    ax = ep.plot_bands(single_band_2dims)
    # Get array from mpl figure
    arr = ax.get_images()[0].get_array()
    assert arr.ndim == 2
    assert len(ax.get_images()) == 1
    plt.close()
