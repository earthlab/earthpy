import os
import json
import configparser
from pathlib import Path

import pytest
from platformdirs import user_config_dir, user_data_dir

from earthpy.project import Project

@pytest.fixture
def clear_env(monkeypatch):
    monkeypatch.delenv("EARTHPY_DATA_HOME", raising=False)
    monkeypatch.delenv("EARTHPY_DATA_PROJECT_DIR", raising=False)

@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path

def test_default_behavior(fake_home, clear_env, monkeypatch):
    monkeypatch.setenv("HOME", str(fake_home))

    project = Project()
    expected = Path(
        user_data_dir("data", "earth-analytics")
    ).expanduser() / "earthpy-downloads"

    assert project.project_dir == expected
    assert expected.exists()

def test_env_override(monkeypatch, tmp_path, clear_env):
    override_path = tmp_path / "custom_data"
    monkeypatch.setenv("EARTHPY_DATA_HOME", str(override_path))
    project = Project()
    assert project.data_home == override_path
    assert project.project_dir == override_path / "earthpy-downloads"
    assert os.environ["EARTHPY_DATA_HOME"] == str(project.data_home)
    assert os.environ["EARTHPY_DATA_PROJECT_DIR"] == str(
        project.project_dir
    )

def test_local_json_config(tmp_path, monkeypatch, clear_env):
    config_path = tmp_path / "earthpy_config.json"
    custom_path = tmp_path / "json_home"
    config_path.write_text(json.dumps({"data_home": str(custom_path)}))
    monkeypatch.chdir(tmp_path)

    project = Project()
    assert project.data_home == custom_path.resolve()
    assert project.project_dir == custom_path / "earthpy-downloads"

def test_local_ini_config(tmp_path, monkeypatch, clear_env):
    config_path = tmp_path / "earthpy_config.ini"
    custom_path = tmp_path / "ini_home"
    parser = configparser.ConfigParser()
    parser["data"] = {"home": str(custom_path)}
    with open(config_path, "w") as f:
        parser.write(f)

    monkeypatch.chdir(tmp_path)
    project = Project()
    assert project.data_home == custom_path.resolve()
    assert project.project_dir == custom_path / "earthpy-downloads"

def test_global_config_fallback(tmp_path, monkeypatch, clear_env):
    monkeypatch.setenv("HOME", str(tmp_path))

    # Correct config path using platformdirs
    config_dir = Path(user_config_dir("data", "earth-analytics")).expanduser()
    config_dir.mkdir(parents=True)
    config_path = config_dir / "earthpy_config.json"

    fallback_path = tmp_path / "global_config_data"
    config_path.write_text(json.dumps({"data_home": str(fallback_path)}))

    project = Project()
    assert project.data_home == fallback_path.resolve()
    assert project.project_dir == fallback_path / "earthpy-downloads"

def test_project_dirname_override(tmp_path, monkeypatch, clear_env):
    monkeypatch.setenv("HOME", str(tmp_path))
    project = Project(project_dirname="alt-downloads")
    assert project.project_dir.name == "alt-downloads"
    assert project.project_dir.exists()
