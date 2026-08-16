import os
import pytest
from pathlib import Path
from platformdirs import user_data_dir

from earthpy.project import Project
from earthpy.io import Data

@pytest.fixture
def project():
    """Fixture for creating a temporary Project instance."""
    return Project(title="Test Project", 
                   dirname="test-downloads")


def test_directory_creation(project):
    """Test that the project and data directories are created."""
    assert project.data_home.exists()
    assert project.project_dir.exists()


def test_project_directory_naming(project):
    """Test that the project directory is named correctly."""
    expected_name = "test-downloads"
    assert project.project_dir.name == expected_name


def test_get_config_parameter_env_var(monkeypatch):
    """Test that environment variables override config files."""
    monkeypatch.setenv("EARTHPY_PROJECT_TITLE", "Env Project Title")
    project = Project()
    assert (
        project._get_config_parameter("project_title") 
        == "Env Project Title")


def test_get_config_parameter_config_file(monkeypatch, tmp_path):
    """Test that configuration is loaded from a local file."""
    # Create a mock configuration file
    config_file = tmp_path / "earthpy_config.json"
    config_file.write_text('{"project_title": "Config Project Title"}')
    
    # Switch to the temp directory and load the project
    monkeypatch.chdir(tmp_path)
    project = Project()
    assert (
        project._get_config_parameter("project_title") 
        == "Config Project Title")


def test_default_data_home():
    """Test that the default data home is set correctly."""
    project = Project()
    expected_data_home = Path(user_data_dir("earth-analytics"))
    assert project.data_home == expected_data_home


def test_default_figshare_project_id():
    """Test that the default Figshare project ID is set if not in config."""
    project = Project()
    assert project.figshare_project_id == "30926"


def test_invalid_config_file(monkeypatch, tmp_path):
    """Test that an invalid config file does not crash the loader."""
    # Create an invalid JSON configuration
    config_file = tmp_path / "earthpy_config.json"
    config_file.write_text('{"project_title": "Config Project Title" INVALID_JSON')
    
    # Switch to the temp directory and load the project
    monkeypatch.chdir(tmp_path)
    project = Project()
    assert project._get_config_parameter("project_title") is None

def test_get_data_cheyenne_river(monkeypatch, tmp_path):
    """Test the Cheyenne River Flood Frequency dataset download."""
    cr_project = Project(
        title="Cheyenne River Flood Frequency",
        dirname="cheyenne-river-flood-test")
    cr_project.get_data()
    
    # Assertions
    file_path = cr_project.project_dir / "cheyenne_streamflow_1934_2024.csv"
    assert Path(file_path).exists(), f"{file_path} was not downloaded successfully."
    print(f"✅ Downloaded successfully: {file_path}")
