"""Tests for the plot module"""

import numpy as np
import pytest
import matplotlib as mpl
import matplotlib.pyplot as plt

plt.show = lambda: None
from matplotlib.colors import ListedColormap
import earthpy.plot as ep


@pytest.fixture
def listed_cmap():
    cmap = ListedColormap(
        ["white", "tan", "purple", "springgreen", "darkgreen"]
    )
    norm = mpl.colors.Normalize(vmin=1, vmax=5)
    return cmap, norm


@pytest.fixture
def binned_array_3bins():
    im_arr = np.random.randint(10, size=(6, 6))
    bins = [-np.inf, 2, 7, np.inf]
    im_arr_bin = np.digitize(im_arr, bins)

    return bins, im_arr_bin


@pytest.fixture
def binned_array():
    im_arr = np.random.uniform(-2, 1, (6, 6))
    bins = [-100, -0.8, -0.2, 0.2, 0.8, np.Inf]
    im_arr_bin = np.digitize(im_arr, bins)
    return bins, im_arr_bin


@pytest.fixture
def arr_plot_blues(binned_array_3bins):
    """Returns an imshow object using the Blues cmap and the arr used to plot"""
    bins, im_arr_bin = binned_array_3bins

    f, ax = plt.subplots()
    return ax.imshow(im_arr_bin), im_arr_bin


@pytest.fixture
def arr_plot_list_cmap(binned_array, listed_cmap):
    """Returns a plot rendered using a listed cmap """

    cmap, norm = listed_cmap
    bins, arr_class = binned_array

    f, ax = plt.subplots()
    return ax.imshow(arr_class, cmap=cmap), arr_class


@pytest.fixture
def vals_missing_plot_list_cmap(binned_array, listed_cmap):
    """Returns a normalized imshow plot using a 3 value array w vals 2,3,4"""

    cmap, norm = listed_cmap
    bins, arr = binned_array

    arr[arr == 1] = 2
    arr[arr == 5] = 4

    f, ax = plt.subplots(figsize=(5, 5))
    return ax.imshow(arr, cmap=cmap, norm=norm), arr


@pytest.fixture
def vals_missing_plot_cont_cmap(binned_array):
    """Returns a non normalized imshow plot using 3 consecutive value array"""

    bins, arr = binned_array

    arr[arr == 1] = 2
    arr[arr == 5] = 4

    f, ax = plt.subplots(figsize=(5, 5))
    return ax.imshow(arr), arr


""" Draw legend tests """


def test_num_titles_classes(arr_plot_blues):
    """Test that the number of classes equals the number of legend titles"""

    im_ax, _ = arr_plot_blues

    with pytest.raises(
        ValueError,
        match="The number of classes should equal the number of titles",
    ):
        ep.draw_legend(
            im_ax=im_ax, classes=[1, 2], titles=["small", "medium", "large"]
        )

    with pytest.raises(
        ValueError,
        match="The number of classes should equal the number of titles",
    ):
        ep.draw_legend(
            im_ax=im_ax, classes=[1, 2, 3], titles=["small", "large"]
        )
    plt.close()


def test_stock_legend_titles(arr_plot_blues):
    """Test that the correct number of default titles plot"""

    im_ax, im_arr_bin = arr_plot_blues

    # Default legend title values
    def_titles = ["Category {}".format(i) for i in np.unique(im_arr_bin)]

    the_legend = ep.draw_legend(im_ax=im_ax)
    # Legend handle titles should equal unique values in ax array
    assert len(the_legend.get_texts()) == len(
        np.unique(im_ax.get_array().data)
    )
    assert def_titles == [text.get_text() for text in the_legend.get_texts()]
    plt.close()


def test_custom_legend_titles(arr_plot_blues):
    """Test that the correct number of custom legend titles plot"""

    im_ax, _ = arr_plot_blues

    custom_titles = ["one", "two", "three"]
    the_legend = ep.draw_legend(im_ax=im_ax, titles=custom_titles)

    assert len(the_legend.get_texts()) == len(
        np.unique(im_ax.get_array().data)
    )
    assert custom_titles == [
        text.get_text() for text in the_legend.get_texts()
    ]
    plt.close()


def test_non_ax_obj():
    """Draw_legend fun should raise AttributeError if provided with a
    non mpl axis object"""

    with pytest.raises(
        AttributeError,
        match="The legend function requires a matplotlib axis object",
    ):
        ep.draw_legend(im_ax=list())


