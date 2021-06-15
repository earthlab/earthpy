import pytest
import rasterio as rio
import os.path as op
import earthpy as et
import earthpy.spatial as es
from earthpy.io import path_to_example

@pytest.fixture
def output_dir(out_path):
    return op.dirname(out_path)

def test_epsg():
    """Unit test for loading EPSG to Proj4 string dictionary."""

    assert et.epsg["4326"] == "+proj=longlat +datum=WGS84 +no_defs"


def test_crs_check_tif():
    """Test crs check works properly."""
    crs = es.crs_check(path_to_example("rmnp-rgb.tif"))
    assert(crs.to_epsg() == 4326)


def test_crs_check_bad_file():
    with pytest.raises(rio.errors.RasterioIOError, match="Oops, your data are"):
        es.crs_check(path_to_example("rmnp.shp"))


def test_no_crs_in_file(output_dir):
    output_path = op.join(output_dir, "no_crs.tif")

    with rio.open(et.io.path_to_example("green.tif")) as src:
        data = src.read(1)
        profile = src.profile
        profile.update(crs=None)

    with rio.open(output_path, 'w', **profile) as dst:
        dst.write(data, 1)

    with pytest.raises(ValueError, match="No CRS found in data. The raster "):
        es.crs_check(output_path)
