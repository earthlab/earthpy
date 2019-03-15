import earthpy as et


def test_epsg():
    """Unit test for loading EPSG to Proj4 string dictionary."""

    epsg = et.epsg
    wgs84_proj4 = epsg["4326"]

    assert wgs84_proj4 == "+proj=longlat +datum=WGS84 +no_defs"
