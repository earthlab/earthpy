import pandas as pd
import numpy as np
import pytest
from shapely.geometry import Polygon, Point, LineString
import shapely
import geopandas as gpd
import earthpy.spatial as es
import earthpy.clip as cl


def test_extent_to_json():
    """"Unit tests for extent_to_json()."""
    # Giving a list [minx, miny, maxx, maxy] makes a polygon
    list_out = es.extent_to_json([0, 0, 1, 1])
    assert list_out['type'] == 'Polygon'

    # The polygon is the unit square
    list_poly = Polygon(list_out['coordinates'][0])
    assert list_poly.area == 1
    assert list_poly.length == 4

    # Providing a GeoDataFrame creates identical output
    df = pd.DataFrame(
        {'lat': [0, 1],
         'lon': [0, 1]}
    )
    df['coords'] = list(zip(df.lon, df.lat))
    df['coords'] = df['coords'].apply(Point)
    gdf = gpd.GeoDataFrame(df, geometry='coords')
    gdf_out = es.extent_to_json(gdf)
    assert gdf_out == list_out

    # Giving non-list or GeoDataFrame input raises a ValueError
    with pytest.raises(ValueError):
        es.extent_to_json({'a': 'dict'})

    # Giving minima that exceed maxima raises an error for both x and y coords
    with pytest.raises(AssertionError):
        es.extent_to_json([1, 0, 0, 1])

    with pytest.raises(AssertionError):
        es.extent_to_json([0, 1, 1, 0])


# Create points GDF
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


############## LINE OBJECTS #######

linea = LineString([(1, 1), (2, 2), (3, 2), (5, 3)])
lineb = LineString([(3, 4), (5, 7), (12, 2), (10, 5), (17, 17)])

linez_gdf = gpd.GeoDataFrame([1, 2],
                             geometry=[linea, lineb],
                             crs={'init': 'epsg:4326'})

############## POLY OBJECTS ################

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

# LINE OBJECTS

def test_non_overlapping_geoms():
    """Test that a bounding box returns error if the extents don't overlap"""
    with pytest.raises(ValueError):
        cl.clip_shp(locs_gdf, poly_out_gdf)

def returns_gdf():
    """Test that function is provided 2 GDFs """
    with pytest.raises(AssertionError):
        cl.clip_shp(locs, poly_in_gdf)

def test_clip_points():
    """Test clipping a points GDF with a generic polygon geometry."""
    clipped = cl.clip_shp(locs_gdf, poly_in_gdf)
    assert len(clipped.geometry) == 6 and clipped.geom_type[1] == "Point"

def test_clip_poly():
    """Test clipping a polygon GDF with a generic polygon geometry."""
    clipped_poly = cl.clip_shp(locs_buff, poly_in_gdf)
    assert len(clipped_poly.geometry) == 6 and \
           clipped_poly.geom_type[1] == "Polygon"

def test_clip_multipoly():
    """Test clipping a polygon with a multi-polygon geometry"""

    clipped_multi = cl.clip_shp(poly_in_gdf, multi_gdf)
    assert len(clipped_multi.geometry) == 6 and clipped_multi.geom_type[
            1] == "MultiPolygon"

def test_clip_multipoly():
    """Test what happens with a clip when a donut hole topology is used to
    clip points"""

    clipz = cl.clip_shp(locs_gdf, donut_geom)
    assert len(clipz.geometry) == 1 and clipz.geom_type[
        1] == "Point"

def test_clip_lines():
    """Test what happens when you give the clip_extent a line GDF"""
    clipped_line = cl.clip_shp(linez_gdf, poly_in_gdf)
    assert len(clipped_line.geometry) == 6 and clipped_line.geom_type[
        1] == "LineString"
