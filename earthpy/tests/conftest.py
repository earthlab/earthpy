""" Utility functions for tests. """
import numpy as np
import pytest
from shapely.geometry import Polygon, Point, LineString
import geopandas as gpd


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
