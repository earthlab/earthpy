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

def test_clip_funs():
    # Test that a bounding box returns error if the extents don't overlap
    with pytest.raises(ValueError):
        cl.clip_shp(locs_gdf, poly_out_gdf)

    # Test that function is provided 2 GDFs - quack
    with pytest.raises(AssertionError):
        cl.clip_shp(locs, poly_in_gdf)

    # Test that clip shape runs if extents do overlap
    # This code should run just fine -- how do i "test" that?
    # i dont love testing how many features are returned just in case we adjust the data in some way?
    # but i want to test that 1. there is a geometry col in the output and
    # 2. that 6 features are returned i suppose in this case
    # Technically if this runs below and passes clipped.geometry then it's a
    # GDF and it did run??
    clipped = cl.clip_shp(locs_gdf, poly_in_gdf)
    assert len(clipped.geometry) == 6 and clipped.geom_type[1] == "Point"

    clipped_poly = cl.clip_shp(locs_buff, poly_in_gdf)
    # Clip a poly with a poly - returns x num of features of type Polygon
    assert len(clipped_poly.geometry) == 6 and clipped_poly.geom_type[1] == "Polygon"

    # Clip a poly with a multi-poly - this should work (testing that all is in order)
    # Should i "try" these statements vs running them?
    clipped_multi = cl.clip_shp(poly_in_gdf, multi_gdf)
    assert len(clipped_multi.geometry) == 6 and clipped_multi.geom_type[
            1] == "MultiPolygon"

    # Test what happens with a clip when a donut hole topology is used
    clipz = cl.clip_shp(locs_gdf, donut_geom)
    assert len(clipz.geometry) == 1 and clipz.geom_type[
        1] == "Point"


    # Test what happens when you give the clip_extent a line
    clipped_line = cl.clip_shp(linez_gdf, poly_in_gdf)
    assert len(clipped_multi.geometry) == 6 and clipped_multi.geom_type[
        1] == "LineString"


    # Test what happens when you give the clip extent a perfectly straight
    # line so there is not technically a box the extent is a line
