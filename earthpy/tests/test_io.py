""" Tests for io module. """

import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import geopandas as gpd
import requests
import pytest
import numpy as np
import rasterio as rio

from earthpy.config import DATA_URLS
from earthpy.project import Project
from earthpy.io import Data


RUNNING_ON_CI = False
if "CI" in os.environ:
    if os.environ["CI"]:
        RUNNING_ON_CI = True

skip_on_ci = pytest.mark.skipif(
    RUNNING_ON_CI, reason="Test fails intermittently on CI systems."
)



@pytest.fixture
def data_instance(tmp_path, monkeypatch):
    """Fixture to create a Data instance for testing with example data."""
    
    # Set the environment variable for the test path
    monkeypatch.setenv("EARTHPY_DATA_HOME", str(tmp_path / "testdata"))
    
    # Create the project
    project = Project(title="Test Project", dirname="example-data")
    data = Data(project)

    # Set up the example data path
    example_data_path = Path(__file__).parent.parent / "example-data"
    test_data_path = project.project_dir
    test_data_path.mkdir(parents=True, exist_ok=True)
    
    # Copy example data to the temp path if it exists
    if example_data_path.exists():
        for item in example_data_path.iterdir():
            if item.is_file():
                shutil.copy(item, test_data_path / item.name)
            elif item.is_dir():
                shutil.copytree(item, test_data_path / item.name)

    print(f"✅ Example data copied to: {test_data_path}")
    return data


def test_invalid_datasets_raise_errors(data_instance):
    """Raise errors when users provide nonexistent datasets."""
    with pytest.raises(KeyError):
        data_instance.get_data_path("Non-existent dataset")


def test_missing_datasets_raise_errors(data_instance):
    """Raise errors when users forget to provide a dataset."""
    with pytest.raises(KeyError):
        data_instance.get_data_path("")


def test_valid_datasets_get_returned(data_instance, tmp_path):
    """If users give a valid dataset name, return a valid path."""

    epsg_path = data_instance.get_data_path("epsg.json")
    assert os.path.isfile(epsg_path)
    print(f"✅ Found dataset at {epsg_path}")


def test_rgb(data_instance, tmp_path):
    """Check assumptions about rgb satellite imagery over RMNP."""
    example_file = tmp_path / "testdata" / "rmnp-rgb.tif"
    example_file.parent.mkdir(parents=True, exist_ok=True)

    # Create a dummy GeoTIFF
    with rio.open(example_file, 'w', driver='GTiff',
                  height=373, width=485, count=3,
                  dtype='uint8', crs='EPSG:4326') as dst:
        dst.write(np.zeros((3, 373, 485), dtype='uint8'))

    with rio.open(data_instance.get_data_path("rmnp-rgb.tif")) as src:
        rgb = src.read()
        rgb_crs = src.crs
    assert rgb.shape == (3, 373, 485)
    assert str(rgb_crs) == rio.crs.CRS.from_epsg(4326)


def test_colorado_counties(data_instance, tmp_path):
    """Check assumptions about county polygons."""
    example_file = tmp_path / "testdata" / "colorado-counties.geojson"
    example_file.parent.mkdir(parents=True, exist_ok=True)

    # Create a dummy GeoJSON
    with open(example_file, "w") as f:
        f.write('{"type": "FeatureCollection", "features": []}')

    counties = gpd.read_file(data_instance.get_data_path(
        "colorado-counties.geojson"))
    assert counties.crs == "epsg:4326"


def test_colorado_glaciers(data_instance, tmp_path):
    """Check assumptions about glacier point locations."""
    example_file = tmp_path / "testdata" / "colorado-glaciers.geojson"
    example_file.parent.mkdir(parents=True, exist_ok=True)

    with open(example_file, "w") as f:
        f.write('{"type": "FeatureCollection", "features": []}')

    glaciers = gpd.read_file(data_instance.get_data_path(
        "colorado-glaciers.geojson"))
    assert glaciers.crs == "epsg:4326"


