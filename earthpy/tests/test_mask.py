""" Tests for the mask module. """

import numpy as np
from earthpy.mask import make_apply_mask
import pytest


im = np.random.randint(10, size=(4, 5))
im_mask = np.random.randint(5, size=(4, 5))


def test_arr_provided():
    """ Test for arrays provided as image and/or mask input. """

    an_arr_tup = (2, 3)
    with pytest.raises(AttributeError):
        make_apply_mask(an_arr_tup, mask_arr=im_mask, vals=[0, 4])
    with pytest.raises(AttributeError):
        make_apply_mask(im, mask_arr=an_arr_tup, vals=[0, 4])


def test_masked_arr_returned():
    """ Test for return of masked_array type. """

    masked = make_apply_mask(im, im_mask, [0, 4])
    assert np.ma.is_masked(masked)


def test_val_list_provided():
    """ Provide a singular value to the vals keyword to raise AttributeError"""

    with pytest.raises(AttributeError):
        make_apply_mask(im, mask_arr=im_mask, vals=0)


def test_mask_provided_with_no_ones():
    """ Test that a mask is provided to apply mask that doesn't have 1's in it.
        should return - there's nothing to mask here!"""

    im_mask_no_ones = im_mask * 0
    with pytest.raises(ValueError):
        make_apply_mask(im, im_mask_no_ones, [3, 4])


def test_im_with_mask_as_masked_array():
    """Test that a user provides an array with a mask already.
       Does it merge properly?
       and return a masked array with the values expected?"""

    im_with_mask = np.ma.masked_where(im_mask < 2, im)
    im_result = make_apply_mask(im_with_mask, mask_arr=im_mask, vals=[0, 4])
    assert np.ma.is_masked(im_result)
