"""Tests for the clip module."""

import pytest
import numpy as np
from shapely.geometry import Polygon, Point, LineString
import shapely
import geopandas as gpd
import earthpy.clip as cl


def make_locs_gdf():
    """ Create a dummy point GeoDataFrame. """
    pts = np.array([[2, 2], [3, 4], [9, 8], [-12, -15]])
    gdf = gpd.GeoDataFrame(
        [Point(xy) for xy in pts],
        columns=["geometry"],
        crs={"init": "epsg:4326"},
    )
    return gdf


def make_poly_in_gdf():
    """ Bounding box polygon. """
    poly_inters = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
    gdf = gpd.GeoDataFrame(
        [1], geometry=[poly_inters], crs={"init": "epsg:4326"}
    )
    return gdf


def make_locs_buff():
    """ Buffer points to create multi poly. """
    buffered_locations = make_locs_gdf()
    buffered_locations["geometry"] = buffered_locations.buffer(4)
    return buffered_locations


def make_donut_geom():
    """ Make a donut geometry. """
    donut = gpd.overlay(
        make_locs_buff(), make_poly_in_gdf(), how="symmetric_difference"
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
def poly_in_gdf():
    """ Fixture for a bounding box polygon. """
    return make_poly_in_gdf()


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
    return out_df


def test_not_gdf(poly_in_gdf):
    """Non-GeoDataFrame inputs raise attribute errors."""
    with pytest.raises(AttributeError):
        cl.clip_shp((2, 3), poly_in_gdf)
    with pytest.raises(AttributeError):
        cl.clip_shp(poly_in_gdf, (2, 3))


def test_returns_gdf(locs_gdf, poly_in_gdf):
    """Test that function returns a GeoDataFrame (or GDF-like) object."""
    out = cl.clip_shp(locs_gdf, poly_in_gdf)
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


def test_input_gdfs(poly_in_gdf):
    """Test that function fails if not provided with 2 GDFs."""
    with pytest.raises(AttributeError):
        cl.clip_shp(list(), poly_in_gdf)
    with pytest.raises(AttributeError):
        cl.clip_shp(poly_in_gdf, list())


def test_clip_points(locs_gdf, poly_in_gdf):
    """Test clipping a points GDF with a generic polygon geometry."""
    clip_pts = cl.clip_shp(locs_gdf, poly_in_gdf)
    assert len(clip_pts.geometry) == 3 and clip_pts.geom_type[1] == "Point"


def test_clip_poly(locs_buff, poly_in_gdf):
    """Test clipping a polygon GDF with a generic polygon geometry."""
    clipped_poly = cl.clip_shp(locs_buff, poly_in_gdf)
    assert len(clipped_poly.geometry) == 3
    assert clipped_poly.geom_type[1] == "Polygon"


def test_clip_multipoly(poly_in_gdf, multi_gdf):
    """Test that multi poly returns a value error."""
    with pytest.raises(ValueError):
        cl.clip_shp(poly_in_gdf, multi_gdf)


def test_clip_donut_poly(locs_gdf, donut_geom):
    """Donut holes are multipolygons and should raise ValueErrors."""
    with pytest.raises(ValueError):
        cl.clip_shp(locs_gdf, donut_geom)


def test_clip_lines(linez_gdf, poly_in_gdf):
    """Test what happens when you give the clip_extent a line GDF."""
    clip_line = cl.clip_shp(linez_gdf, poly_in_gdf)
    assert len(clip_line.geometry) == 2
