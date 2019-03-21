""" Tests for io module. """

import os
import requests
import pytest
import numpy as np
import rasterio as rio
import geopandas as gpd
import earthpy.io as eio


@pytest.fixture
def eld(tmpdir):
    return eio.Data(path=tmpdir)


def test_invalid_datasets_raise_errors():
    """ Raise errors when users provide nonexistent datasets. """
    with pytest.raises(KeyError):
        eio.path_to_example("Non-existent dataset")


def test_missing_datasets_raise_errors():
    """ Raise errors when users forget to provide a dataset. """
    with pytest.raises(KeyError):
        eio.path_to_example("")


def test_valid_datasets_get_returned():
    """ If users give a valid dataset name, return a valid path. """
    epsg_path = eio.path_to_example("epsg.json")
    assert os.path.isfile(epsg_path)


def test_rgb():
    """ Check assumptions about rgb satellite imagery over RMNP. """
    with rio.open(eio.path_to_example("rmnp-rgb.tif")) as src:
        rgb = src.read()
        rgb_crs = src.crs
    assert rgb.shape == (3, 373, 485)
    assert str(rgb_crs) == rio.crs.CRS.from_epsg(4326)


def test_rgb_single_channels():
    """ Check assumptions about single channel R, G, and B images. """
    tif_names = [color + ".tif" for color in ["red", "green", "blue"]]
    fnames = [eio.path_to_example(f) for f in tif_names]
    rgb_parts = list()
    for f in fnames:
        with rio.open(f) as src:
            rgb_parts.append(src.read())
            assert str(src.crs) == rio.crs.CRS.from_epsg(4326)

    with rio.open(eio.path_to_example("rmnp-rgb.tif")) as src:
        assert np.array_equal(src.read(), np.concatenate(rgb_parts))


def test_colorado_counties():
    """ Check assumptions about county polygons. """
    counties = gpd.read_file(eio.path_to_example("colorado-counties.geojson"))
    assert counties.shape == (64, 13)
    assert counties.crs == {"init": "epsg:4326"}


def test_colorado_glaciers():
    """ Check assumptions about glacier point locations. """
    glaciers = gpd.read_file(eio.path_to_example("colorado-glaciers.geojson"))
    assert glaciers.shape == (134, 2)
    assert glaciers.crs == {"init": "epsg:4326"}


def test_continental_divide_trail():
    """ Check assumptions about Continental Divide Trail path. """
    cdt = gpd.read_file(eio.path_to_example("continental-div-trail.geojson"))
    assert cdt.shape == (1, 2)
    assert cdt.crs == {"init": "epsg:4326"}


""" Tests for the EarthlabData class. """

eio.DATA_URLS["little-text-file"] = [
    ("https://ndownloader.figshare.com/files/14555681", "abc.txt", "file")
]

eio.DATA_URLS["little-zip-file"] = [
    ("https://ndownloader.figshare.com/files/14555684", ".", "zip")
]


@pytest.mark.vcr()
def test_urls_are_valid():
    """ Test responses for each dataset to ensure valid URLs. """
    for key in eio.DATA_URLS:
        dataset = eio.DATA_URLS[key]
        if not isinstance(dataset, list):
            dataset = [dataset]
        for url, name, kind in dataset:
            r = requests.get("http://www.example.com")
            assert r.status_code == 200


def test_key_and_url_set_simultaneously(eld):
    """ Only key or url should be set, not both. """
    with pytest.raises(ValueError, match="can not both be set at the same"):
        eld.get_data(key="foo", url="bar")


def test_available_datasets_are_printed(eld, capsys):
    """ If no key or url provided, print datasets.

    The output that is printed should be identical to the __repr__ output.
    Using capsys in pytest provides a way to capture stdout/stderr output.

    """
    eld.get_data()
    printed_output = capsys.readouterr().out
    print(eld)
    repr_output = capsys.readouterr().out
    assert printed_output == repr_output


def test_invalid_dataset_key(eld):
    """ Raise errors for unknown dataset keys. """
    with pytest.raises(KeyError, match="not found in"):
        eld.get_data(key="some non-existent key")


@pytest.mark.vcr()
def test_valid_download_file(eld):
    """ Test that single files get downloaded. """
    file = eld.get_data("little-text-file")
    assert os.path.isfile(file)


@pytest.mark.vcr()
def test_valid_download_zip(eld):
    """ Test that zipped files get downloaded and extracted. """
    path = eld.get_data("little-zip-file")
    path_has_contents = len(os.listdir(path)) > 0
    assert path_has_contents


@pytest.mark.parametrize("replace_arg_value", [True, False])
@pytest.mark.vcr()
def test_replace_arg_controle_overwrite(eld, replace_arg_value):
    """ If replace=False, do not replace existing files. If true, replace. """
    file1 = eld.get_data("little-text-file")
    mtime1 = os.path.getmtime(file1)
    file2 = eld.get_data("little-text-file", replace=replace_arg_value)
    mtime2 = os.path.getmtime(file2)
    if replace_arg_value is True:
        assert mtime1 < mtime2
    else:
        assert mtime1 == mtime2


@pytest.mark.vcr()
def test_arbitrary_url_file_download(eld):
    """ Verify that arbitrary URLs work for data file downloads. """
    file = eld.get_data(url="http://www.google.com/robots.txt")
    assert os.path.isfile(file)


def test_invalid_data_type(eld):
    """ Raise errors for invalid data types. """
    eio.DATA_URLS["invalid-data-type"] = [
        ("https://www.google.com", ".", "an_invalid_file_extension")
    ]
    with pytest.raises(ValueError, match="kind must be one of"):
        eld.get_data("invalid-data-type")


@pytest.mark.vcr()
def test_arbitrary_url_zip_download(eld):
    """ Verify that aribitrary URLs work for zip file downloads. """
    path = eld.get_data(
        url="https://www2.census.gov/geo/tiger/GENZ2016/shp/cb_2016_us_nation_20m.zip"
    )
    path_has_contents = len(os.listdir(path)) > 0
    assert path_has_contents


@pytest.mark.vcr()
def test_url_download_tar_file(eld):
    """ Ensure that tar files are downloaded and extracted. """
    path = eld.get_data(url="https://ndownloader.figshare.com/files/14615411")
    assert "abc.txt" in os.listdir(path)


@pytest.mark.vcr()
def test_url_download_tar_gz_file(eld):
    """ Ensure that tar.gz files are downloaded and extracted. """
    path = eld.get_data(url="https://ndownloader.figshare.com/files/14615414")
    assert "abc.txt" in os.listdir(path)


@pytest.mark.vcr()
def test_url_download_txt_file_with_content_disposition(eld):
    """ Test arbitrary URL download with content-disposition. """
    path = eld.get_data(url="https://ndownloader.figshare.com/files/14555681")
    assert path.endswith("abc.txt") and os.path.isfile(path)


@pytest.mark.parametrize("verbose_arg_value", [True, False])
@pytest.mark.vcr()
def test_verbose_arg_works(eld, verbose_arg_value, capsys):
    """ Test that the verbose argument can print or suppress messages. """
    eld.get_data("little-text-file", verbose=verbose_arg_value)
    output_printed = capsys.readouterr().out != ""
    assert output_printed == verbose_arg_value
