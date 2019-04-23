"""Tests for the clip module."""

import pytest
from shapely.geometry import Polygon, Point, LineString
import shapely
import geopandas as gpd
import earthpy.clip as cl
import numpy as np


# TODO Make sure we are testing that attributes are returned
# TODO make sure that we are using multiple shapes not just one


def make_locs_gdf():
    """ Create a dummy point GeoDataFrame. """
    pts = np.array([[2, 2], [3, 4], [9, 8], [-12, -15]])
    gdf = gpd.GeoDataFrame(
        [Point(xy) for xy in pts],
        columns=["geometry"],
        crs={"init": "epsg:4326"},
    )
    return gdf


def make_single_rect_poly_gdf():
    """ Bounding box polygon. """
    poly_inters = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
    gdf = gpd.GeoDataFrame(
        [1], geometry=[poly_inters], crs={"init": "epsg:4326"}
    )
    gdf["attr2"] = ["road"]
    return gdf


def make_locs_buff():
    """ Buffer points to create multi poly. """
    buffered_locations = make_locs_gdf()
    buffered_locations["geometry"] = buffered_locations.buffer(4)
    return buffered_locations


def make_donut_geom():
    """ Make a donut geometry. """
    donut = gpd.overlay(
        make_locs_buff(),
        make_single_rect_poly_gdf(),
        how="symmetric_difference",
    )
    return donut


@pytest.fixture
def locs_gdf():
    """ Create a sample point GeoDataFrame.

    This fixture calls make_locs_gdf(), which is a function that is used in
    multiple fixtures. But, fixtures are not supposed to be used like that:

    see https://github.com/pytest-dev/pytest/issues/3950 for discussion
    """
    return make_locs_gdf()


@pytest.fixture
def linez_gdf():
    """ Create Line Objects For Testing """
    linea = LineString([(1, 1), (2, 2), (3, 2), (5, 3)])
    lineb = LineString([(3, 4), (5, 7), (12, 2), (10, 5), (9, 7.5)])
    gdf = gpd.GeoDataFrame(
        [1, 2], geometry=[linea, lineb], crs={"init": "epsg:4326"}
    )
    return gdf


@pytest.fixture
def single_rect_poly_gdf():
    """ Fixture for a bounding box polygon. """
    return make_single_rect_poly_gdf()


@pytest.fixture
def locs_buff():
    """ Fixture for buffered locations. """
    return make_locs_buff()


@pytest.fixture
def donut_geom():
    """ Fixture for donut geometry objects. """
    return make_donut_geom()


@pytest.fixture
def multi_gdf():
    """ Create a multi-polygon GeoDataFrame. """
    multi_poly = make_donut_geom().unary_union
    out_df = gpd.GeoDataFrame(
        geometry=gpd.GeoSeries(multi_poly), crs={"init": "epsg:4326"}
    )
    out_df = out_df.rename(columns={0: "geometry"}).set_geometry("geometry")
    out_df["attr"] = ["pool"]
    return out_df


# TODO -- this fixture should have more than one multi line and atleast one attribute column
#  with several diff attribute values like line one: type: road, line two: type pool


@pytest.fixture
def multi_line(linez_gdf):
    """ Create a multi-line GeoDataFrame.

    This has one multi line and another regular line.
    """
    # Create a single and multi line object
    multiline_feat = linez_gdf.unary_union
    linec = LineString([(2, 1), (3, 1), (4, 1), (5, 2)])
    out_df = gpd.GeoDataFrame(
        geometry=gpd.GeoSeries([multiline_feat, linec]),
        crs={"init": "epsg:4326"},
    )
    out_df = out_df.rename(columns={0: "geometry"}).set_geometry("geometry")
    out_df["attr"] = ["road", "stream"]
    return out_df


@pytest.fixture
def multi_point():
    """ Create a multi-line GeoDataFrame. """
    multi_point = make_locs_gdf().unary_union
    out_df = gpd.GeoDataFrame(
        gpd.GeoSeries(multi_point), crs={"init": "epsg:4326"}
    )
    out_df = out_df.rename(columns={0: "geometry"}).set_geometry("geometry")
    return out_df


def make_locs_gdf():
    """ Create a dummy point GeoDataFrame. """
    pts = np.array([[2, 2], [3, 4], [9, 8], [-12, -15]])
    gdf = gpd.GeoDataFrame(
        [Point(xy) for xy in pts],
        columns=["geometry"],
        crs={"init": "epsg:4326"},
    )
    return gdf


def make_single_rect_poly_gdf():
    """ Bounding box polygon. """
    poly_inters = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
    gdf = gpd.GeoDataFrame(
        [1], geometry=[poly_inters], crs={"init": "epsg:4326"}
    )
    gdf["attribute1"] = ["roads"]
    return gdf


def make_locs_buff():
    """ Buffer points to create multi poly. """
    buffered_locations = make_locs_gdf()
    buffered_locations["geometry"] = buffered_locations.buffer(4)
    return buffered_locations


def make_donut_geom():
    """ Make a donut geometry. """
    donut = gpd.overlay(
        make_locs_buff(),
        make_single_rect_poly_gdf(),
        how="symmetric_difference",
    )
    return donut


@pytest.fixture
def locs_gdf():
    """ Get a dummy point GeoDataFrame.

    This fixture calls make_locs_gdf(), which is a function that is used in
    multiple fixtures. But, fixtures are not supposed to be used like that:

    see https://github.com/pytest-dev/pytest/issues/3950 for discussion
    """
    return make_locs_gdf()


