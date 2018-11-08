import numpy as np
import numpy.ma as ma


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

    # construct the mask
    temp_mask = np.isin(mask_arr, vals)
    
    # mask the values
    mask_arr[temp_mask] = 1
    mask_arr[~temp_mask] = 0
    
    return(mask_arr)


def apply_cloud_mask(arr, the_mask):
    # Create a mask for all bands in the landsat scene
    cl_mask = np.broadcast_to(the_mask == 1,
                              arr.shape)

    # If the user provides a masked array, combine masks
    if isinstance(arr, np.ma.MaskedArray):
        cl_mask = np.logical_or(arr.mask, cl_mask)

    # Return combined mask
    return (ma.masked_array(arr, mask=cl_mask))


def make_apply_mask(arr, mask_arr, vals):
    cl_mask = make_cloud_mask(mask_arr, vals)
    return (apply_cloud_mask(arr, cl_mask))