def test_colors(arr_plot_blues):
    """Test that the correct colors appear in the patches of the legend"""

    im_ax, _ = arr_plot_blues
    the_legend = ep.draw_legend(im_ax=im_ax)

    legend_cols = [i.get_facecolor() for i in the_legend.get_patches()]
    # Get the array and cmap from axis object
    cmap_name = im_ax.axes.get_images()[0].get_cmap().name
    unique_vals = np.unique(im_ax.get_array().data)
    image_colors = ep.make_col_list(unique_vals, cmap=cmap_name)

    assert image_colors == legend_cols
    plt.close()


def test_neg_vals():
    """Test that the legend plots when positive and negative values are provided"""

    arr = np.array([[-1, 0, 1], [1, 0, -1]])
    f, ax = plt.subplots()
    im_ax = ax.imshow(arr)

    leg_neg = ep.draw_legend(im_ax)
    legend_cols = [i.get_facecolor() for i in leg_neg.get_patches()]
    assert len(legend_cols) == len(np.unique(arr))
    plt.close(f)


def test_listed_cmap(arr_plot_list_cmap):
    """Test that the the legend generates properly when provided with a ListedColormap"""

    im_ax, arr = arr_plot_list_cmap

    leg = ep.draw_legend(im_ax)
    legend_cols = [i.get_facecolor() for i in leg.get_patches()]
    assert len(legend_cols) == len(np.unique(arr))
    plt.close()


def test_classes_provided_as_array(arr_plot_list_cmap):
    """Test that draw_legend works when classes are provided as an arr (not a list)."""

    im_ax, arr = arr_plot_list_cmap
    n_classes = 5

    leg = ep.draw_legend(im_ax, classes=np.arange(n_classes))

    legend_cols = [i.get_facecolor() for i in leg.get_patches()]
    assert len(legend_cols) == n_classes
    plt.close()


def test_noncont_listed_cmap(vals_missing_plot_list_cmap):
    """An arr with 3 vals (missing the 1, and 5) which requires normalization
     produces creates a legend with 3 handles."""

    im_ax, arr = vals_missing_plot_list_cmap

    leg = ep.draw_legend(im_ax)

    legend_cols = [i.get_facecolor() for i in leg.get_patches()]
    assert len(legend_cols) == len(np.unique(arr))
    plt.close()


def test_listed_cmap_3_classes(vals_missing_plot_list_cmap):
    """Test legend for a listed cmap where
    the user wants all classes to be drawn in the legend. IE the classified
    image has classes 2,3,4 and the user wants classes 1-5 to appear """

    im_ax, arr = vals_missing_plot_list_cmap

    class_list = list(range(5))
    leg = ep.draw_legend(im_ax, classes=class_list)
    legend_cols = [i.get_facecolor() for i in leg.get_patches()]

    assert len(legend_cols) == len(class_list)
    plt.close()


def test_cont_cmap_3_classes(vals_missing_plot_cont_cmap):
    """Test legend for a listed cmap where
    the user wants all classes to be drawn in the legend. IE the classified
    image has classes 2,3,4 and the user wants classes 1-5 to appear """

    im_ax, arr = vals_missing_plot_cont_cmap

    class_list = list(range(5))
    leg = ep.draw_legend(im_ax, classes=class_list)
    legend_cols = [i.get_facecolor() for i in leg.get_patches()]

    assert len(legend_cols) == len(class_list)
    plt.close()


def test_listedcmap_ncol_equals_nclasses(vals_missing_plot_list_cmap):
    """If a 5 color listed cmap is provided and 6 classes are specified, return value error"""

    n_classes = 5
    im_ax, arr = vals_missing_plot_list_cmap

    with pytest.raises(
        ValueError, match="There are more classes than colors in your cmap"
    ):
        ep.draw_legend(im_ax, classes=np.arange(0, n_classes + 1))
    plt.close()


def test_masked_vals():
    """Legend for masked array plots properly"""

    im_arr = np.random.uniform(-2, 1, (15, 15))
    bins = [-0.8, -0.2, 0.2, 0.8, np.Inf]
    im_arr_bin = np.digitize(im_arr, bins)
    arr_bin_ma = np.ma.masked_equal(im_arr_bin, 0)
    unmasked_vals = [
        val for val in np.unique(arr_bin_ma) if val is not np.ma.core.masked
    ]

    f, ax = plt.subplots()
    im_ax = ax.imshow(arr_bin_ma)
    leg = ep.draw_legend(im_ax)
    legend_cols = [i.get_facecolor() for i in leg.get_patches()]
    assert len(legend_cols) == len(unmasked_vals)
    plt.close(f)


def test_subplots(binned_array):
    """Plot with subplots still has a legend."""

    bins, arr_class = binned_array

    f, (ax1, ax2) = plt.subplots(2, 1)
    im_ax = ax1.imshow(arr_class)
    ep.draw_legend(im_ax)

    im_ax2 = ax2.imshow(arr_class)
    ep.draw_legend(im_ax2)
    plt.close(f)
