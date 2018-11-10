import numpy as np
from earthpy.mask import make_apply_mask

import pytest
import rasterio as rio


"""Functions for the mask module"""


im = np.random.randint(10, size=(4, 5))
im_mask = np.random.randint(5, size=(4, 5))

#def make_apply_mask(arr, mask_arr, vals):

def test_arr_provided():
    an_arr_tup = (2,3)
    with pytest.raises(AttributeError):
        make_apply_mask(an_arr_tup,
                    mask_arr=im_mask,
                    vals=[0,4])
    with pytest.raises(AttributeError):
        make_apply_mask(im,
                        mask_arr=an_arr_tup,
                        vals=[0, 4])


def test_masked_arr_returned():
    masked = make_apply_mask(im, im_mask, [0,4])
    assert np.ma.is_masked(masked)

# def test_val_list_provided:
#     """Tuple works just fine. what about some other object type? like? """
#
#     with pytest.raises(AttributeError):
#         make_apply_mask(im,
#                     mask_arr=im_mask,
#                     vals=[0,4])