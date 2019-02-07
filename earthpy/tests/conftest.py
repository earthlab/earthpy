""" Utility functions for tests. """
import numpy as np
import pytest
from shapely.geometry import Polygon, Point, LineString
from affine import Affine
import rasterio as rio
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


@pytest.fixture
def basic_geometry():
    """
    A square polygon spanning (2, 2) to (4.25, 4.25) in x and y directions
    Borrowed from rasterio/tests/conftest.py

    Returns
    -------
    dict: GeoJSON-style geometry object.
        Coordinates are in grid coordinates (Affine.identity()).
    """
    return Polygon([(2, 2), (2, 4.25), (4.25, 4.25), (4.25, 2), (2, 2)])


@pytest.fixture
def basic_geometry_gdf(basic_geometry):
    """
    A GeoDataFrame containing the basic geometry

    Returns
    -------
    GeoDataFrame containing the basic_geometry polygon
    """
    gdf = gpd.GeoDataFrame(
        geometry=[basic_geometry], crs={"init": "epsg:4326"}
    )
    return gdf


@pytest.fixture
def basic_image():
    """
    A 10x10 array with a square (3x3) feature
    Equivalent to results of rasterizing basic_geometry with all_touched=True.
    Borrowed from rasterio/tests/conftest.py

    Returns
    -------
    numpy ndarray
    """
    image = np.zeros((10, 10), dtype=np.uint8)
    image[2:5, 2:5] = 1
    return image


@pytest.fixture
def basic_image_tif(tmpdir, basic_image):
    """
    A GeoTIFF representation of the basic_image array.
    Borrowed from rasterio/tests/conftest.py

    Returns
    -------
    string path to raster file
    """
    outfilename = str(tmpdir.join("basic_image.tif"))
    kwargs = {
        "crs": rio.crs.CRS({"init": "epsg:4326"}),
        "transform": Affine.identity(),
        "count": 1,
        "dtype": rio.uint8,
        "driver": "GTiff",
        "width": basic_image.shape[1],
        "height": basic_image.shape[0],
        "nodata": None,
    }
    with rio.open(outfilename, "w", **kwargs) as out:
        out.write(basic_image, indexes=1)
    return outfilename


@pytest.fixture
def image_array_2bands():
    return np.random.randint(10, size=(2, 4, 5))


@pytest.fixture
def one_band_3dims():
    return np.random.randint(10, size=(1, 4, 5))
