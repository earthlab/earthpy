""" Tests for the mask module. """

import numpy as np
from earthpy.mask import mask_pixels
import pytest


@pytest.fixture
def im():
    """Create image arr for masking"""
    arr = np.array(
        [[0, 1, 8, 7, 5], [3, 8, 8, 7, 0], [3, 0, 0, 9, 9], [5, 5, 7, 4, 5]]
    )
    return arr


@pytest.fixture
def im_mask():
    """Create image mask"""
    arr = np.array(
        [[0, 1, 1, 0, 2], [1, 4, 4, 0, 1], [0, 0, 3, 4, 3], [4, 1, 2, 0, 3]]
    )
    return arr


def test_arr_provided(im, im_mask):
    """ Test that inputs are numpy arrays. """

    an_arr_tup = (2, 3)
    with pytest.raises(
        AttributeError, match="Input arr should be a numpy array."
    ):
        mask_pixels(an_arr_tup, mask_arr=im_mask, vals=[0, 4])
    with pytest.raises(
        AttributeError, match="Input arr should be a numpy array."
    ):
        mask_pixels(im, mask_arr=an_arr_tup, vals=[0, 4])


def test_masked_arr_returned(im, im_mask):
    """ Test for return of masked_array type. """

    masked = mask_pixels(im, im_mask, vals=[0, 4])
    assert np.ma.is_masked(masked)


def test_vals_as_list(im, im_mask):
    """ Test for return of masked_array type. """

    with pytest.raises(
        AttributeError, match="Values should be provided as a list"
    ):
        mask_pixels(im, mask_arr=im_mask, vals=(4))


def test_mask_contains_ones(im, im_mask):
    """A boolean mask without the value 1 fails gracefully."""

    im_mask[im_mask > 0] = 0
    with pytest.raises(ValueError, match="Mask requires values of 1"):
        mask_pixels(im, mask_arr=im_mask)


def test_mask_vals_in_arr(im, im_mask):
    """If vals are not found in mask_arr, fail gracefully"""

    im_mask_no_ones = im_mask * 0
    with pytest.raises(
        ValueError,
        match="""List of values provided for the mask does 
                             not exist in your mask array.""",
    ):
        mask_pixels(im, im_mask_no_ones, [3, 4])


def test_masked_arr_provided(im, im_mask):
    """If a boolean arr is provided, mask returns masked arr"""

    masked_im = np.ma.masked_where(im_mask < 2, im)
    assert np.ma.is_masked(mask_pixels(masked_im, im_mask, vals=[4]))


def test_boolean_mask(im, im_mask):
    """If boolean mask provided without vals, a masked arr is returned."""

    im_mask[im_mask > 1] = 1

    assert np.ma.is_masked(mask_pixels(im, im_mask))


def test_user_mask_arr(im, im_mask):
    """Test that vals are provided for non boolean mask."""

    with pytest.raises(
        ValueError,
        match="""You have provided a mask_array with no values to mask""",
    ):
        mask_pixels(im, im_mask)