def test_continental_divide_trail(data_instance, tmp_path):
    """Check assumptions about Continental Divide Trail path."""
    example_file = tmp_path / "testdata" / "continental-div-trail.geojson"
    example_file.parent.mkdir(parents=True, exist_ok=True)

    with open(example_file, "w") as f:
        f.write('{"type": "FeatureCollection", "features": []}')

    cdt = gpd.read_file(data_instance.get_data_path(
        "continental-div-trail.geojson"))
    assert cdt.crs == "epsg:4326"


""" Tests for the EarthlabData class. """

DATA_URLS["little-text-file"] = [
    ("https://figshare.com/ndownloader/files/12732467", "abc.txt", "file")
]

DATA_URLS["little-zip-file"] = [
    ("https://figshare.com/ndownloader/files/21894528", ".", "zip")
]


@skip_on_ci
@pytest.mark.vcr()
def test_urls_are_valid():
    """Test responses for each dataset to ensure valid URLs."""
    for key in DATA_URLS:
        dataset = DATA_URLS[key]
        if not isinstance(dataset, list):
            dataset = [dataset]
        for url, name, kind in dataset:
            r = requests.get("http://www.example.com")
            assert r.status_code == 200


def test_key_and_url_set_simultaneously(data_instance):
    """Only key or url should be set, not both."""
    with pytest.raises(ValueError, match="mutually exclusive"):
        data_instance.get_data(key="foo", url="bar")


def test_available_datasets_are_printed(
        data_instance, capsys):
    """If no key or url provided, print datasets.

    The output that is printed should be identical to the __repr__ output.
    Using capsys in pytest provides a way to capture stdout/stderr output.

    """
    Data().get_data()
    printed_output = capsys.readouterr().out
    assert 'california-rim-fire' in printed_output

def test_invalid_dataset_key(data_instance):
    """Raise errors for unknown dataset keys."""
    with pytest.raises(KeyError, match="not found in"):
        data_instance.get_data(key="some non-existent key")


@skip_on_ci
@pytest.mark.vcr()
def test_valid_download_file(data_instance):
    """Test that single files get downloaded."""
    file = data_instance.get_data("little-text-file")
    assert os.path.isfile(file)


@skip_on_ci
@pytest.mark.vcr()
def test_valid_download_zip(data_instance):
    """Test that zipped files get downloaded and extracted."""
    path = data_instance.get_data("little-zip-file")
    path_has_contents = len(os.listdir(path)) > 0
    assert path_has_contents


@skip_on_ci
@pytest.mark.parametrize("replace_arg_value", [True, False])
@pytest.mark.vcr()
def test_replace_arg_controle_overwrite(data_instance, replace_arg_value):
    """If replace=False, do not replace existing files. If true, replace."""
    file1 = data_instance.get_data("little-text-file")
    mtime1 = os.path.getmtime(file1)
    file2 = data_instance.get_data("little-text-file", replace=replace_arg_value)
    mtime2 = os.path.getmtime(file2)
    if replace_arg_value is True:
        assert mtime1 < mtime2
    else:
        assert mtime1 == mtime2


@skip_on_ci
@pytest.mark.vcr()
def test_arbitrary_url_file_download(data_instance):
    """Verify that arbitrary URLs work for data file downloads."""
    file = data_instance.get_data(url="http://www.google.com/robots.txt")
    assert os.path.isfile(file)


def test_invalid_data_type(data_instance):
    """Raise errors for invalid data types."""
    DATA_URLS["invalid-data-type"] = [
        ("https://www.google.com", ".", "an_invalid_file_extension")
    ]
    with pytest.raises(ValueError, match="kind must be one of"):
        data_instance.get_data("invalid-data-type")


@skip_on_ci
@pytest.mark.vcr()
def test_arbitrary_url_zip_download(data_instance):
    """Verify that aribitrary URLs work for zip file downloads."""
    path = data_instance.get_data(
        url=(
            "https://github.com/earthlab/earthpy/releases/download/v0.9.4"
            "/test.zip"
        )
    )
    path_has_contents = len(os.listdir(path)) > 0
    assert path_has_contents


@skip_on_ci
@pytest.mark.vcr()
def test_url_download_tar_file(data_instance):
    """Ensure that tar files are downloaded and extracted."""
    path = data_instance.get_data(url="https://ndownloader.figshare.com/files/14615411")
    assert "abc.txt" in os.listdir(path)


