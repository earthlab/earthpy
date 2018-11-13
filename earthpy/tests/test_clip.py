"""Tests for the clip module."""

import numpy as np
import pytest
from shapely.geometry import Polygon, Point, LineString
import shapely
import geopandas as gpd
import earthpy.clip as cl


""" Setup dummy data for tests """

pts = np.array([[2, 2],
                [3, 4],
                [9, 8],
                [-12, -15]])

locs = [Point(xy) for xy in pts]
locs_gdf = gpd.GeoDataFrame(locs,
                            columns=['geometry'],
                            crs={'init': 'epsg:4326'})

# TODO? Create a create gdf from list function since we do it like 3
# times in this test file already


""" Create Line Objects For Testing """

linea = LineString([(1, 1), (2, 2), (3, 2), (5, 3)])
lineb = LineString([(3, 4), (5, 7), (12, 2), (10, 5), (9, 7.5)])

linez_gdf = gpd.GeoDataFrame([1, 2],
                             geometry=[linea, lineb],
                             crs={'init': 'epsg:4326'})

""" Create Polygon Objects For Testing """

# Create crop box
poly_inters = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
poly_in_gdf = gpd.GeoDataFrame([1],
                               geometry=[poly_inters],
                               crs={'init': 'epsg:4326'})

# Shift by 20
poly_out_gdf = poly_in_gdf.copy()
poly_out_gdf = poly_in_gdf.geometry.apply(lambda x: shapely.affinity.
                                          translate(x, xoff=20, yoff=20))
# Buffer points to create multi poly
locs_buff = locs_gdf.copy()
locs_buff["geometry"] = locs_gdf.buffer(4)

# Create geom w "donut hole"
donut_geom = gpd.overlay(locs_buff, poly_in_gdf,
                         how='symmetric_difference')

multi_poly = donut_geom.unary_union
multi_gdf = gpd.GeoDataFrame(gpd.GeoSeries(multi_poly),
                             crs={'init': 'epsg:4326'})
multi_gdf = multi_gdf.rename(columns={0: 'geometry'}).\
    set_geometry('geometry')



""" Run clip shape tests """


def test_returns_gdf():
    """Test that function returns a GeoDataFrame (or GDF-like) object."""
    out = cl.clip_shp(locs_gdf, poly_in_gdf)
    assert hasattr(out, 'geometry')


def test_non_overlapping_geoms():
    """Test that a bounding box returns error if the extents don't overlap"""
    with pytest.raises(ValueError):
        cl.clip_shp(locs_gdf, poly_out_gdf)


def check_input_gdfs():
    """Test that function fails if not provided with 2 GDFs."""
    with pytest.raises(AssertionError):
        cl.clip_shp(locs, poly_in_gdf)
    with pytest.raises(AssertionError):
        cl.clip_shp(poly_in_gdf, locs)


def test_clip_points():
    """Test clipping a points GDF with a generic polygon geometry."""
    clip_pts = cl.clip_shp(locs_gdf, poly_in_gdf)
    assert len(clip_pts.geometry) == 3 and clip_pts.geom_type[1] == "Point"


def test_clip_poly():
    """Test clipping a polygon GDF with a generic polygon geometry."""
    clipped_poly = cl.clip_shp(locs_buff, poly_in_gdf)
    assert len(clipped_poly.geometry) == 3
    assert clipped_poly.geom_type[1] == "Polygon"


# TODO same test for points and lines


def test_clip_multipoly():
    """Test that multi poly returns a value error."""
    with pytest.raises(ValueError):
        cl.clip_shp(poly_in_gdf, multi_gdf)


def test_clip_donut_poly():
    """Donut holes are multipolygons and should raise ValueErrors."""
    with pytest.raises(ValueError):
        cl.clip_shp(locs_gdf, donut_geom)


def test_clip_lines():
    """Test what happens when you give the clip_extent a line GDF."""
    clip_line = cl.clip_shp(linez_gdf, poly_in_gdf)
    assert len(clip_line.geometry) == 2
