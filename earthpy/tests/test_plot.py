"""Tests for the plot module"""

import numpy as np
import pytest
import earthpy.spatial as es
import matplotlib.pyplot as plt

plt.show = lambda: None


@pytest.fixture
def image_array_2bands():
    return np.random.randint(10, size=(2, 4, 5))


@pytest.fixture
def one_band_3dims():
    return np.random.randint(10, size=(1, 4, 5))


@pytest.fixture
def one_band_2dims():
    return np.random.randint(10, size=(5, 5))


""" General functions for matplotlib elements """


def test_arr_parameter():
    """Raise an AttributeError if an array is not provided."""
    with pytest.raises(AttributeError):
        es.plot_bands(arr=(1, 2))


def test_num_titles(image_array_2bands):
    """If a user provides two titles for a single band array, the function
    should raise an error OR if the title list is a different length than
    the array it should also raise an errors"""

    single_band = image_array_2bands[0]

    with pytest.raises(ValueError):
        es.plot_bands(arr=single_band, title=["Title1", "Title2"])
    with pytest.raises(ValueError):
        es.plot_bands(
            arr=image_array_2bands, title=["Title1", "Title2", "Title3"]
        )


def test_num_axes(image_array_2bands):
    """If provided with a 2 band array, plot_bands should return 3 axes by
    default"""

    f, ax = es.plot_bands(image_array_2bands)
    assert len(f.axes) == 3
    plt.close(f)


def test_two_plot_title(image_array_2bands):
    """Test that the default title is provided for a 2 band array plot"""

    f, ax = es.plot_bands(image_array_2bands)
    ax = f.axes
    num_plts = image_array_2bands.shape[0]
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ["Band 1", "Band 2"]
    plt.close(f)


def test_custom_plot_title(image_array_2bands):
    """Test that the custom title is applied for a 2 band array plot"""

    f, ax = es.plot_bands(image_array_2bands, title=["Red Band", "Green Band"])
    ax = f.axes
    num_plts = image_array_2bands.shape[0]
    all_titles = [ax[i].get_title() for i in range(num_plts)]
    assert all_titles == ["Red Band", "Green Band"]
    plt.close(f)


def test_single_band_3dims(one_band_3dims):
    """If you provide a single band array with 3 dimensions (shape[0]==1
    test that it still plots and only returns a single axis"""

    f, ax = es.plot_bands(one_band_3dims)
    arr = f.axes[0].get_images()[0].get_array()
    assert arr.ndim == 2
    assert len(f.axes[0].get_images()) == 1
    plt.close(f)


def test_single_band_2dims(one_band_3dims):
    """If you provide a single band array with 3 dimensions (shape[0]==1
    test that it still plots and only returns a single axis"""

    single_band_2dims = one_band_3dims[0]
    f, ax = es.plot_bands(single_band_2dims)
    # Get array from mpl figure
    arr = f.axes[0].get_images()[0].get_array()
    assert arr.ndim == 2
    assert len(f.axes[0].get_images()) == 1
    plt.close(f)


""" Colorbar Tests """


def test_colorbar_height(one_band_2dims):
    """Test that the colorbar ax height matches the image axis height"""

    f, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(one_band_2dims, cmap="RdYlGn")
    cb = es.colorbar(im)

    assert cb.ax.get_position().height == im.axes.get_position().height
    plt.close(f)


def test_colorbar_raises_value_error():
    """Test that a non matbplotlib axis object raises an value error"""

    with pytest.raises(AttributeError, match="requires a matplotlib"):
        es.colorbar(list())
