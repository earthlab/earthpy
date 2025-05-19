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
from pprint import pprint

import requests
from dvc.repo import Repo

from .config import (
    DVCIGNORE,
    DVCIGNORE_TEMPLATE,
    DEFAULT_PROJECT_DIRNAME,
    DEFAULT_DATA_HOME,
    DEFAULT_FIGSHARE_PROJECT_ID,
)
from .io import Data

class Project:
    """
    Manage a project data directory.

    This class resolves a user-specific data directory using
    `platformdirs`, environment variables, or configuration files.
    It then creates a named subdirectory for storing project data.

    Parameters
    ----------
    title : str, optional
        Title of the project. If not provided, a default name is used.
    project_dirname : str, optional
        Name of the project directory, derived from the title if not
        provided. Default for title=None is "earthpy-downloads".
    appname : str, optional
        Name of the application. Default is "earth-analytics".
        This is used to determine the user-specific data directory.

    Attributes
    ----------
    data_home : Path
        The path to the user-specific data directory.
    project_dir : Path
        The path to the project-specific directory.
    config : dict
        Configuration parameters loaded from files.
    figshare_token : str
        Figshare API token for authentication.
    project_id : str
        Figshare project ID for uploading data.
    headers : dict
        Headers for Figshare API requests.
    data : Data
        Instance of the Data class for downloading data.
    title : str
        Title of the project.
    key : str
        Earthpy legacy dataset key for downloading data.
    figshare_project_id : str
        Figshare project ID for downloading data.
    figshare_token : str
        Figshare API token for downloading data.

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
        title=None, key=None,
        dirname=None,
        appname="earth-analytics",
    ):
        self.appname = appname
        self.config = self._load_config_files()
        self.title = title or self._get_config_parameter("project_title")
        self.key = key or self._get_config_parameter("earthpy_data_key")
        self.project_dirname = (
            dirname 
            or self._get_config_parameter("project_dirname")
            or title
            or DEFAULT_PROJECT_DIRNAME
        ).replace(" ", "-").lower()
        

        # Prepare directories
        self.data_home = Path(
            self._get_config_parameter("data_home")
            or user_data_dir(self.appname)
            or pathlib.Path.home() / "earth-analytics" / "data")
        self.project_dir = self.data_home / self.project_dirname

        self.data_home.mkdir(parents=True, exist_ok=True)
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Initialize DVC
        self._init_dvc()

        # Figshare API setup
        self.figshare_project_id = (
            self._get_config_parameter("figshare_project_id")
            or DEFAULT_FIGSHARE_PROJECT_ID)
        self.figshare_token = self._get_config_parameter("figshare_token")

        self.data = Data(project=self)

    def get_data(
            self, 
            key=None, url=None, title=None,
            filename=None,
            replace=False, verbose=True
        ):
        """
        Download data to project directory.

        Parameters
        ----------
        key : str, optional
            Figshare API key. If not provided, uses the class attribute.
        url : str, optional
            URL to download data from. If not provided, uses the class attribute.
        title : str, optional
            Title of the project. If not provided, uses the class attribute.
        filename : str, optional
            Name of the file to save the data as. If not provided, uses the class attribute.
        replace : bool, default False
            Whether to replace existing files.
        verbose : bool, default True
            Whether to print progress messages.

        Returns
        -------
        None
        """
        self.key = key or self.key
        self.title = title or self.title

        if self.key:
            self.data.get_data(
                key=self.key, replace=replace, verbose=verbose)
        if url:
            self.data.get_data(
                url=self.url, filename=filename, 
                replace=replace, verbose=verbose)
        if self.title:
            self.data.get_data(
                title=self.title, replace=replace, verbose=verbose)
            
        return
    
    def _read_config_file(self, file_path):
        """
        Read a configuration file into a dictionary.

        Supported formats: `.json`, `.ini`, `.yml`, and `.cfg`.

        Parameters
        ----------
        file_path : Path
            The path to the configuration file.

        Returns
        -------
        dict
            Parsed configuration data.
        """
        ext = file_path.suffix
        config_data = {}

        try:
            if ext == ".json":
                with open(file_path) as f:
                    config_data.update(json.load(f))
            elif ext == ".yml":
                with open(file_path) as f:
                    config_data.update(yaml.safe_load(f))
            elif ext in [".ini", ".cfg"]:
                parser = configparser.ConfigParser()
                parser.read(file_path)
                for section in parser.sections():
                    for key, value in parser.items(section):
                        config_data[f"{section}.{key}"] = value
        except Exception as e:
            print(f"[Warning] Failed to read {file_path}: {e}")
        
        return config_data

    def _load_config_files(self):
        """
        Load earthpy configuration files.

        This method searches for `earthpy_config.ext` in the current 
        working directory and the user configuration directory provided 
        by `platformdirs` and merges them into a single dictionary.
        If both are found, local configurations **override** global 
        configurations. Supported extensions are `.yml`, `.cfg`, 
        `.ini`, and `.json`, with duplicate parameters overridden in 
        that order.

        Returns
        -------
        dict
            Merged configuration dictionary.
        """
        # Paths to check
        local_config_dir = Path.cwd()
        global_config_dir = Path(user_config_dir(self.appname))

        # Supported extensions
        supported_exts = [".json", ".ini", ".cfg", ".yml"]

        # Local and global configuration files
        local_configs = {}
        global_configs = {}

        # 🔍 Search for files in both locations
        for ext in supported_exts:
            local_file = local_config_dir / f"earthpy_config{ext}"
            global_file = global_config_dir / f"earthpy_config{ext}"

            # Load local config if it exists
            if local_file.exists():
                print(f"Loading local configuration from {local_file}")
                local_configs.update(self._read_config_file(local_file))

            # Load global config if it exists
            if global_file.exists():
                print(f"Loading global configuration from {global_file}")
                global_configs.update(self._read_config_file(global_file))

        # Merge configurations, local values override global
        combined_config = {**global_configs, **local_configs}

        print("\n**Final Configuration Loaded:**")
        pprint(combined_config, sort_dicts=False, width=80)

        return combined_config
    
    def _get_config_parameter(self, param_name):
        """
        Retrieve a configuration parameter.

        This method checks if the parameter exists as an 
        environment variable with the `EARTHPY_` prefix 
        (case-insensitive). If not found, it searches the loaded 
        configuration files.

        Parameters
        ----------
        param_name : str
            The name of the parameter to search for.

        Returns
        -------
        str or None
            The value of the parameter if found, otherwise None.
        """
        # Environment variable check (case-insensitive)
        for key, value in os.environ.items():
            if key.lower() == f"EARTHPY_{param_name}".lower():
                print(f"Found '{param_name}' in environment variables.")
                return value

        # Configuration file check
        if param_name in self.config:
            print(f"Found '{param_name}' in configuration files.")
            return self.config[param_name]

        return None
    
    def _init_dvc(self):
        """
        Initialize DVC in the project directory.
        
        This method checks if DVC is already initialized in the
        project directory. If not, it initializes DVC and creates
        a `.dvcignore` file with common ignore patterns.
        """
        # Initialize DVC if not already initialized
        if (self.project_dir / ".dvc").exists():
            self.repo = Repo(self.project_dir)
            print(f"DVC already initialized in {self.project_dir}.")
        else:
            print(f"Initializing DVC in {self.project_dir}...")
            self.repo = Repo.init(self.project_dir, no_scm=True)
            
            # Restore DVC pipeline if dvc.yaml and dvc.lock exist
            dvc_yaml = self.project_dir / "dvc.yaml"
            dvc_lock = self.project_dir / "dvc.lock"
            
            if dvc_yaml.exists() and dvc_lock.exists():
                print("🔄 dvc.yaml and dvc.lock found. Running DVC repro...")

                try:
                    # Reproduce the DVC pipeline
                    self.repo.reproduce()
                    print("✅ DVC pipeline successfully reproduced.")
                except Exception as e:
                    print(f"❌ DVC repro failed: {e}")
            else:
                print(
                    "⚠️ dvc.yaml and dvc.lock not found. "
                    "Skipping DVC restoration.")

        # Create a .dvcignore if not exists
        ignore_path = self.project_dir / ".dvcignore"
        if not ignore_path.exists():
            with open(ignore_path, 'w') as f:
                f.write(DVCIGNORE_TEMPLATE)
            print(".dvcignore created.")

        # Update DVC tracking if there are changes
        self._update_dvc(human_check=False)

        print("DVC tracking initialized.")

    @property
    def _dvc_tracked_files(self):
        """
        Get a list of DVC tracked files in the project directory.

        Returns
        -------
        list
            List of DVC tracked files.
        """
        tracked_files = []
        for file in self.project_dir.rglob("*"):
            if Path(str(file) + ".dvc").exists():
                tracked_files.append(file)
        return tracked_files

    def _update_dvc(self, human_check=False):
        """
        Add and commit changes to DVC if there are detected differences.
        Optionally, prompt for human confirmation before proceeding.

        Parameters
        ----------
        human_check : bool, default=False
            If True, prompts the user for confirmation before committing.

        Returns
        -------
        bool
            True if a commit was made, False otherwise.
        """
        dvc_file = self.repo.status()
        print(f"Adding untracked data files to DVC")

        self.repo.add(str(self.project_dir))
        print(f"Added {files} to DVC")

        # Human confirmation (if enabled)
        if human_check:
            print("\n📌 Detected Changes:")
            
            user_input = input(
                "\n⚠️  Proceed with committing changes? (y/n): ")
            if user_input.lower() not in ['y', 'yes']:
                print("❌ Commit aborted by user. Removing staged changes.")
                self.repo.reset()
                return False

        # Now check for status (which ones are staged)
        changes_after_add = self.repo.status()
        if not changes_after_add:
            print("⚠️ No staged changes detected. Skipping commit.")
            return False

        # 🔄 Commit the changes
        print(f"📦 Detected staged changes. Committing...")
        self.repo.commit(f"Updated DVC state for {self.project_dirname}")
        print("✅ DVC tracking updated.")
        return True
