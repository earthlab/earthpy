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
    im_arr = np.random.randint(10, size=(15, 15))
    bins = [-np.inf, 2, 7, np.inf]
    im_arr_bin = np.digitize(im_arr, bins)

    return bins, im_arr_bin


@pytest.fixture
def binned_array():
    im_arr = np.random.uniform(-2, 1, (15, 15))
    bins = [-100, -0.8, -0.2, 0.2, 0.8, np.Inf]
    im_arr_bin = np.digitize(im_arr, bins)
    return bins, im_arr_bin


""" Draw legend tests """


def test_num_titles_classes(binned_array_3bins):
    """Test to ensure the the number of "handles" or classes provided for each
    legend items matches the number of classes being used to build the legend.
    This case should return a ValueError if these items are different"""
    bins, im_arr_bin = binned_array_3bins
    im_arr_bin[im_arr_bin == 2] = 3

    f, ax = plt.subplots(figsize=(5, 5))
    im_ax = ax.imshow(im_arr_bin, cmap="Blues")

    with pytest.raises(ValueError):
        ep.draw_legend(
            im_ax=im_ax, classes=[1, 2], titles=["small", "medium", "large"]
        )

    with pytest.raises(ValueError):
        ep.draw_legend(
            im_ax=im_ax, classes=[1, 2, 3], titles=["small", "large"]
        )
    plt.close(f)


def test_stock_legend_titles(binned_array_3bins):
    """Test that the correct number of generic titles plot when titles
    parameter = None"""

    bins, im_arr_bin = binned_array_3bins

    f, ax = plt.subplots()
    imp2 = ax.imshow(im_arr_bin, cmap="Blues")

    # Default legend title values should be
    def_titles = ["Category {}".format(i) for i in np.unique(im_arr_bin)]

    the_legend = ep.draw_legend(im_ax=imp2)
    # Legend handle titles should equal unique values in ax array
    assert len(the_legend.get_texts()) == len(np.unique(imp2.get_array().data))
    assert def_titles == [text.get_text() for text in the_legend.get_texts()]
    plt.close(f)


def test_custom_legend_titles(binned_array_3bins):
    """Test that the correct number of and text for custom legend titles
    plot when titles parameter = None"""
    bins, im_arr_bin = binned_array_3bins

    f, ax = plt.subplots()
    imp2 = ax.imshow(im_arr_bin, cmap="Blues")
    custom_titles = ["one", "two", "three"]

    the_legend = ep.draw_legend(im_ax=imp2, titles=custom_titles)
    assert len(the_legend.get_texts()) == len(np.unique(imp2.get_array().data))
    assert custom_titles == [
        text.get_text() for text in the_legend.get_texts()
    ]
    plt.close(f)


def test_non_ax_obj():
    """Draw_legend fun should raise ValueError if provided with a
    non mpl axis object"""

    with pytest.raises(AttributeError):
        ep.draw_legend(im_ax=list())


def test_colors(binned_array_3bins):
    """Test that the correct colors appear in the patches of the legend"""

    bins, im_arr_bin = binned_array_3bins

    f, ax = plt.subplots()
    im = ax.imshow(im_arr_bin, cmap="Blues")
    the_legend = ep.draw_legend(im_ax=im)
    legend_cols = [i.get_facecolor() for i in the_legend.get_patches()]
    # Get the array and cmap from axis object
    cmap_name = im.axes.get_images()[0].get_cmap().name
    unique_vals = np.unique(im.get_array().data)
    image_colors = ep.make_col_list(unique_vals, cmap=cmap_name)

    assert image_colors == legend_cols
    plt.close(f)


def test_neg_vals(binned_array):
    """Test that the things plot when positive and negative vales
    are provided"""
    bins, arr_class = binned_array

    f, ax = plt.subplots()
    im_ax = ax.imshow(arr_class)
    leg_neg = ep.draw_legend(im_ax)
    legend_cols = [i.get_facecolor() for i in leg_neg.get_patches()]
    assert len(legend_cols) == len(bins) - 1
    plt.close(f)


def test_listed_cmap(binned_array):
    """Test that the the legend generates properly when provided with a Listed
     colormap"""

    bins, arr_class = binned_array

    # TODO make the list of colors a fixture for reuse
    cmap_list = ListedColormap(
        ["white", "tan", "purple", "springgreen", "darkgreen"]
    )
    f, ax = plt.subplots()
    im_plt = ax.imshow(arr_class, cmap=cmap_list)
    leg = ep.draw_legend(im_plt)
    legend_cols = [i.get_facecolor() for i in leg.get_patches()]
    assert len(legend_cols) == len(bins) - 1
    plt.close(f)


def test_noncont_listed_cmap(binned_array, listed_cmap):
    """Test that an arr with 3 classes (missing the 1, and 5) which
     would need to be normalized, only creates a legend with x handles
     by default"""

    cmap, norm = listed_cmap
    bins, arr_class = binned_array

    arr_class[arr_class == 1] = 2
    arr_class[arr_class == 5] = 4

    f, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(arr_class, cmap=cmap, norm=norm)
    leg = ep.draw_legend(im)

    legend_cols = [i.get_facecolor() for i in leg.get_patches()]
    assert len(legend_cols) == len(np.unique(arr_class))
    plt.close(f)


def test_noncont_listed_cmap_3_classes(binned_array, listed_cmap):
    """Test legend for a non continuous listed cmap where
    the user wants all classes to be drawn in the legend. IE the classified
    image has classes 2,3,4 and the user wants classes 1-5 to appear """

    cmap, norm = listed_cmap
    bins, arr_class = binned_array

    f, ax = plt.subplots(figsize=(5, 5))
    im = ax.imshow(arr_class, cmap=cmap, norm=norm)
    leg = ep.draw_legend(im, classes=[1, 2, 3, 4, 5])

    legend_cols = [i.get_facecolor() for i in leg.get_patches()]
    assert len(legend_cols) == len([1, 2, 3, 4, 5])
    plt.close(f)


def test_masked_vals():
    """Test to ensure that a masked array plots properly"""
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
    """Test to ensure that a plot with subplots still has a legend."""

    bins, arr_class = binned_array

    f, (ax1, ax2) = plt.subplots(2, 1)
    im_ax = ax1.imshow(arr_class)
    ep.draw_legend(im_ax)

    im_ax2 = ax2.imshow(arr_class)
    ep.draw_legend(im_ax2)
    plt.close(f)
