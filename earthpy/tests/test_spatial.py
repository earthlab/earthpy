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
import os

# A helper function to write a 3D array of data to disk as a GeoTIFF
# The result will have no spatial info or relevance
def create_tif_file(arr, destfile):
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
        geotrans = (0, 1, 0, 0, 0, -1)

        # Get the dimensions of the array
        y_pixels, x_pixels, n_channels = arr.shape

        # Create the GeoTIFF file
        driver = gdal.GetDriverByName("GTiff")
        dataset = driver.Create(
            destfile, x_pixels, y_pixels, int(n_channels), gdal.GDT_Float32
        )

        # Write the bands to the GeoTIFF
        for i in range(n_channels):
            dataset.GetRasterBand(i + 1).WriteArray(arr[:, :, i])

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
        return (e, None)


def test_create_tif_file():
    """ Testing dummy_tif_writer."""
    destfile = "dummy.tif"
    arr = np.ones((5, 5, 1))
    code, fi = create_tif_file(arr, destfile)

    assert code == 0
    assert os.path.exists(destfile) is True

    # Clean up the file
    if os.path.exists(destfile):
        os.remove(destfile)


def test_extent_to_json():
    """"Unit tests for extent_to_json()."""
    # Giving a list [minx, miny, maxx, maxy] makes a polygon
    list_out = es.extent_to_json([0, 0, 1, 1])
    assert list_out["type"] == "Polygon"

    # The polygon is the unit square
    list_poly = Polygon(list_out["coordinates"][0])
    assert list_poly.area == 1
    assert list_poly.length == 4

    # Providing a GeoDataFrame creates identical output
    points_df = pd.DataFrame({"lat": [0, 1], "lon": [0, 1]})
    points_df["coords"] = list(zip(points_df.lon, points_df.lat))
    points_df["coords"] = points_df["coords"].apply(Point)
    gdf = gpd.GeoDataFrame(points_df, geometry="coords")
    gdf_out = es.extent_to_json(gdf)
    assert gdf_out == list_out

    # Giving non-list or GeoDataFrame input raises a ValueError
    with pytest.raises(ValueError):
        es.extent_to_json({"a": "dict"})

    # Giving minima that exceed maxima raises an error for both x and y coords
    with pytest.raises(AssertionError):
        es.extent_to_json([1, 0, 0, 1])

    with pytest.raises(AssertionError):
        es.extent_to_json([0, 1, 1, 0])


def test_bytescale_high_low_val():
    """"Unit tests for earthpy.spatial.bytescale """
    arr = np.random.randint(300, size=(10, 10))

    # Bad high value
    with pytest.raises(
        ValueError, message="`high` should be less than or equal to 255."
    ):
        es.bytescale(arr, high=300)

    # Bad low value
    with pytest.raises(
        ValueError, message="`low` should be greater than or equal to 0."
    ):
        es.bytescale(arr, low=-100)

    # High value is less than low value
    with pytest.raises(
        ValueError, message="`high` should be greater than or equal to `low`."
    ):
        es.bytescale(arr, high=100, low=150)

    # Valid case. should also take care of if statements for cmin/cmax
    val_arr = es.bytescale(arr, high=255, low=0)

    assert val_arr.min() == 0
    assert val_arr.max() == 255

    # Test scale value max is less than min
    with pytest.raises(
        ValueError, message="`cmax` should be larger than `cmin`."
    ):
        es.bytescale(arr, cmin=100, cmax=50)

    # Test scale value max is less equal to min. Commented out for now because it breaks stuff somehow.
    with pytest.raises(
        ValueError,
        message="`cmax` and `cmin` should not be the same value. Please specify `cmax` > `cmin`",
    ):
        es.bytescale(arr, cmin=100, cmax=100)

    # Test scale value max is less equal to min
    scale_arr = es.bytescale(arr, cmin=10, cmax=240)

    assert scale_arr.min() == 0
    assert scale_arr.max() == 255


def test_stack_invalid_out_paths_raise_errors():
    """ If users provide an output path that doesn't exist, raise error. """
    with pytest.raises(ValueError, match="not exist"):
        es.stack(band_paths=['fname1.tif', 'fname2.tif'],
                             out_path="nonexistent_directory/output.tif")

                             
def test_stack_raster():
    """Unit tests for raster stacking with es.stack()."""
    
    # Create a number of files with create_tif_file
    band_files = ["dummy{}.tif".format(i) for i in range(4)]
    arr = np.ones((5, 5, 1))

    test_files = []
    for bfi in band_files:    
        code, fi = create_tif_file(arr, bfi)
        test_files.append(fi)
    
    # Test output path is valid when write_raster is True
    with pytest.raises(ValueError, message="Please specify a valid file name for output."):
        stack_arr, stack_prof = es.stack(band_files, out_path='', write_raster=True)
        
    # Test write_raster flag needs to be True if out_path is valid and specified
    out_fi = 'test_stack.tif'
    with pytest.raises(ValueError, message="Please specify write_raster==True to generate output file {}".format(out_fi)):
        stack_arr, stack_prof = es.stack(band_files, out_path=out_fi, write_raster=False)
        
    # Test that out_path needs a file extension to be valid
    out_fi = 'test_stack'
    with pytest.raises(ValueError, message="Please specify a valid file name for output."):
        stack_arr, stack_prof = es.stack(band_files, out_path=out_fi, write_raster=True) 

    # Test that the output file format is same as inputs
    # THIS CAN BE FLEXIBLE BUT FOR NOW FORCING SAME FORMAT
    out_fi = 'test_stack.jp2'
    with pytest.raises(ValueError, message="Source data is GTiff. Please specify corresponding output extension."):
        stack_arr, stack_prof = es.stack(band_files, out_path=out_fi, write_raster=True)
        
    # Test valid use case specifying output file. 
    # Make sure the output file exists and then clean it up
    out_fi = 'test_stack.tif'
    stack_arr, stack_prof = es.stack(band_files, out_path=out_fi, write_raster=True)
    
    assert os.path.exists(out_fi)
    if os.path.exists(out_fi):
        os.remove(out_fi)
        
    # Test valid use case of just getting back the array. 
    stack_arr, stack_prof = es.stack(test_files)
    
    assert stack_arr.shape[0] == len(test_files)
    assert stack_prof['count'] == len(test_files)
    
    # Clean up files
    for tfi in test_files:
        os.remove(tfi)
    
    
    