""" Tests for the extent_to_json function """


import pandas as pd
import pytest
import geopandas as gpd
from shapely.geometry import Polygon, Point
import earthpy.spatial as es


@pytest.fixture
def list_out():
    """ A JSON extent on the unit square spanning (0, 0), (1, 1). """
    return es.extent_to_json([0, 0, 1, 1])


@pytest.mark.parametrize(
    "list_input,error",
    [
        ([1, 0, 0, 1], "xmin must be <= xmax"),
        ([0, 1, 1, 0], "ymin must be <= ymax"),
    ],
)
def test_min_exceeds_max(list_input, error):
    """Min value that exceeds max raises error for both x and y coords"""

    with pytest.raises(AssertionError, match=error):
        es.extent_to_json(list_input)


def test_list_format_works(list_out):
    """" Giving a list [minx, miny, maxx, maxy] makes a polygon"""
    assert list_out["type"] == "Polygon"


def test_polygon_is_square(list_out):
    """The polygon is the unit square"""

    list_poly = Polygon(list_out["coordinates"][0])
    assert list_poly.area == 1
    assert list_poly.length == 4


def test_gdf_format_works(list_out):
    """ Providing a GeoDataFrame creates returns expected vals"""

    points_df = pd.DataFrame({"lat": [0, 1], "lon": [0, 1]})
    points_df["coords"] = list(zip(points_df.lon, points_df.lat))
    points_df["coords"] = points_df["coords"].apply(Point)
    gdf = gpd.GeoDataFrame(points_df, geometry="coords")
    gdf_out = es.extent_to_json(gdf)
    assert gdf_out == list_out


def test_not_a_list():
    """Providing a non-list or GeoDataFrame input raises a ValueError"""

    with pytest.raises(ValueError):
        es.extent_to_json({"a": "dict"})