@pytest.fixture
def linez_gdf():
    """ Create Line Objects For Testing """
    linea = LineString([(1, 1), (2, 2), (3, 2), (5, 3)])
    lineb = LineString([(3, 4), (5, 7), (12, 2), (10, 5), (9, 7.5)])
    gdf = gpd.GeoDataFrame(
        [1, 2], geometry=[linea, lineb], crs={"init": "epsg:4326"}
    )
    return gdf


@pytest.fixture
def single_rect_poly_gdf():
    """ Fixture for a bounding box polygon. """
    return make_single_rect_poly_gdf()


@pytest.fixture
def locs_buff():
    """ Fixture for buffered locations. """
    return make_locs_buff()


@pytest.fixture
def donut_geom():
    """ Fixture for donut geometry objects. """
    return make_donut_geom()


@pytest.fixture
def multi_gdf():
    """ Create a multi-polygon GeoDataFrame. """
    multi_poly = make_donut_geom().unary_union
    out_df = gpd.GeoDataFrame(
        gpd.GeoSeries(multi_poly), crs={"init": "epsg:4326"}
    )
    out_df = out_df.rename(columns={0: "geometry"}).set_geometry("geometry")
    out_df["attr1"] = "pools"
    return out_df


def test_not_gdf(single_rect_poly_gdf):
    """Non-GeoDataFrame inputs raise attribute errors."""
    with pytest.raises(AttributeError):
        cl.clip_shp((2, 3), single_rect_poly_gdf)
    with pytest.raises(AttributeError):
        cl.clip_shp(single_rect_poly_gdf, (2, 3))


def test_returns_gdf(locs_gdf, single_rect_poly_gdf):
    """Test that function returns a GeoDataFrame (or GDF-like) object."""
    out = cl.clip_shp(locs_gdf, single_rect_poly_gdf)
    assert hasattr(out, "geometry")


def test_non_overlapping_geoms():
    """Test that a bounding box returns error if the extents don't overlap"""
    unit_box = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
    unit_gdf = gpd.GeoDataFrame(
        [1], geometry=[unit_box], crs={"init": "epsg:4326"}
    )
    non_overlapping_gdf = unit_gdf.copy()
    non_overlapping_gdf = unit_gdf.geometry.apply(
        lambda x: shapely.affinity.translate(x, xoff=20)
    )
    with pytest.raises(ValueError):
        cl.clip_shp(unit_gdf, non_overlapping_gdf)


def test_input_gdfs(single_rect_poly_gdf):
    """Test that function fails if not provided with 2 GDFs."""
    with pytest.raises(AttributeError):
        cl.clip_shp(list(), single_rect_poly_gdf)
    with pytest.raises(AttributeError):
        cl.clip_shp(single_rect_poly_gdf, list())


def test_clip_points(locs_gdf, single_rect_poly_gdf):
    """Test clipping a points GDF with a generic polygon geometry."""
    clip_pts = cl.clip_shp(locs_gdf, single_rect_poly_gdf)
    assert len(clip_pts.geometry) == 3 and clip_pts.geom_type[1] == "Point"


def test_clip_poly(locs_buff, single_rect_poly_gdf):
    """Test clipping a polygon GDF with a generic polygon geometry."""
    clipped_poly = cl.clip_shp(locs_buff, single_rect_poly_gdf)
    assert len(clipped_poly.geometry) == 3
    assert clipped_poly.geom_type[1] == "Polygon"


# TODO -- this function actually clips USING a multi -- we have not coded for that I think??
# We should probably remove this function buf rename it if we keep it
# def test_clip_multipoly(single_rect_poly_gdf, multi_gdf):
#     """Test that multi poly returns a value error."""
#     clip = cl.clip_shp(single_rect_poly_gdf, multi_gdf)
#     assert hasattr(clip, "geometry") and clip.geom_type[0] == "MultiPolygon"


def test_clip_multipoly(multi_gdf, single_rect_poly_gdf):
    """Test a multi poly object can be clipped properly.

    Also the bounds of the object should == the bounds of the clip object
    if they fully overlap (as they do in these fixtures). """
    clip = cl.clip_shp(multi_gdf, single_rect_poly_gdf)
    assert hasattr(clip, "geometry")
    assert np.array_equal(clip.total_bounds, single_rect_poly_gdf.total_bounds)
    # 2 features should be returned with an attribute column
    assert len(clip.attr1) == 2


# TODO make sure all of the doc strings clearly define what each of these do
# TODO make sure that we are testing clipping a multi object not clipping with a multi object (i believe this is fixed now)
# TODO make sure we test clipping objects with multiple features that may have different attributes
# TODO: make sure clipping with a multi object works?? (do we want to support that yet or not - if not provide a message saying it's not supported).
# TODO: cleanup multiline  & multi point and test both!


def test_clip_multiline(single_rect_poly_gdf, multi_line):
    """Test that clipping a multiline feature with a poly returns expected output."""

    clip = cl.clip_shp(multi_line, single_rect_poly_gdf)
    assert hasattr(clip, "geometry") and clip.geom_type[0] == "MultiLineString"


def test_clip_multipoint(single_rect_poly_gdf, multi_point):
    """Clipping a multipoint feature with a polygon works as expected."""

    clip = cl.clip_shp(multi_point, single_rect_poly_gdf)
    assert hasattr(clip, "geometry") and clip.geom_type[0] == "MultiPoint"


def test_clip_lines(linez_gdf, single_rect_poly_gdf):
    """Test what happens when you give the clip_extent a line GDF."""
    clip_line = cl.clip_shp(linez_gdf, single_rect_poly_gdf)
    assert len(clip_line.geometry) == 2
