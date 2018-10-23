import earthpy.spatial as es
from shapely.geometry import Polygon, Point
import geopandas as gpd
import pandas as pd
import pytest


def test_extent_to_json():
    """"Unit tests for extent_to_json()."""
    # giving a list [minx, miny, maxx, maxy] makes a polygon
    list_out = es.extent_to_json([0, 0, 1, 1])
    assert list_out['type'] == 'Polygon'

    # the polygon is the unit square
    list_poly = Polygon(list_out['coordinates'][0])
    assert list_poly.area == 1
    assert list_poly.length == 4

    # providing a GeoDataFrame creates identical output
    df = pd.DataFrame(
        {'lat': [0, 1],
         'lon': [0, 1]}
    )
    df['coords'] = list(zip(df.lon, df.lat))
    df['coords'] = df['coords'].apply(Point)
    gdf = gpd.GeoDataFrame(df, geometry='coords')
    gdf_out = es.extent_to_json(gdf)
    assert gdf_out == list_out

    # giving non-list or GeoDataFrame input raises a ValueError
    with pytest.raises(ValueError):
        es.extent_to_json({'a': 'dict'})
