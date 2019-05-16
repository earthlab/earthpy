"""Tests for the plot bands function"""

import pytest
import matplotlib.pyplot as plt
import earthpy.plot as ep
import numpy as np

plt.show = lambda: None


@pytest.fixture
def one_band_3dims():
    """Return a 3-dim numpy array vals 0-9"""

    return np.array(
        [[[8, 0, 2, 6, 3], [2, 8, 2, 8, 4], [3, 9, 1, 5, 4], [5, 9, 2, 7, 7]]]
    )


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
    And 2 colorbars
    """
    ax = ep.plot_bands(image_array_2bands)
    ax = list(ax)
    cb = [a.images[0].colorbar for a in ax if a.images]

    assert len(ax) == 3
    assert len(cb) == 2
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


def test_cbar_param(one_band_3dims):
    """Test that the colorbar param works for a single band arr
    """
    one_band_2dims = one_band_3dims[0]
    ax = ep.plot_bands(one_band_2dims)
    arr = ax.get_images()[0].get_array()
    c_bar = ax.images[0].colorbar

    # Return arr should be scaled by default between 0-255
    assert arr.min() == 0 and arr.max() == 255
    # A cbar should be drawn in this plot
    assert c_bar
    plt.close()


def test_not_scaled_single_band(one_band_3dims):
    """Test if the user turns off scaling and cbar the data vals should remain intact.

    Also if no cbar is specified it should not render.
    """
    one_band_2dims = one_band_3dims[0]

    ax = ep.plot_bands(one_band_2dims, cbar=False, scale=False)
    arr = ax.get_images()[0].get_array()
    c_bar = ax.images[0].colorbar

    # Return arr is unscaled for plotting
    assert (
        arr.min() == one_band_2dims.min() and arr.max() == one_band_2dims.max()
    )
    # A cbar should not be drawn in this plot
    assert not c_bar
    plt.close()


def test_not_scaled_multi_band(image_array_2bands):
    """Test if the user turns off scaling for multi bands the data vals should remain intact.
    """

    im = image_array_2bands
    ax = ep.plot_bands(im, scale=False)

    # Get all arrays to be plotted
    all_arrs = [a.get_images()[0].get_array() for a in ax if a.get_images()]
    all_arrs_flat = np.concatenate(all_arrs, axis=0)

    # Return arr is unscaled for plotting
    assert all_arrs_flat.min() == im.min() and all_arrs_flat.max() == im.max()
    plt.close()


def test_vmin_vmax_multi_band(image_array_2bands):
    """Test vmin and max apply properly in multi band images

    If the data are scaled between -10 and 10 the cbar vals should reflect that.
    """

    one_band_2dims = image_array_2bands
    vmin = -10
    vmax = 10
    ax = ep.plot_bands(one_band_2dims, vmin=vmin, vmax=vmax, scale=False)

    # Get all cbars - the min and max vals for all cbars should be -10 and 10
    cb_max = [a.images[0].colorbar.vmax for a in ax if a.images]
    cb_min = [a.images[0].colorbar.vmin for a in ax if a.images]

    assert all(map(lambda x: x == vmin, cb_min))
    assert all(map(lambda x: x == vmax, cb_max))
    plt.close()


def test_vmin_vmax_single_band(one_band_3dims):
    """Test vmin and max apply properly

    If the data are scaled between -10 and 10 the cbar vals should reflect that.
    """

    one_band_2dims = one_band_3dims[0]
    vmin = 0
    vmax = 10
    ax = ep.plot_bands(one_band_2dims, vmin=vmin, vmax=vmax, scale=False)
    c_bar = ax.images[0].colorbar

    # Cbar should be scaled between the vmin and vmax vals
    assert c_bar.vmin == vmin and c_bar.vmax == vmax
    plt.close()


def test_extent(one_band_3dims):
    """Test that extent param returns a plot with the correct extent."""

    one_band_2dims = one_band_3dims[0]
    # shift extents by 10
    xmin = one_band_2dims.shape[1]
    xmax = one_band_2dims.shape[1] + xmin
    ymin = one_band_2dims.shape[0]
    ymax = one_band_2dims.shape[0] + ymin
    ext = [xmin, xmax, ymin, ymax]

    ax = ep.plot_bands(one_band_2dims, extent=ext)
    pl_extent = list(ax.get_xlim() + ax.get_ylim())

    # Cbar should be scaled between the vmin and vmax vals
    assert pl_extent == ext
    plt.close()


def test_multi_panel_single_band(one_band_3dims):
    """Test that multi panel works with single band arr."""

    title1 = "Title axis one"
    title2 = "Title axis two"
    f, (ax1, ax2) = plt.subplots(2, 1)
    ep.plot_bands(one_band_3dims, title=title1, ax=ax1)
    ep.plot_bands(one_band_3dims, title=title2, ax=ax2)

    # get all axis subplot elements - note this returns subplots and axes
    all_axes = f.axes

    assert len(all_axes) == 4
    assert all_axes[0].get_title() == title1
    assert all_axes[1].get_title() == title2
