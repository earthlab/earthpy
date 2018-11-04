import pandas as pd
import numpy as np
import pytest
from shapely.geometry import Polygon, Point, LineString
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


# Create some data for testing clip operations
# prob a clip test file would be good?

# Create crop box
poly_inters = Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])
poly_no_inters = Polygon([(20, 20), (20, 30), (30, 30), (30, 20), (20, 20)])

# Create points GDF
pts = np.array([[2, 2],
                [3, 4],
                [9, 8],
                [-12, -15]])

locs = [Point(xy) for xy in pts]
locs_gdf = gpd.GeoDataFrame(locs,
                            columns=['geometry'],
                            crs={'init': 'epsg:4326'})

# Create a create points function since we do it like 3 times in this test file already

poly_out_gdf = gpd.GeoDataFrame(gpd.GeoSeries(poly_no_inters),
                   crs={'init': 'epsg:4326'})
poly_out_gdf = poly_out_gdf.rename(columns={0: 'geometry'}).\
    set_geometry('geometry')

poly_in_gdf = gpd.GeoDataFrame(gpd.GeoSeries(poly_inters),
                   crs={'init': 'epsg:4326'})
poly_in_gdf = poly_in_gdf.rename(columns={0: 'geometry'}).\
    set_geometry('geometry')

locs_buff = locs_gdf.copy()
locs_buff["geometry"] = locs_gdf.buffer(4)

# Create geom w "donut"
donut_geom = locs_buff.copy()
donut_geom["geometry"] = gpd.overlay(locs_buff, poly_in_gdf,
                         how='symmetric_difference')

# This creates a multi polygon but we need more points and bigger things to clip
# Want to then clip using the multi poly - this below creates on ebut need to converto gdf still

multi_poly = donut_geom.unary_union
multi_gdf = gpd.GeoDataFrame(gpd.GeoSeries(multi_poly),
                   crs={'init': 'epsg:4326'})
multi_gdf = multi_gdf.rename(columns={0: 'geometry'}).\
    set_geometry('geometry')





def test_clip_funs():
    # Test that a bounding box returns error if the extents don't overlap
    with pytest.raises(ValueError):
        cl.clip_shp(locs_gdf, poly_out_gdf)

    # Test that function is provided 2 GDFs - quack
    with pytest.raises(AssertionError):
        cl.clip_shp(locs, poly_in_gdf)

    # Test that clip shape runs if extents do overlap
    # This code should run just fine -- how do i "test" that?
    # Technically if this runs below and passes clipped.geometry then it's a
    # GDF and it did run??
    try:
        clipped = cl.clip_shp(locs_gdf, poly_in_gdf)
        clipped.geometry
    except:
        pass

    # Clip a poly with a poly - this should work (testing that all is in order)
    try:
        clipped = cl.clip_shp(locs_buff, poly_in_gdf)
        clipped.geometry
    except:
        pass

    # Clip a poly with a multi-poly - this should work (testing that all is in order)

    try:
        clipped_multi = cl.clip_shp(poly_in_gdf, multi_gdf)
        clipped_multi.geometry
    except:
        pass

    # Test what happens with a clip when a donut hole topology is used? this should work?



    # Test what happens when you give the clip_extent a line

    # Test what happens when you give the clip extent a perfectly straight
    # line so there is not technically a box the extent is a line
