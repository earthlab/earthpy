""" Tests for the spatial module. """

import os
import numpy as np
import pytest
import geopandas as gpd
import rasterio as rio
from affine import Affine
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


@pytest.fixture
def output_dir(out_path):
    return out_path[:-8]


@pytest.fixture
def output_file_list(output_dir):
    output_file_list = []
    for i in range(4):
        output_file_list.append(
            os.path.join(output_dir, "file" + str(i) + ".tif")
        )
    return output_file_list


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


def test_crop_all_returns_list(in_paths, output_dir, basic_geometry_gdf):
    """Test that crop all returns a list. """
    img_list = es.crop_all(
        in_paths, output_dir, basic_geometry_gdf, overwrite=True
    )
    assert type(img_list) == list


def test_crop_all_returns_list_when_given_list(
    in_paths, output_file_list, basic_geometry_gdf
):
    """Test that crop all returns a list when given a list instead of a directory. """
    img_list = es.crop_all(
        in_paths, output_file_list, basic_geometry_gdf, overwrite=True
    )
    assert isinstance(img_list, list)


def test_crop_all_files_exist(in_paths, output_dir, basic_geometry_gdf):
    """Test that crop all actually creates the files in the directory. """
    img_list = es.crop_all(
        in_paths, output_dir, basic_geometry_gdf, overwrite=True
    )
    for files in img_list:
        assert os.path.exists(files)


def test_crop_all_fails_overwrite(in_paths, output_dir, basic_geometry_gdf):
    """Test that crop all fails when overwrite isn't set to True if files already exist. """
    with pytest.raises(ValueError, match="The file "):
        es.crop_all(in_paths, output_dir, basic_geometry_gdf)


def test_crop_all_fails_bad_dir(in_paths, basic_geometry_gdf):
    """Test crop all fails if user provides a bad directory path. """
    bad_path = "Badpath"
    with pytest.raises(TypeError, match="The output directo"):
        es.crop_all(in_paths, bad_path, basic_geometry_gdf, overwrite=True)


def test_crop_all_fails_bad_dir_list(in_paths, basic_geometry_gdf):
    """Test crop all fails if user provides a list of bad directory path. """
    bad_path_list = ["Badpath0", "Badpath1", "Badpath2", "Badpath3"]
    with pytest.raises(TypeError, match="The output directo"):
        es.crop_all(
            in_paths, bad_path_list, basic_geometry_gdf, overwrite=True
        )


def test_crop_all_returns_list_of_same_len(
    in_paths, output_dir, basic_geometry_gdf
):
    """Test that crop all returns a list of the same length as the input list. """
    img_list = es.crop_all(
        in_paths, output_dir, basic_geometry_gdf, overwrite=True
    )
    assert len(img_list) == len(in_paths)


def test_crop_all_fails_with_mismatch_list_len(
    in_paths, output_file_list, basic_geometry_gdf
):
    """Test that crop all fails if the input and output list lengths don't match. """
    path = os.path.commonpath(output_file_list)
    output_file_list.append(os.path.join(path, "file5.tif"))
    with pytest.raises(TypeError, match="The list of input bands does not m"):
        es.crop_all(
            in_paths, output_file_list, basic_geometry_gdf, overwrite=True
        )


def test_crop_all_verbose(in_paths, output_dir, basic_geometry_gdf):
    """Test that when verbose is set to false, nothing is returned. """
    out_list = es.crop_all(
        in_paths, output_dir, basic_geometry_gdf, overwrite=True, verbose=False
    )
    assert out_list is None


def test_crop_all_with_geoms(in_paths, output_file_list, basic_geometry):
    """Test crop all works with geoms instead of a gdf. """
    test = es.crop_all(
        in_paths, output_file_list, [basic_geometry], overwrite=True
    )
    assert isinstance(test, list)


def test_crop_all_with_nonoverlapping_geom(in_paths, output_file_list):
    """Test crop all if extents don't overlap. """
    bad_geom = Polygon(
        [(12, 12), (12, 14.25), (14.25, 14.25), (14.25, 12), (12, 12)]
    )
    with pytest.raises(ValueError, match="Input shapes do not ov"):
        es.crop_all(in_paths, output_file_list, [bad_geom], overwrite=True)
