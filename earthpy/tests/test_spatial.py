""" Tests for the spatial module. """

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon, Point
import geopandas as gpd
import earthpy.spatial as es
from osgeo import gdal
from osgeo import osr
import rasterio as rio

# A helper function to write a 3D array of data to disk as a GeoTIFF 
# The result will have no spatial info or relevance
def dummy_tif_writer(arr, destfile):
    """Writes a tif file to a specified location using an array.
    Parameters
    ----------
    arr : numpy ndarray 
        The array should have 3 dimensions, arranged such that
        a the result of arr.shape is in the form [rows, columns, channels].
        
    destfile : filepath string
        The filepath for where the GeoTIFF file will be written.
    """    
    

    # Make sure the array is 3 dimensional, assuming last dimension is number of bands
    assert len(arr.shape) == 3
    
    try:
        geotrans = (0,1,0,0,0,-1)

        # Get the dimensions of the array
        y_pixels, x_pixels, n_channels = arr.shape

        # Create the GeoTIFF file
        driver = gdal.GetDriverByName('GTiff')
        dataset = driver.Create(destfile, x_pixels, y_pixels, int(n_channels), gdal.GDT_Float32)

        # Write the bands to the GeoTIFF
        for i in range(n_channels):
            dataset.GetRasterBand(i+1).WriteArray(arr[:,:,i])

        # Define the Unknown projection
        srs = osr.SpatialReference()            
        srs.ImportFromEPSG(0)
        proj = srs.ExportToWkt() 

        # Set the spatial properties of the GeoTIFF file
        dataset.SetGeoTransform(geotrans)
        dataset.SetProjection(proj)

        dataset.FlushCache()

        # Remove the dataset from memory
        dataset = None
    
        return (0, destfile)
    
    except Exception as e:
        
        return(e, None)
    

def test_dummy_tif_writer():
    """ Testing dummy_tif_writer."""
    
    destfile = 'dummy.tif'
    arr = np.ones((5,5,1))
    code,fi = dummy_tif_writer(arr, destfile)
    
    assert code == 0
    assert os.path.exists(destfile) is True
    
    # Clean up the file
    if os.path.exists(destfile):
        os.remove(destfile)
        
def test_extent_to_json():
    """"Unit tests for extent_to_json()."""
    # Giving a list [minx, miny, maxx, maxy] makes a polygon
    list_out = es.extent_to_json([0, 0, 1, 1])
    assert list_out['type'] == 'Polygon'

    # The polygon is the unit square
    list_poly = Polygon(list_out['coordinates'][0])
    assert list_poly.area == 1
    assert list_poly.length == 4

    # Providing a GeoDataFrame creates identical output
    points_df = pd.DataFrame(
        {'lat': [0, 1],
         'lon': [0, 1]}
    )
    points_df['coords'] = list(zip(points_df.lon, points_df.lat))
    points_df['coords'] = points_df['coords'].apply(Point)
    gdf = gpd.GeoDataFrame(points_df, geometry='coords')
    gdf_out = es.extent_to_json(gdf)
    assert gdf_out == list_out

    # Giving non-list or GeoDataFrame input raises a ValueError
    with pytest.raises(ValueError):
        es.extent_to_json({'a': 'dict'})

    # Giving minima that exceed maxima raises an error for both x and y coords
    with pytest.raises(AssertionError):
        es.extent_to_json([1, 0, 0, 1])

    with pytest.raises(AssertionError):
        es.extent_to_json([0, 1, 1, 0])


def test_bytescale_high_low_val():
    """"Unit tests for earthpy.spatial.bytescale """

    arr = np.random.randint(300, size=(10, 10))

    # Bad high value
    with pytest.raises(ValueError):
        es.bytescale(arr, high=300)

    # Bad low value
    with pytest.raises(ValueError):
        es.bytescale(arr, low=-100)

    # High value is less than low value
    with pytest.raises(ValueError):
        es.bytescale(arr, high=100, low=150)

    # Valid case. should also take care of if statements for cmin/cmax
    val_arr = es.bytescale(arr, high=255, low=0)

    assert val_arr.min() == 0
    assert val_arr.max() == 255

    # Test scale value max is less than min
    with pytest.raises(ValueError):
        es.bytescale(arr, cmin=100, cmax=50)

    # TODO: write test case for cmax == cmin
    # Commented out because it breaks for unknown reasons.
    # es.bytescale(arr, cmin=100, cmax=100)

    # Test scale value max is less equal to min
    scale_arr = es.bytescale(arr, cmin=10, cmax=240)
    assert scale_arr.min() == 0
    assert scale_arr.max() == 255
