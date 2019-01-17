""" Tests for the spatial module. """

import numpy as np
import numpy.ma as ma
import pandas as pd
import pytest
import geopandas as gpd
import rasterio as rio
from shapely.geometry import Polygon, Point, LineString
import earthpy.spatial as es
import os


@pytest.fixture
def b1_b2_arrs():
    b1 = np.array([[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
    b2 = np.array([[1, 2, 3, 4, 5], [14, 12, 13, 14, 17]])
    return b1, b2


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


def test_normalized_diff_shapes(b1_b2_arrs):
    """Test that two arrays with different shapes returns a ValueError."""

    # Test data
    b1, b2 = b1_b2_arrs
    b2 = b2[0]

    # Check ValueError
    with pytest.raises(
        ValueError, match="Both arrays should have the same dimensions"
    ):
        es.normalized_diff(b1=b1, b2=b2)


def test_normalized_diff_no_mask(b1_b2_arrs):
    """Test that if result does not include nan values,
    the array is returned as unmasked."""

    # Test data
    b1, b2 = b1_b2_arrs

    n_diff = es.normalized_diff(b1=b1, b2=b2)

    # Output array unmasked
    assert not ma.is_masked(n_diff)


def test_normalized_diff_inf(b1_b2_arrs):
    """Test that inf values in result are set to nan and
    that array is returned as masked."""

    # Test data
    b1, b2 = b1_b2_arrs
    b2[1:, 4:] = -20

    # Check warning
    with pytest.warns(
        Warning, match="Divide by zero produced infinity values"
    ):
        n_diff = es.normalized_diff(b1=b1, b2=b2)

    # Inf values set to nan
    assert not np.isinf(n_diff).any()

    # Output array masked
    assert ma.is_masked(n_diff)


def test_normalized_diff_mask(b1_b2_arrs):
    """Test that if result does include nan values,
    the array is returned as masked."""

    # Test data
    b1, b2 = b1_b2_arrs
    b2 = b2.astype(float)
    b2[1:, 4:] = np.nan

    n_diff = es.normalized_diff(b1=b1, b2=b2)

    # Output array masked
    assert ma.is_masked(n_diff)


def test_bytescale_high_low_val():
    """"Unit tests for earthpy.spatial.bytescale """
    arr = np.random.randint(300, size=(10, 10))

    # Bad high value
    with pytest.raises(
        ValueError, match="`high` should be less than or equal to 255."
    ):
        es.bytescale(arr, high=300)

    # Bad low value
    with pytest.raises(
        ValueError, match="`low` should be greater than or equal to 0."
    ):
        es.bytescale(arr, low=-100)

    # High value is less than low value
    with pytest.raises(
        ValueError, match="`high` should be greater than or equal to `low`."
    ):
        es.bytescale(arr, high=100, low=150)

    # Valid case. should also take care of if statements for cmin/cmax
    val_arr = es.bytescale(arr, high=255, low=0)

    assert val_arr.min() == 0
    assert val_arr.max() == 255

    # Test scale value max is less than min
    with pytest.raises(
        ValueError, match="`cmax` should be larger than `cmin`."
    ):
        es.bytescale(arr, cmin=100, cmax=50)

    # Test scale value max is less equal to min. Commented out for now because it breaks stuff somehow.
    with pytest.raises(
        ValueError,
        match="`cmax` and `cmin` should not be the same value. Please specify `cmax` > `cmin`",
    ):
        es.bytescale(arr, cmin=100, cmax=100)

    # Test scale value max is less equal to min
    scale_arr = es.bytescale(arr, cmin=10, cmax=240)

    assert scale_arr.min() == 0
    assert scale_arr.max() == 255


def test_stack_invalid_out_paths_raise_errors():
    """ If users provide an output path that doesn't exist, raise error. """
    with pytest.raises(ValueError, match="not exist"):
        es.stack(
            band_paths=["fname1.tif", "fname2.tif"],
            out_path="nonexistent_directory/output.tif",
        )


def test_stack_raster(basic_image_tif):
    """Unit tests for raster stacking with es.stack()."""

    # create list of 4 basic_image_tif files (filepaths)
    test_files = [basic_image_tif] * 4
    band_files = [basic_image_tif] * 4

    # Test output path is valid when write_raster is True
    with pytest.raises(
        ValueError, match="Please specify a valid file name for output."
    ):
        stack_arr, stack_prof = es.stack(
            band_files, out_path="", write_raster=True
        )

    # Test write_raster flag needs to be True if out_path is valid and specified
    out_fi = "test_stack.tif"
    with pytest.raises(
        ValueError,
        match="Please specify write_raster==True to generate output file {}".format(
            out_fi
        ),
    ):
        stack_arr, stack_prof = es.stack(
            band_files, out_path=out_fi, write_raster=False
        )

    # Test that out_path needs a file extension to be valid
    out_fi = "test_stack"
    with pytest.raises(
        ValueError, match="Please specify a valid file name for output."
    ):
        stack_arr, stack_prof = es.stack(
            band_files, out_path=out_fi, write_raster=True
        )

    # Test that the output file format is same as inputs
    # THIS CAN BE FLEXIBLE BUT FOR NOW FORCING SAME FORMAT
    out_fi = "test_stack.jp2"
    with pytest.raises(
        ValueError,
        match="Source data is GTiff. Please specify corresponding output extension.",
    ):
        stack_arr, stack_prof = es.stack(
            band_files, out_path=out_fi, write_raster=True
        )

    # Test valid use case specifying output file.
    # Make sure the output file exists and then clean it up
    out_fi = "test_stack.tif"
    stack_arr, stack_prof = es.stack(
        band_files, out_path=out_fi, write_raster=True
    )

    assert os.path.exists(out_fi)
    if os.path.exists(out_fi):
        os.remove(out_fi)

    # Test valid use case of just getting back the array.
    stack_arr, stack_prof = es.stack(test_files)

    assert stack_arr.shape[0] == len(test_files)
    assert stack_prof["count"] == len(test_files)

    # Clean up files
    # os.remove(basic_image_tif)


def test_crop_image_with_gdf(basic_image_tif, basic_geometry_gdf):
    """ Cropping with a GeoDataFrame works when all_touched=True.

    Cropping basic_image_tif file with the basic geometry fixture returns
    all of the cells that have the value 1 in the basic_image_tif fixture

    These fixtures are described in conftest.py
    """
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, basic_geometry_gdf, all_touched=True)
    assert np.sum(img) == 9


def test_crop_image_with_gdf_touch_false(basic_image_tif, basic_geometry_gdf):
    """ Cropping with a GeoDataFrame works when all_touched=False. """
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, basic_geometry_gdf, all_touched=False)
    assert np.sum(img) == 4


def test_crop_image_with_geometry(basic_image_tif, basic_geometry):
    """ Cropping with a geometry works with all_touched=True. """
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, [basic_geometry], all_touched=True)
    assert np.sum(img) == 9


