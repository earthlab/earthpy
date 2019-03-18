import earthpy as et


def test_epsg():
    """Unit test for loading EPSG to Proj4 string dictionary."""

    assert et.epsg["4326"] == "+proj=longlat +datum=WGS84 +no_defs"
