"""
earthpy.project
==========

Directory management for data projects

"""

import os
import json
import configparser
from pathlib import Path
from platformdirs import user_data_dir, user_config_dir

class Project:
    """
    Manage a project data directory.

    This class resolves a user-specific data directory using
    `platformdirs`, environment variables, or configuration files.
    It then creates a named subdirectory for storing project data.

    Parameters
    ----------
    appname : str, optional
        Application name for directory naming. Defaults to "data".

    appauthor : str, optional
        Author or organization name. Defaults to "earth-analytics".

    project_dirname : str, optional
        Name of the subdirectory to store project data inside the
        data home. Defaults to "earthpy-downloads".

    env_var : str, optional
        Environment variable to override the data home location.
        Defaults to "EARTHPY_DATA_HOME".

    Attributes
    ----------
    data_home : pathlib.Path
        Resolved base directory for storing user-specific data.

    project_dir : pathlib.Path
        Subdirectory inside `data_home` for storing project data.

    Examples
    --------
    >>> project = Project()
    >>> print(project.data_home)
    /home/user/.local/share/earth-analytics/data
    >>> print(project.project_dir)
    /home/user/.local/share/earth-analytics/data/earthpy-downloads
    """

    def __init__(
        self,
        appname="earth-analytics",
        project_dirname="earthpy-downloads",
        env_var="EARTHPY_DATA_HOME"
    ):
        self.appname = appname
        self.project_dirname = project_dirname
        self.env_var = env_var

        self.data_home = self._resolve_data_home()
        self.project_dir = self.data_home / self.project_dirname

        self.data_home.mkdir(parents=True, exist_ok=True)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        os.environ[self.env_var] = str(self.data_home)
        os.environ["EARTHPY_DATA_PROJECT_DIR"] = str(self.project_dir)

    def _resolve_data_home(self) -> Path:
        """
        Resolve the user data directory with priority:
        1. Environment variable
        2. Local config file
        3. Global config file
        4. platformdirs default

        Returns
        -------
        pathlib.Path
            The resolved data home path.
        """
        # Environment variable override
        if self.env_var in os.environ:
            return Path(os.environ[self.env_var]).expanduser().resolve()

        # Look for local config file
        local_config = self._find_config_file(Path.cwd())
        if local_config:
            return local_config

        # Look for global config file
        config_dir = Path(
            user_config_dir(self.appname)
        ).expanduser()
        global_config = self._find_config_file(config_dir)
        if global_config:
            return global_config

        # Fallback to platformdirs default
        return Path(
            user_data_dir(self.appname)
        ).expanduser().resolve()

    def _find_config_file(self, directory: Path) -> Path | None:
        """
        Search for a JSON or INI config file in a given directory.

        Parameters
        ----------
        directory : Path
            Directory to search for a config file.

        Returns
        -------
        Path or None
            Path to resolved data home if config found, else None.
        """
        for ext in [".json", ".ini"]:
            path = directory / f"earthpy_config{ext}"
            if not path.exists():
                continue
            try:
                if ext == ".json":
                    with open(path) as f:
                        cfg = json.load(f)
                    if "data_home" in cfg:
                        return Path(cfg["data_home"]).expanduser().resolve()
                elif ext == ".ini":
                    parser = configparser.ConfigParser()
                    parser.read(path)
                    if (
                        parser.has_section("data")
                        and parser.has_option("data", "home")
                    ):
                        return Path(
                            parser.get("data", "home")
                        ).expanduser().resolve()
            except Exception as e:
                print(f"[Warning] Failed to read {path}: {e}")
        return None