def test_crop_image_with_geojson_touch_false(basic_image_tif, basic_geometry):
    """ Cropping with GeoJSON works when all_touched=False. """
    geojson = basic_geometry.__geo_interface__
    with rio.open(basic_image_tif) as src:
        img, meta = es.crop_image(src, [geojson], all_touched=False)
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


def test_crop_image_with_1d_extent_raises_error(basic_image_tif):
    """ Cropping with a horizontal or vertical line raises an error. """
    line = LineString([(1, 1), (2, 1), (3, 1)])
    with rio.open(basic_image_tif) as src:
        with pytest.raises(ValueError, match="width and height must be > 0"):
            es.crop_image(src, [line])


def test_crop_image_fails_two_rasters(basic_image_tif, basic_geometry):
    """ crop_image should raise an error if provided two rasters. """
    with rio.open(basic_image_tif) as src:
        with pytest.raises(TypeError):
            es.crop_image(src, src)


def test_crop_image_swapped_args(basic_image_tif, basic_geometry):
    """ If users provide a polygon instead of raster raise an error. """
    with pytest.raises(AttributeError):
        es.crop_image(basic_geometry, basic_image_tif)
    with pytest.raises(AttributeError):
        es.crop_image(basic_geometry, basic_geometry)


def test_crop_image_fails_empty_list(basic_image_tif, basic_geometry):
    """ If users provide empty list as arg, crop_image fails. """
    with pytest.raises(AttributeError):
        es.crop_image(list(), basic_geometry)
    with rio.open(basic_image_tif) as src:
        with pytest.raises(ValueError):
            es.crop_image(src, list())