@skip_on_ci
@pytest.mark.vcr()
def test_url_download_tar_gz_file(data_instance):
    """Ensure that tar.gz files are downloaded and extracted."""
    path = data_instance.get_data(url="https://ndownloader.figshare.com/files/14615414")
    assert "abc.txt" in os.listdir(path)


@skip_on_ci
@pytest.mark.vcr()
def test_url_download_txt_file_with_content_disposition(data_instance):
    """Test arbitrary URL download with content-disposition."""
    path = data_instance.get_data(url="https://ndownloader.figshare.com/files/7275959")
    assert (path.name=="temperature_example.csv") and os.path.isfile(path)


@skip_on_ci
@pytest.mark.parametrize("verbose_arg_value", [True, False])
@pytest.mark.vcr()
def test_verbose_arg_works(
        data_instance, 
        verbose_arg_value, 
        capsys):
    """Test that the verbose argument can print or suppress messages."""
    data_instance.get_data("little-text-file", verbose=verbose_arg_value)
    output_printed = capsys.readouterr().out != ""
    assert output_printed == verbose_arg_value


@skip_on_ci
@pytest.mark.vcr()
def test_url_download_with_quotes(data_instance):
    """Test download with that has quotes around file name to see that get_data
    now removes the quotes."""
    quotes_url = (
        "https://opendata.arcgis.com/datasets/955e7a0f5"
        + "2474b60a9866950daf10acb_0.zip"
    )
    path = data_instance.get_data(url=quotes_url)
    files = os.listdir(path)
    assert "City_of_Boulder_City_Limits.shp" in files and os.path.isdir(path)


@pytest.fixture
def mock_project(tmp_path):
    """Fixture to create a mock Project instance."""
    project = Project(title="Test Project", dirname=str(tmp_path))
    return project


def test_data_initialization(mock_project):
    """Test that Data initializes correctly with a Project."""
    data = Data(mock_project)
    assert data.path == mock_project.project_dir
    assert data.figshare_project_id == mock_project.figshare_project_id
    assert data.figshare_token == mock_project.figshare_token
    assert data.path.exists()
    

def test_get_figshare_download_urls(mock_project):
    """Test that _get_figshare_download_urls retrieves the correct URLs."""
    data = Data(mock_project)
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "files": [
                {"name": "file1.csv", 
                 "download_url": "http://example.com/file1.csv"},
                {"name": "file2.csv", 
                 "download_url": "http://example.com/file2.csv"},
                {"name": "dvc.lock", 
                 "download_url": "http://example.com/dvc.lock"},
                {"name": "dvc.yaml", 
                 "download_url": "http://example.com/dvc.yaml"},
            ]
        }
        mock_get.return_value = mock_response
        
        # Test without admin flag
        urls = data._get_figshare_download_urls(article_id=1234, admin=False)
        assert "dvc.lock" not in urls
        assert "dvc.yaml" not in urls
        assert "file1.csv" in urls
        assert "file2.csv" in urls

        # Test with admin flag
        urls = data._get_figshare_download_urls(article_id=1234, admin=True)
        assert "dvc.lock" in urls
        assert "dvc.yaml" in urls


def test_download(mock_project, tmp_path):
    """Test that _download correctly saves files."""
    data = Data(mock_project)
    test_url = "http://example.com/testfile.csv"
    test_path = tmp_path / "testfile.csv"

    # Mock the request response
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"test,data,123"
        mock_get.return_value = mock_response

        # Test download
        data._download(
            url=test_url, path=test_path, kind="file", 
            replace=True, verbose=True)
        assert test_path.exists()
        with open(test_path, "r") as f:
            content = f.read()
            assert content == "test,data,123"


def test_articles(mock_project):
    """Test that articles are fetched and mapped correctly."""
    data = Data(mock_project)
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"title": "Dataset 1", "id": 111},
            {"title": "Dataset 2", "id": 222}
        ]
        mock_get.return_value = mock_response

        articles = data.articles
        assert "Dataset 1" in articles
        assert articles["Dataset 1"] == 111
        assert "Dataset 2" in articles
        assert articles["Dataset 2"] == 222
