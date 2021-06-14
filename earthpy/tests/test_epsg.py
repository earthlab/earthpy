import pytest
import rasterio as rio
import earthpy as et
import earthpy.spatial as es
from earthpy.io import path_to_example


def test_epsg():
    """Unit test for loading EPSG to Proj4 string dictionary."""

    assert et.epsg["4326"] == "+proj=longlat +datum=WGS84 +no_defs"


def test_crs_check_tif():
    """Test crs check works properly."""
    crs = es.crs_check(path_to_example("rmnp-rgb.tif"))
    assert(crs.to_epsg() == 4326)


def test_crs_check_bad_file():
    with pytest.raises(rio.errors.RasterioIOError):
        es.crs_check(path_to_example("rmnp.shp"))
