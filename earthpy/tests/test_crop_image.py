""" Tests for the spatial module. """

import numpy as np
import pytest
import geopandas as gpd
import rasterio as rio
from shapely.geometry import Polygon, Point, LineString
import earthpy.spatial as es


@pytest.fixture
def basic_geometry():
    """
    A square polygon spanning (2, 2) to (4.25, 4.25) in x and y directions
    Borrowed from rasterio/tests/conftest.py

    Returns
    -------
    dict: GeoJSON-style geometry object.
        Coordinates are in grid coordinates (Affine.identity()).
    """
    return Polygon([(2, 2), (2, 4.25), (4.25, 4.25), (4.25, 2), (2, 2)])


@pytest.fixture
def basic_geometry_gdf(basic_geometry):
    """
    A GeoDataFrame containing the basic geometry

    Returns
    -------
    GeoDataFrame containing the basic_geometry polygon
    """
    gdf = gpd.GeoDataFrame(
        geometry=[basic_geometry], crs={"init": "epsg:4326"}
    )
    return gdf


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
