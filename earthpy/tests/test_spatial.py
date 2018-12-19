""" Tests for the spatial module. """

import os
import numpy as np
import pandas as pd
import pytest
from affine import Affine
import geopandas as gpd
from osgeo import gdal
from osgeo import osr
import rasterio as rio
from shapely.geometry import Polygon, Point, LineString
import earthpy.spatial as es


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
        es.stack_raster_tifs(
            band_paths=["fname1.tif", "fname2.tif"],
            out_path="nonexistent_directory/output.tif",
        )


def test_crop_image_with_gdf(basic_image_tif, basic_geometry_gdf):
    """ Cropping with a GeoDataFrame works when all_touched=True.

    Cropping basic_image_tif file with the basic geometry should return
    all of the cells that have the value 1.
    """
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, basic_geometry_gdf, all_touched=True)
        print(meta)
    assert np.sum(img) == 9


def test_crop_image_with_gdf_touch_false(basic_image_tif, basic_geometry_gdf):
    """ Cropping with a GeoDataFrame works when all_touched=False. """
    print([es.extent_to_json(basic_geometry_gdf)])
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, basic_geometry_gdf, all_touched=False)
    assert np.sum(img) == 4


def test_crop_image_with_geometry(basic_image_tif, basic_geometry):
    """ Cropping with a geometry works with all_touched=True. """
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, [basic_geometry], all_touched=True)
    assert np.sum(img) == 9


def test_crop_image_with_geometry_touch_false(basic_image_tif, basic_geometry):
    """ Cropping with a geometry works with all_touched=False. """
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, [basic_geometry], all_touched=False)
    assert np.sum(img) == 4


def test_crop_image_when_poly_bounds_image_extent(basic_image_tif):
    """ When an image is fully contained in a larger polygon, dont crop. """
    big_polygon = Polygon([(-1, -1), (11, -1), (11, 11), (-1, 11), (-1, -1)])
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, [big_polygon])
        src_array = src.read()
    assert np.array_equal(img, src_array)


def test_crop_image_with_one_point_raises_error(basic_image_tif):
    """ Cropping an image with one point should raise an error. """
    point = Point([(1, 1)])
    with rio.open(basic_image_tif) as src:
        with pytest.raises(ValueError, match="width and height must be > 0"):
            es.crop_image(src, [point])


def crop_image_with_1d_extent_raises_error(basic_image_tif):
    """ Cropping with a horizontal or vertical line raises an error. """
    line = LineString([(1, 1), (2, 1), (3, 1)])
    with rio.open(basic_image_tif) as src:
        with pytest.raises(ValueError, match="width and height must be > 0"):
            es.crop_image(src, [line])
