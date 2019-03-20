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


def _create_mask(mask_arr, vals):
    """Mask specific values in a 1-dimensional numpy array.

    Parameters
    -----------
    mask_arr : numpy array
        An array of the pixel_qa or mask raster of interest.

    vals : list of numbers (int or float)
        A list of values from mask_arr (the qa layer) used to create
        the mask for the final return array.

    Returns
    -----------
    arr : numpy array
        A numpy array populated with 1's where the mask is applied (a Boolean True)
        and a 0 where no masking will be done.
    """

    try:
        vals.sort()
    except AttributeError:
        raise AttributeError("Values should be provided as a list")

    # For some reason if you don't copy this here, it magically changes the input
    # qa layer to a boolean in the main environment.
    new_mask_arr = mask_arr.copy()
    unique_vals = np.unique(new_mask_arr).tolist()

    if any(num in vals for num in unique_vals):
        temp_mask = np.isin(new_mask_arr, vals)
        new_mask_arr[temp_mask] = 1
        new_mask_arr[~temp_mask] = 0

        return new_mask_arr

    else:
        raise ValueError(
            """The values provided for the mask do not occur
            in your mask array."""
        )


def _apply_mask(arr, input_mask):
    """Apply a mask to each band in the provided array.

    Parameters
    -----------
    arr : numpy array
        The original numpy array in rasterio (band, row, col) order
        that needs a mask applied.

    input_mask : numpy array
        A numpy array containing O's and 1's where the 1's indicate where the
        mask is applied.

    Returns
    -----------
    numpy array
        The original numpy array with the mask applied to cover up issue pixels.
    """

    # Test if input_mask is numpy array w values == 1 for masked
    if not np.any(input_mask == 1):
        raise ValueError("Mask requires values of 1 (True) to be applied.")

    cover_mask = np.broadcast_to(input_mask == 1, arr.shape)

    # If the user provides a masked array, combine masks
    if isinstance(arr, np.ma.MaskedArray):
        cover_mask = np.logical_or(arr.mask, cover_mask)

    # Return combined mask
    return ma.masked_array(arr, mask=cover_mask)


def mask_pixels(arr, mask_arr, vals=None):
    """Apply a mask to an input array.

    Masks values in an n-dimensional input array (arr) based on input 1-dimensional
    array (mask_arr). If mask_arr is provided in a boolean format, it is used as a mask.
    If mask_arr is provided as a non-boolean format and values to mask (vals) are provided,
    a Boolean masked array is created from the mask_arr and the indicated vals to mask, and
    then this new 1-dimensional masked array is used to mask the input arr.

    This function is useful when masking cloud and other unwanted pixels.

    Parameters
    -----------
    arr : numpy array
        The array to mask in rasterio (band, row, col) order.
    mask_arr : numpy array
        An array of either the pixel_qa or mask of interest.
    vals : list of numbers either int or float (optional)
        A list of values from the pixel qa layer that will be used to create
        the mask for the final return array. If vals are not passed in,
        it is assumed the mask_arr given is the mask of interest.

    Returns
    -------
    arr : numpy array
        A numpy array populated with 1's where the mask is applied (a Boolean True)
        and the original numpy array's value where no masking was done.

    Example
    -------
    >>> import numpy as np
    >>> from earthpy.mask import mask_pixels
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
    >>> mask_pixels(im, mask_arr=im_mask, vals=[1])
    masked_array(
      data=[[--, --, --],
            [3, 4, 5],
            [--, --, --]],
      mask=[[ True,  True,  True],
            [False, False, False],
            [ True,  True,  True]],
      fill_value=999999)
    """

    try:
        arr.ndim
    except AttributeError:
        raise AttributeError("Input arr should be a numpy array.")

    try:
        mask_arr.ndim
    except AttributeError:
        raise AttributeError("Input arr should be a numpy array.")

    if vals:
        cover_mask = _create_mask(mask_arr, vals)
    else:
        # Check to make sure the mask_arr is a boolean
        if np.array_equal(mask_arr, mask_arr.astype(bool)):
            cover_mask = mask_arr.astype(bool)
        else:
            raise ValueError(
                """You have provided a mask_array with no values to mask. Please
                either provide a mask_array of type bool, or provide values
                to be used to create a mask."""
            )
    return _apply_mask(arr, cover_mask)
