import numpy as np
import numpy.ma as ma

# A dictionary for values to use in masking the QA band
pixel_flags = {
    "pixel_qa": {
        "L47": {
            "Fill": [1],
            "Clear": [66, 130],
            "Water": [68, 132],
            "Cloud Shadow": [72, 136],
            "Snow": [80, 112, 144, 176],
            "Cloud": [96, 112, 160, 176, 224],
            "Low Cloud Confidence": [66, 68, 72, 80, 96, 112],
            "Medium Cloud Confidence": [130, 132, 136, 144, 160, 176],
            "High Cloud Confidence": [224],
        },
        "L8": {
            "Fill": [1],
            "Clear": [322, 386, 834, 898, 1346],
            "Water": [324, 388, 836, 900, 1348],
            "Cloud Shadow": [328, 392, 840, 904, 1350],
            "Snow": [336, 368, 400, 432, 848, 880, 912, 944, 1352],
            "Cloud": [352, 368, 416, 432, 480, 864, 880, 928, 944, 992],
            "Low Cloud Confidence": [
                322,
                324,
                328,
                336,
                352,
                368,
                834,
                836,
                840,
                848,
                864,
                880,
            ],
            "Medium Cloud Confidence": [
                386,
                388,
                392,
                400,
                416,
                432,
                900,
                904,
                928,
                944,
            ],
            "High Cloud Confidence": [480, 992],
            "Low Cirrus Confidence": [
                322,
                324,
                328,
                336,
                352,
                368,
                386,
                388,
                392,
                400,
                416,
                432,
                480,
            ],
            "Medium Cirrus Confidence": [],
            "High Cirrus Confidence": [
                834,
                836,
                840,
                848,
                864,
                880,
                898,
                900,
                904,
                912,
                928,
                944,
                992,
            ],
            "Terrain Occlusion": [1346, 1348, 1350, 1352],
        },
    }
}


def make_cloud_mask(mask_arr, vals):
    """Take an input single band mask layer such as a pixel_qa
    layer for MODIS or Landsat and apply a mask given a range of vals to mask

    Parameters
    -----------
    mask_arr : numpy array
        An array... to open the pixel_qa or mask raster of interest

    vals : list of numbers (int or float)
        A list of values that represent no data in the provided raster
        layer (mask_arr)

    Returns
    -----------
    arr : numpy array
        A numpy array with values that should be masked set to 1 for
        True (Boolean)
    """

    # Make sure vals is a list
    try:
        vals.sort()
    except AttributeError:
        raise AttributeError("Values should be provided as a list")

    try:
        mask_arr.ndim
        temp_mask = np.isin(mask_arr, vals)
    except AttributeError:
        raise AttributeError("Input arr should be a numpy array")

    # Mask the values
    mask_arr[temp_mask] = 1
    mask_arr[~temp_mask] = 0

    return mask_arr


def apply_cloud_mask(arr, the_mask):
    """Take an input raster numpy array in band order (bands, rows,cols)
     and apply a mask to the array

    Parameters
    -----------
    arr : numpy array
        An array in rasterio (band, row, col) order

    the_mask : single dimension (band) numpy array
        A numpy array containing a qa values for raster pixels that should be
        masked - ex landsat pixel_qa layer.

    Returns
    -----------
    masked arr : a masked numpy array
        A masked numpy array with the mask having the same dimensions as arr
    """

    # Test if the_mask is numpy array w values == 1 for masked
    if not np.any(the_mask == 1):
        raise ValueError("Mask requires values of 1 (True) to be applied.")

    try:
        # Create a mask for all bands in the landsat scene
        cl_mask = np.broadcast_to(the_mask == 1, arr.shape)
    except AttributeError:
        raise AttributeError("Input arr should be a numpy array")

    # If the user provides a masked array, combine masks
    if isinstance(arr, np.ma.MaskedArray):
        cl_mask = np.logical_or(arr.mask, cl_mask)

    # Return combined mask
    return ma.masked_array(arr, mask=cl_mask)


def make_apply_mask(arr, mask_arr, vals):
    """Take an input array to be masked, single band mask layer such as a
    pixel_qa layer for MODIS or Landsat and apply a mask given a range of
    vals to mask.

    Parameters
    -----------
    arr : numpy array
        An array in rasterio (band, row, col) order

    mask_arr : numpy array
        An array... to open the pixel_qa or mask raster of interest

    vals : list of numbers (int or float)
        A list of values that represent no data in the provided raster
        layer (mask_arr)

    Returns
    -----------
    arr : numpy array
        A numpy array with values that should be masked set to 1 for
        True (Boolean)

    >>> import numpy as np
    >>> from earthpy.mask import make_apply_mask
    >>> im = np.arange(9).reshape((3, 3))
    >>> im
    array([[0, 1, 2],
           [3, 4, 5],
           [6, 7, 8]])
    >>> im_mask = np.array([1, 1, 1, 0, 0, 0, 1, 1, 1]).reshape(3, 3)
    >>> im_mask
    array([[1, 1, 1],
           [0, 0, 0],
           [1, 1, 1]])
    >>> make_apply_mask(im, mask_arr=im_mask, vals=[1])
    masked_array(
      data=[[--, --, --],
            [3, 4, 5],
            [--, --, --]],
      mask=[[ True,  True,  True],
            [False, False, False],
            [ True,  True,  True]],
      fill_value=999999)
    """
    cl_mask = make_cloud_mask(mask_arr, vals)
    return apply_cloud_mask(arr, cl_mask)
