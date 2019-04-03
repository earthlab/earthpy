""" Tests for the extent to json function """


import pandas as pd
import pytest
import geopandas as gpd
from shapely.geometry import Polygon, Point
import earthpy.spatial as es


def test_extent_to_json():
    """"Unit tests for extent_to_json()."""
    # Giving a list [minx, miny, maxx, maxy] makes a polygon
    list_out = es.extent_to_json([0, 0, 1, 1])
    assert list_out["type"] == "Polygon"

    # The polygon is the unit square
    list_poly = Polygon(list_out["coordinates"][0])
    assert list_poly.area == 1
    assert list_poly.length == 4

    # Providing a GeoDataFrame creates identical output
    points_df = pd.DataFrame({"lat": [0, 1], "lon": [0, 1]})
    points_df["coords"] = list(zip(points_df.lon, points_df.lat))
    points_df["coords"] = points_df["coords"].apply(Point)
    gdf = gpd.GeoDataFrame(points_df, geometry="coords")
    gdf_out = es.extent_to_json(gdf)
    assert gdf_out == list_out

    # Giving non-list or GeoDataFrame input raises a ValueError
    with pytest.raises(ValueError):
        es.extent_to_json({"a": "dict"})

    # Giving minima that exceed maxima raises an error for both x and y coords
    with pytest.raises(AssertionError):
        es.extent_to_json([1, 0, 0, 1])

    with pytest.raises(AssertionError):
        es.extent_to_json([0, 1, 1, 0])
