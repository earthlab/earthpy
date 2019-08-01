""" Hist tests """

import numpy as np
import pytest
import matplotlib.pyplot as plt
import earthpy.plot as ep


def test_num_plot_titles_mismatch_hist(image_array_2bands):
    """Raise an error if the number of titles != number of bands."""
    with pytest.raises(ValueError, match="number of plot titles"):
        ep.hist(image_array_2bands, title=["One", "too", "many"])
    plt.close()


def test_num_axes_hist(image_array_2bands, basic_image):
    """We expect one AxesSubplot object per band."""
    f_1, ax_1 = ep.hist(basic_image)
    assert len(f_1.axes) == 1
    f_2, ax_2 = ep.hist(image_array_2bands)
    assert len(f_2.axes) == 2
    plt.close(f_1)
    plt.close(f_2)


def test_single_hist_title(basic_image):
    """Test that custom titles work for one band hists."""
    custom_title = "Great hist"
    f, ax = ep.hist(basic_image, title=[custom_title])
    assert ax.get_title() == custom_title
    plt.close(f)


def test_title_string(basic_image):
    """Test that custom titles work for one band hists."""
    custom_title = "Great hist"
    f, ax = ep.hist(basic_image, title=custom_title)
    assert ax.get_title() == custom_title
    plt.close(f)


def test_multiband_hist_title(image_array_2bands):
    """Test that custom titles work for multiband hists."""
    custom_titles = ["Title 1", "Title 2"]
    f, ax = ep.hist(image_array_2bands, title=custom_titles)
    num_plts = image_array_2bands.shape[0]
    assert [f.axes[i].get_title() for i in range(num_plts)] == custom_titles
    plt.close(f)


def test_number_of_hist_bins(basic_image):
    """Test that the number of bins is customizable."""
    n_bins = [1, 10, 100]
    for n in n_bins:
        f, ax = ep.hist(basic_image, bins=n)
        assert n == len(ax.patches)
        plt.close()


def test_hist_bbox(basic_image):
    """Test that the bbox dimensions are customizable."""
    f, ax = ep.hist(basic_image, figsize=(50, 3))
    bbox = str(f.__dict__.get("bbox_inches"))
    assert bbox == "Bbox(x0=0.0, y0=0.0, x1=50.0, y1=3.0)"
    plt.close()


def test_hist_color_single_band(basic_image):
    """Check that the color argument works for single bands."""
    f, ax = ep.hist(basic_image, colors=["red"])
    facecolor = ax.patches[0].__dict__.get("_original_facecolor")
    assert np.array_equal(facecolor, np.array([1.0, 0.0, 0.0, 1.0]))
    plt.close(f)


def test_hist_color_multi_band(image_array_2bands):
    """Test that multiple colors work for multiband images."""
    f, ax = ep.hist(image_array_2bands, colors=["red", "blue"])
    colors = [a.patches[0].__dict__.get("_original_facecolor") for a in ax]
    expected_colors = [
        np.array([1.0, 0.0, 0.0, 1.0]),
        np.array([0.0, 0.0, 1.0, 1.0]),
    ]
    for i in range(2):
        assert np.array_equal(colors[i], expected_colors[i])
    plt.close(f)


def test_hist_number_of_columns(image_array_2bands):
    """Test that the col argument changes the number of columns."""
    number_of_columns = [1, 2]
    for n in number_of_columns:
        f, ax = ep.hist(image_array_2bands, cols=n)
        assert [a.numCols for a in ax] == [n] * 2
        plt.close(f)


# not sure how the tests below are different...
def test_hist_plot_1_band_array(basic_image):
    f, ax = ep.hist(basic_image)
    assert len(f.axes) == 1
    plt.close(f)


def test_hist_plot_1_dim(image_array_2bands):
    array_1_dim = image_array_2bands.ravel()
    f, ax = ep.hist(array_1_dim)
    assert len(f.axes) == 1
    plt.close(f)


# TODO: test that adding an x and y label to the plot works


# TODO add a test for when color is provided in a single band hist as a string

""" Tests for masked arrays """

# TODO: This should count the number of values in the output hist


def test_hist_masked_array(image_array_2bands):
    """ Test that a masked 2 band array plots properly"""
    masked_arr = np.ma.masked_where(
        image_array_2bands == 6, image_array_2bands
    )
    f, ax = ep.hist(masked_arr)
    # TODO:
    # We probably want to count the number of values in the
    # histogram total to ensure the mask is proper
    assert len(f.axes) == 2
    plt.close(f)


def test_hist_1band_masked_array(image_array_single_band):
    """Ensure that a masked single band arr plots & the number of bins is correct"""
    masked_arr = np.ma.masked_where(
        image_array_single_band == 4, image_array_single_band
    )
    nbins = 3
    f, ax = ep.hist(masked_arr, title=["TITLE HERE"], bins=nbins)
    assert len(f.axes) == 1
    assert len(ax.patches) == nbins
    plt.close(f)
