from earthpy import spatial
from osgeo import gdal
from osgeo import osr
import rasterio as rio
import numpy as np

# a helper function to generate a 3D array of data
def createArray(arr_shape):
    """ createArray(arr_shape) creates a numpy ndarray with the shape defined by the tuple arr_shape
        arr_shape should be:
        (rows, cols, [channels])
        the values for each channel will be the 1-based number of that channel.
    """
    
    dummy_arr = np.ones(arr_shape)
    
    if len(arr_shape) == 2:
        
        # there is only one channel, so that one channel is all 1's
        dummy_arr = np.expand_dims(dummy_arr,-1)
    
    else:
        # multiply each channel by the channel number (1-based)
        for i in range(arr_shape[-1]):
            dummy_arr[:,:,i] *= i+1
    
    return dummy_arr

# a helper function to write a 3D array of data to disk as a GeoTIFF 
# the result will have no spatial info or relevance
def dummy_tif_writer(arr, dst_filename):
    """
        dummy_tif_writer(arr_dst_filename) writes a tif file specified by dst_filename using the array specified
        by arr. The shape of arr should be 3 dimensional such that the last dimension is the number of bands.
        this type of array can be created with the createArray(arr_shape) function.
    """

    # make sure the array is 3 dimensional, assuming last dimension is number of bands
    # this is assured by using createArray to generate the data
    assert len(arr.shape) == 3
    
    try:
        # define a dummy geotransform
        geotrans = (0,1,0,0,0,-1)

        # get the dimensions of the array
        n_rows, n_cols, n_channels = arr.shape
        n_rows, n_cols, n_channels

        x_pixels = n_cols  # number of pixels in x
        y_pixels = n_rows  # number of pixels in y

        # set the driver
        driver = gdal.GetDriverByName('GTiff')

        # create the file
        dataset = driver.Create(dst_filename, x_pixels, y_pixels, int(n_channels), gdal.GDT_Byte)

        # write the bands
        for i in range(n_channels):
            dataset.GetRasterBand(i+1).WriteArray(dummy[:,:,i])

        # define the Unknown projection
        srs = osr.SpatialReference()            
        srs.ImportFromEPSG(0)
        proj = srs.ExportToWkt() 

        # set the geotransform
        dataset.SetGeoTransform(geotrans)

        # set the projection
        dataset.SetProjection(proj)

        # flush the cache
        dataset.FlushCache()

        # remove the dataset from memory
        dataset=None
    
        return (0, dst_filename)
    
    except Exception as e:
        
        return(e, None)
    

def test_dummy():
    """"Dummy test that will pass."""
    assert 1 == 1
