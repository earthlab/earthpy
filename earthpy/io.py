"""
earthpy.io
==========

File Input/Output utilities.

"""

import io
import re

import requests
import tarfile
import zipfile

from .config import DEFAULT_DATA_HOME, DATA_URLS, FIGSHARE_API_URL, DVCIGNORE

ALLOWED_FILE_TYPES = ["file", "tar", "tar.gz", "zip"]

# Backward compatibility for old datasets
HOME = DEFAULT_DATA_HOME
        
class Data(object):
    """
    Data storage and retrieval functionality for Earthlab.

    An object of this class is available upon importing earthpy as
    ``earthpy.data`` that writes data files to the project path, 
    default ``~/earth-analytics/data/project-name``.

    Parameters
    ----------
    project : earthpy.Project | None
        The project defining where data is stored.
    figshare_project_id : str | None
        The Figshare project ID to use for data retrieval.
    figshare_token : str | None
        The Figshare token to use for data uploads.
    """

    def __init__(self, project=None, verbose=False):
        self.project = project

        if project is not None:
            self.path = project.project_dir
            self.figshare_project_id = project.figshare_project_id
            self.figshare_token = project.figshare_token
        else:
            self.path = DEFAULT_DATA_HOME
            self.figshare_project_id = None
            self.figshare_token = None
        self.path.mkdir(parents=True, exist_ok=True)

        self.data_keys = sorted(list(DATA_URLS.keys()))

        self.headers = {"Content-Type": "application/json"}
        if self.figshare_token:
            self.headers['Authorization'] = f"token {self.figshare_token}"

    @property
    def articles(self):
        """Fetch and map article titles to IDs."""
        if self.project is None:
            return {}
        article_url = (
            f"{FIGSHARE_API_URL}/projects/"
            f"{self.figshare_project_id}/articles"
        )
        response = requests.get(article_url, headers=self.headers)
        response.raise_for_status()
        articles = response.json()
        # Create a mapping of titles to article IDs
        return {article['title']: article['id'] for article in articles}

    def list_datasets(self):
        """Pretty print available datasets."""
        if self._is_notebook():
            display(JSON(self.articles))
            print('Legacy datasets:')
            display(JSON(self.data_keys))
        else:
            print(self.articles)
            print('Legacy datasets:')
            print(self.data_keys)

    def _is_notebook(self):
        """Check if the code is being run in a Jupyter notebook."""
        try:
            from IPython import get_ipython
            from IPython.display import display, JSON
            return get_ipython() is not None
        except ImportError:
            return False

    def __repr__(self):
        s = "Available Datasets: {}".format(self.data_keys)
        return s

    def get_data(self, 
                 key=None, url=None, title=None,
                 filename=None,
                 replace=False, verbose=True
        ):
        """
        Retrieve the data subset and return its path.

        This will retrieve data from the internet if it isn't already
        downloaded, otherwise it will only return a path to that dataset.

        Parameters
        ----------
        key : str
            The dataset to retrieve. Possible options can be found in
            ``self.data_keys``. Note: ``key``, ``url``, and 
            ``title`` are mutually exclusive.
        url : str
            A URL to fetch into the data directory. Use this for 
            ad-hoc dataset downloads. Note: ``key``, ``url``, and 
            ``title`` are mutually exclusive.
        title : str
            The title of the dataset to retrieve. This is used to
            fetch the article ID from Figshare. Note: ``key``, 
            ``url``, and ``title`` are mutually exclusive.
        filename : str
            The name of the file to save the dataset as. This is
            useful for renaming files after download.
        replace : bool
            Whether to replace the data for this key if it is
            already downloaded.
        verbose : bool
            Whether to print verbose output while downloading files.

        Returns
        -------
        path_data : str
            The path to the downloaded data.

        Examples
        --------
        Download a dataset using a key:

            >>> et.data.get_data('california-rim-fire') # doctest: +SKIP

        Or, download a dataset using a URL:

            >>> url = 'https://ndownloader.figshare.com/files/12395030'
            >>> et.data.get_data(url=url)  # doctest: +SKIP

        """

        if (key is not None) + (url is not None) + (title is not None) > 1:
            raise ValueError(
                "The `key`, `url`, and `title` parameters are mutually "
                "exclusive. Please provide only one of them."
            )

        if (key is None) and (url is None) and (title is None):
            if self.project:
                title = self.project.title
            else:
                print("No key, url, or title provided. Available datasets:")
                self.list_datasets()
                return

        if key is not None:
            if key not in DATA_URLS:
                pretty_keys = ", ".join(repr(k) for k in self.data_keys)
                raise KeyError(
                    "Key '" + key + "' not found in earthpy.io.DATA_URLS. "
                    "Choose one of: {}".format(pretty_keys)
                )

            this_data = DATA_URLS[key]

        if title is not None:
            article_id = self.articles.get(title)
            if article_id is None:
                raise KeyError(
                    f"Title '{title}' not found in available datasets."
                )
            urls = self._get_figshare_download_urls(article_id)

            this_data = []
            for fname, data_url in urls.items():
                # Determine filetype using file name extension
                file_type = "file"
                for ext in ALLOWED_FILE_TYPES:
                    if fname.endswith(ext):
                        file_type = ext
                        fname = fname.replace('.'+ext, "")
                this_data.append((data_url, fname, file_type))

        if url is not None:
            with requests.head(url) as r:
                # Try HTML headers
                if "content-disposition" in r.headers.keys():
                    content = r.headers["content-disposition"]
                    fname = re.findall("filename=(.+)", content)[0]
                # Otherwise get filename from URL
                else:
                    fname = url.split("/")[-1]

            # Remove any extra quotes
            if fname.endswith('"') and fname.startswith('"'):
                fname = fname[1:-1]

            # Determine filetype using file name extension
            file_type = "file"
            for ext in ALLOWED_FILE_TYPES:
                if fname.endswith(ext):
                    file_type = ext

            # User override file name
            if not (filename is None):
                fname = filename

            # Remove file or archive extension for pretty download paths
            # Does not remove extensions for individual files
            fname = re.sub("\\.{}$".format(file_type), "", fname)

            this_data = (url, fname, file_type)

        if not isinstance(this_data, list):
            this_data = [this_data]

        data_paths = []
        print(this_data)
        for url, name, kind in this_data:
            print(name)

            if kind not in ALLOWED_FILE_TYPES:
                raise ValueError(
                    "kind must be one of {}, got {}".format(
                        ALLOWED_FILE_TYPES, kind
                    )
                )

            this_path = self._download(
                url=url,
                path=(self.path / name),
                kind=kind,
                replace=replace,
                verbose=verbose,
            )
            data_paths.append(this_path)
            print(data_paths)
        
        # Return the data path or list of paths
        if len(data_paths) == 1:
            data_paths = data_paths[0]
        return data_paths
    
    def get_data_path(self, dataset_name):
        """
        Retrieve the path to a dataset if it exists in the project directory.
        This method searches recursively in all nested directories and only
        returns exact matches.

        Parameters
        ----------
        dataset_name : str
            The name of the dataset to retrieve.

        Returns
        -------
        Path
            Path to the dataset.

        Raises
        ------
        KeyError
            If the dataset does not exist in the project directory.

        Examples
        --------
        >>> data.get_data_path("rmnp-rgb.tif")
        PosixPath('/path/to/project-dir/subfolder/rmnp-rgb.tif')
        """
        # Recursively search for the file in all subdirectories
        found_files = [
            path for path in self.path.rglob('*') 
            if path.name == dataset_name
        ]

        if not found_files:
            raise KeyError(f"Dataset '{dataset_name}' not found in {self.path}.")
        
        # Return the first match (there shouldn't be duplicates)
        return found_files[0]

    def _get_figshare_download_urls(self, article_id):
        """
        Retrieve the download URLs for all files in a Figshare article.

        Parameters
        ----------
        article_id : int
            The Figshare article ID.

        Returns
        -------
        dict
            A dictionary mapping filenames to download URLs.
        """
        # API Endpoint for article metadata
        url = f"https://api.figshare.com/v2/articles/{article_id}"
        print(f"🔄 Fetching metadata for article {article_id}...")

        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(
                f"Failed to retrieve metadata for article {article_id}."
                f" Status code: {response.status_code}")

        metadata = response.json()
        files = metadata.get("files", [])

        if not files:
            print(f"⚠️ No files found for article {article_id}.")
            return {}

        # Dictionary of filenames and their download URLs
        download_urls = {
            file_info["name"]: file_info["download_url"]
            for file_info in files
        }

        print(f"✅ Found {len(download_urls)} files for download.")
        return download_urls

    def _download(self, url, path, kind, replace, verbose):
        """
        Download a file.

        This helper function downloads files and saves them to ``path``.
        Zip and tar files are extracted to the ``path`` directory.
        The implementation is adapted from the download library:
        https://github.com/choldgraf/download

        Parameters
        ----------
        url : str
            The URL pointing to a file to download.
        path : str
            Destination path of downloaded file.
        kind: str
            Kind of file. Must be one of ALLOWED_FILE_TYPES.
        replace : bool
            Whether to replace the file if it already exists.
        verbose : bool
            Whether to print verbose output while downloading files.


        Returns
        -------
        output_path : str
            Path to the downloaded file.
        """
        path = self.path / path
        if replace is False and path.exists():
            return path

        if verbose is True:
            print("Downloading from {}".format(url))

        r = requests.get(url)
        r.raise_for_status()

        path.parent.mkdir(parents=True, exist_ok=True)
        if kind == "file":
            with open(path, "wb") as f:
                f.write(r.content)
        else:
            self._download_and_extract(path, r, kind, verbose)
        return path

    def _download_and_extract(self, path, r, kind, verbose):
        """Download and extract a compressed archive.

        This function downloads and extracts compressed directories to
        a local directory.

        Parameters
        ----------
        path : str
            Destination path of downloaded file.
        r: requests.models.Response
            URL response that can be used to get the data.
        kind : str
            Kind of file. Must be one of ALLOWED_FILE_TYPES.
        verbose : bool
            Whether to print verbose output while downloading files.


        Returns
        -------
        None

        """
        file_like_object = io.BytesIO(r.content)
        if kind == "zip":
            archive = zipfile.ZipFile(file_like_object)
        if kind == "tar":
            archive = tarfile.open(fileobj=file_like_object)
        if kind == "tar.gz":
            archive = tarfile.open(fileobj=file_like_object, mode="r:gz")
        path.mkdir(parents=True, exist_ok=True)
        archive.extractall(path)
        if verbose is True:
            print("Extracted output to {}".format(path))

    def _zip_dir(self, dir_path, zip_home, zipf, verbose=False):
        """Zip a directory and return the zip file path."""
        for subfile in dir_path.rglob("*"):
            if (subfile.name in DVCIGNORE) and verbose:
                print(f"Skipping {subfile} as it is in DVCIGNORE.")
                continue
            if subfile.is_file():
                dest_path = subfile.relative_to(zip_home)
                if verbose:
                    print(f"    Zipping {subfile} to {dest_path}")
                zipf.write(subfile, dest_path)
            if subfile.is_dir():
                # Ensure directories are included in the zip
                self._zip_dir(subfile, zip_home, zipf)
    
    def prepare_for_upload(self, verbose=False):
        """
        Prepare files for upload to Figshare.
        
        This function collects all files in the project path,
        excluding hidden files and those in the DVCIGNORE list, and 
        zips them into a directory named "figshare-upload". 

        Returns
        -------
        output_path : Path
            Path to the directory containing files prepared for upload.
        """
        files_and_dirs = [
            f for f in self.path.glob("*") 
            if (
                not f in DVCIGNORE) 
                and (not f.name == "figshare-upload")
                and (not f.name.startswith(".")
            )
        ]

        output_path = self.path / "figshare-upload"
        output_path.mkdir(parents=True, exist_ok=True)
        for path in files_and_dirs:
            if path.is_file():
                # If it's a file, just copy it to the output path
                dest_file = output_path / path.name
                if verbose:
                    print(f"Copying file: {path} to {dest_file}")
                dest_file.write_bytes(path.read_bytes())
            if path.is_dir():
                zipfile_name = output_path / f"{path.name}.zip"
                with zipfile.ZipFile(zipfile_name, "w") as zipf:
                    if verbose:
                        print(f"Zipping directory: {path} to {zipfile_name}")
                    self._zip_dir(path, path, zipf)
        if verbose:
            print(f"Prepared files for upload in {output_path}")
        return output_path