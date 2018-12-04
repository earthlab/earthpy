"""Tests for the clip module."""

import pytest
from shapely.geometry import Polygon
import shapely
import geopandas as gpd
import earthpy.clip as cl


def test_not_gdf(poly_in_gdf):
    """Non-GeoDataFrame inputs raise attribute errors."""
    with pytest.raises(AttributeError):
        cl.clip_shp((2, 3), poly_in_gdf)
    with pytest.raises(AttributeError):
        cl.clip_shp(poly_in_gdf, (2, 3))


def test_returns_gdf(locs_gdf, poly_in_gdf):
    """Test that function returns a GeoDataFrame (or GDF-like) object."""
    out = cl.clip_shp(locs_gdf, poly_in_gdf)
    assert hasattr(out, 'geometry')


def test_non_overlapping_geoms():
    """Test that a bounding box returns error if the extents don't overlap"""
    unit_box = Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)])
    unit_gdf = gpd.GeoDataFrame([1],
                                geometry=[unit_box],
                                crs={'init': 'epsg:4326'})
    non_overlapping_gdf = unit_gdf.copy()
    non_overlapping_gdf = unit_gdf.geometry.apply(lambda x: shapely.affinity.
                                                  translate(x, xoff=20))
    with pytest.raises(ValueError):
        cl.clip_shp(unit_gdf, non_overlapping_gdf)


def check_input_gdfs(poly_in_gdf):
    """Test that function fails if not provided with 2 GDFs."""
    with pytest.raises(AssertionError):
        cl.clip_shp(list(), poly_in_gdf)
    with pytest.raises(AssertionError):
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


# TODO same test for points and lines


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
