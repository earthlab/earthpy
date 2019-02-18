""" Tests for the mask module. """

import numpy as np
from earthpy.mask import mask_pixels
import pytest


@pytest.fixture
def im():
    """Create image arr for masking"""
    arr = np.array([[0, 1, 2], [3, 4, 5]])
    return arr


@pytest.fixture
def im_mask():
    """Create image mask"""
    arr = np.array([[0, 0, 1], [1, 2, 2]])
    return arr


def test_arr_provided(im, im_mask):
    """ Test that inputs are numpy arrays. """

    with pytest.raises(
        AttributeError, match="Input arr should be a numpy array."
    ):
        mask_pixels((2, 3), mask_arr=im_mask, vals=[0, 4])
    with pytest.raises(
        AttributeError, match="Input arr should be a numpy array."
    ):
        mask_pixels(im, mask_arr=(2, 3), vals=[0, 4])


def test_masked_arr_returned(im, im_mask):
    """ Test for return of masked_array type. """

    masked = mask_pixels(im, im_mask, vals=[0])
    assert np.ma.is_masked(masked)


def test_vals_as_list(im, im_mask):
    """ Test for return of masked_array type. """

    with pytest.raises(
        AttributeError, match="Values should be provided as a list"
    ):
        mask_pixels(im, mask_arr=im_mask, vals=(0, 1, 2, 3))


def test_mask_contains_ones(im, im_mask):
    """A boolean mask without the value 1 fails gracefully."""

    zero_array = im_mask * 0
    with pytest.raises(ValueError, match="Mask requires values of 1"):
        mask_pixels(im, mask_arr=zero_array)


def test_mask_vals_in_arr(im, im_mask):
    """If vals are not found in mask_arr, fail gracefully"""
    values_not_in_mask = [99, -99]
    with pytest.raises(
        ValueError, match="The values provided for the mask do not occur"
    ):
        mask_pixels(im, im_mask, values_not_in_mask)


def test_masked_arr_provided(im, im_mask):
    """If a masked array is provided, mask returns masked array."""

    masked_input = np.ma.masked_where(im_mask == 0, im)
    out = mask_pixels(masked_input, im_mask, vals=[1])
    elements_in = masked_input.count()
    elements_out = out.count()

    assert np.ma.is_masked(masked_input) and np.ma.is_masked(out)
    assert elements_in == 4
    assert elements_out == 2


def test_boolean_mask(im, im_mask):
    """If boolean mask provided without vals, a masked arr is returned."""

    boolean_mask = im_mask > 1
    assert np.ma.is_masked(mask_pixels(im, boolean_mask))


def test_user_mask_arr(im, im_mask):
    """Test that vals are provided for non boolean mask."""

    with pytest.raises(
        ValueError,
        match="""You have provided a mask_array with no values to mask""",
    ):
        mask_pixels(im, im_mask)
