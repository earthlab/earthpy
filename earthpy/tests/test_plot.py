"""Tests for the plot module"""

import numpy as np
import pytest
import matplotlib as mpl

mpl.use("TkAgg")
import matplotlib.pyplot as plt
import earthpy.plot as ep

plt.show = lambda: None


""" plot_bands tests """


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
    f, ax = ep.plot_bands(arr=single_band, title="my title")
    plot_title = ax.get_title()
    assert "my title" in plot_title
    plt.close()


def test_num_axes(image_array_2bands):
    """Test the number of axes.

    If provided with a 2 band array, plot_bands should return 3 axes.
    """
    f, ax = ep.plot_bands(image_array_2bands)
    assert len(f.axes) == 3
    plt.close(f)


def test_two_plot_title(image_array_2bands):
    """Test that the default title is provided for a 2 band array plot."""

    f, ax = ep.plot_bands(image_array_2bands)
    ax = f.axes
    num_plts = image_array_2bands.shape[0]
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ["Band 1", "Band 2"]
    plt.close(f)


def test_custom_plot_title(image_array_2bands):
    """Test that the custom title is applied for a 2 band array plot."""
    f, ax = ep.plot_bands(image_array_2bands, title=["Red Band", "Green Band"])
    ax = f.axes
    num_plts = image_array_2bands.shape[0]
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ["Red Band", "Green Band"]
    plt.close(f)


def test_single_band_3dims(one_band_3dims):
    """Test single band plot with three dimensions.

    If you provide a single band array with 3 dimensions (shape[0]==1
    test that it still plots and only returns a single axis.
    """
    f, ax = ep.plot_bands(one_band_3dims)
    arr = f.axes[0].get_images()[0].get_array()
    assert arr.ndim == 2
    assert len(f.axes[0].get_images()) == 1
    plt.close(f)


def test_single_band_2dims(one_band_3dims):
    """Test single band plot with two dimensions

    If you provide a single band array with 3 dimensions (shape[0] == 1)
    test that it still plots and only returns a single axis.
    """
    single_band_2dims = one_band_3dims[0]
    f, ax = ep.plot_bands(single_band_2dims)
    # Get array from mpl figure
    arr = f.axes[0].get_images()[0].get_array()
    assert arr.ndim == 2
    assert len(f.axes[0].get_images()) == 1
    plt.close(f)


""" Colorbar Tests """


def test_colorbar_height(basic_image):
    """Test that the colorbar ax height matches the image axis height."""
    f, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(basic_image, cmap="RdYlGn")
    cb = ep.colorbar(im)
    assert cb.ax.get_position().height == im.axes.get_position().height
    plt.close(f)


def test_colorbar_raises_value_error():
    """Test that a non matbplotlib axis object raises an value error."""
    with pytest.raises(AttributeError, match="requires a matplotlib"):
        ep.colorbar(list())
    plt.close()


""" Hist tests """


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
