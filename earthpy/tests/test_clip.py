"""Tests for the clip module."""

import pytest
import numpy as np
from shapely.geometry import Polygon, Point, LineString
import geopandas as gpd
import earthpy.clip as cl


@pytest.fixture
def point_gdf():
    """ Create a point GeoDataFrame. """
    pts = np.array([[2, 2], [3, 4], [9, 8], [-12, -15]])
    gdf = gpd.GeoDataFrame(
        [Point(xy) for xy in pts], columns=["geometry"], crs="epsg:4326",
    )
    return gdf


@pytest.fixture
def single_rectangle_gdf():
    """Create a single rectangle for clipping. """
    poly_inters = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
    gdf = gpd.GeoDataFrame([1], geometry=[poly_inters], crs="epsg:4326")
    gdf["attr2"] = "site-boundary"
    return gdf


@pytest.fixture
def two_line_gdf():
    """ Create Line Objects For Testing """
    linea = LineString([(1, 1), (2, 2), (3, 2), (5, 3)])
    lineb = LineString([(3, 4), (5, 7), (12, 2), (10, 5), (9, 7.5)])
    gdf = gpd.GeoDataFrame([1, 2], geometry=[linea, lineb], crs="epsg:4326")
    return gdf


@pytest.fixture
def multi_line(two_line_gdf):
    """Create a multi-line GeoDataFrame.

    This has one multi line and another regular line.
    """
    # Create a single and multi line object
    multiline_feat = two_line_gdf.unary_union
    linec = LineString([(2, 1), (3, 1), (4, 1), (5, 2)])
    out_df = gpd.GeoDataFrame(
        geometry=gpd.GeoSeries([multiline_feat, linec]), crs="epsg:4326",
    )
    out_df = out_df.rename(columns={0: "geometry"}).set_geometry("geometry")
    out_df["attr"] = ["road", "stream"]
    return out_df


@pytest.fixture
def multi_point(point_gdf):
    """ Create a multi-point GeoDataFrame. """
    multi_point = point_gdf.unary_union
    out_df = gpd.GeoDataFrame(
        gpd.GeoSeries(
            [multi_point, Point(2, 5), Point(-11, -14), Point(-10, -12)]
        ),
        crs="epsg:4326",
    )
    out_df = out_df.rename(columns={0: "geometry"}).set_geometry("geometry")
    out_df["attr"] = ["tree", "another tree", "shrub", "berries"]
    return out_df


def test_warning_main_clip_function(point_gdf, single_rectangle_gdf):
    with pytest.raises(Warning, match="clip_shp is deprecated in earthpy"):
        cl.clip_shp(point_gdf, single_rectangle_gdf)


def test_warning_multi_line_clip_function(multi_line, single_rectangle_gdf):
    with pytest.raises(
        Warning,
        match="_clip_multi_poly_line is deprecated. Use the "
        "_clip_line_poly()",
    ):
        cl._clip_multi_poly_line(multi_line, single_rectangle_gdf)


def test_warning_line_clip_function(two_line_gdf, single_rectangle_gdf):
    with pytest.raises(
        Warning,
        match="_clip_line_poly is deprecated. Use the _clip_line_poly()",
    ):
        cl._clip_line_poly(two_line_gdf, single_rectangle_gdf)


def test_warning_mutli_point_clip_function(multi_point, single_rectangle_gdf):
    with pytest.raises(
        Warning,
        match="_clip_multi_point is deprecated. Use the _clip_points()",
    ):
        cl._clip_multi_point(multi_point, single_rectangle_gdf)


def test_warning_point_clip_function(point_gdf, single_rectangle_gdf):
    with pytest.raises(
        Warning, match="_clip_points is deprecated. Use the _clip_points()",
    ):
        cl._clip_points(point_gdf, single_rectangle_gdf)
