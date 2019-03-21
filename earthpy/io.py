"""File Input/Output utilities."""

import io
import os
import os.path as op
import re
import requests
import tarfile
import zipfile
import earthpy

# Data URLs, structured as {'week_name': [(URL, FILENAME, FILETYPE)]}
# If zipfile, tarfile, etc, unzip to a folder w/ the name
DATA_URLS = {
    "co-flood-extras": [
        (
            "https://ndownloader.figshare.com/files/7010681",
            "boulder-precip.csv",
            "file",
        ),
        (
            "https://ndownloader.figshare.com/files/7010681",
            "temperature_example.csv",
            "file",
        ),
    ],
    "colorado-flood": (
        "https://ndownloader.figshare.com/files/12395030",
        ".",
        "zip",
    ),
    "spatial-vector-lidar": (
        "https://ndownloader.figshare.com/files/12459464",
        ".",
        "zip",
    ),
    "cold-springs-modis-h5": (
        "https://ndownloader.figshare.com/files/10960112",
        ".",
        "zip",
    ),
    "cold-springs-fire": (
        "https://ndownloader.figshare.com/files/10960109",
        ".",
        "zip",
    ),
    "cs-test-naip": (
        "https://ndownloader.figshare.com/files/10960211?private_link=18f892d9f3645344b2fe",
        ".",
        "zip",
    ),
    "cs-test-landsat": (
        "https://ndownloader.figshare.com/files/10960214?private_link=fbba903d00e1848b423e",
        ".",
        "zip",
    ),
    "ndvi-automation": (
        "https://ndownloader.figshare.com/files/13431344",
        ".",
        "zip",
    ),
    "california-rim-fire": (
        "https://ndownloader.figshare.com/files/14419310",
        ".",
        "zip",
    ),
}

HOME = op.join(op.expanduser("~"))
DATA_NAME = op.join("earth-analytics", "data")
ALLOWED_FILE_TYPES = ["file", "tar", "tar.gz", "zip"]


class Data(object):
    """
    Data storage and retrieval functionality for Earthlab.

    An object of this class is available upon importing earthpy as
    ``earthpy.data`` that writes data files to the path:
    ``~/earth-analytics/data/``.

    Parameters
    ----------
    path : string | None
        The path where data is stored. NOTE: this defaults to the directory
        ``~/earth-analytics/data/``.

    Examples
    --------
    List datasets that are available for download, using default object:

        >>> import earthpy as et
        >>> et.data
        Available Datasets: ['california-rim-fire', ...]

    Specify a custom directory for data downloads:

        >>> et.data.path = "."
        >>> et.data
        Available Datasets: ['california-rim-fire', ...]
    """

    def __init__(self, path=None):
        if path is None:
            path = op.join(HOME, DATA_NAME)
        self.path = path
        self.data_keys = sorted(list(DATA_URLS.keys()))

    def __repr__(self):
        s = "Available Datasets: {}".format(self.data_keys)
        return s

    def get_data(self, key=None, url=None, replace=False, verbose=True):
        """
        Retrieve the data for a given week and return its path.

        This will retrieve data from the internet if it isn't already
        downloaded, otherwise it will only return a path to that dataset.

        Parameters
        ----------
        key : str
            The dataset to retrieve. Possible options can be found in
            ``self.data_keys``. Note: ``key`` and ``url`` are mutually
            exclusive.
        url : str
            A URL to fetch into the data directory. Use this for ad-hoc dataset
            downloads. Note: ``key`` and ``url`` are mutually exclusive.
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

        Or, download a dataset using a figshare URL:

            >>> url = 'https://ndownloader.figshare.com/files/12395030'
            >>> et.data.get_data(url=url)  # doctest: +SKIP

        """
        if key is not None and url is not None:
            raise ValueError(
                "The `url` and `key` parameters can not both be "
                "set at the same time."
            )
        if key is None and url is None:
            print(self.__repr__())
            return

        if key is not None:
            if key not in DATA_URLS:
                pretty_keys = ", ".join(repr(k) for k in self.data_keys)
                raise KeyError(
                    "Key '" + key + "' not found in earthpy.io.DATA_URLS. "
                    "Choose one of: {}".format(pretty_keys)
                )

            this_data = DATA_URLS[key]
            this_root = op.join(str(self.path), key)

        if url is not None:
            with requests.head(url) as r:
                if "content-disposition" in r.headers.keys():
                    content = r.headers["content-disposition"]
                    fname = re.findall("filename=(.+)", content)[0]
                else:
                    fname = url.split("/")[-1]

            # try and deduce filetype based on extension
            file_type = "file"
            for ext in ALLOWED_FILE_TYPES:
                if fname.endswith(ext):
                    file_type = ext

            # remove extension for pretty download paths
            fname = re.sub("\\.{}$".format(file_type), "", fname)

            this_data = (url, fname, file_type)
            this_root = op.join(str(self.path), "earthpy-downloads")

        if not isinstance(this_data, list):
            this_data = [this_data]

        data_paths = []
        for url, name, kind in this_data:

            if kind not in ALLOWED_FILE_TYPES:
                raise ValueError(
                    "kind must be one of {}, got {}".format(
                        ALLOWED_FILE_TYPES, kind
                    )
                )

            this_path = self._download(
                url=url,
                path=os.path.join(this_root, name),
                kind=kind,
                replace=replace,
                verbose=verbose,
            )
            data_paths.append(this_path)
        if len(data_paths) == 1:
            data_paths = data_paths[0]
        return data_paths

    def _download(self, url, path, kind, replace, verbose):
        """ Download a file.

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
        path = op.expanduser(path)
        if replace is False and op.exists(path):
            return path

        if verbose is True:
            print("Downloading from {}".format(url))

        r = requests.get(url)

        os.makedirs(op.dirname(path), exist_ok=True)
        if kind == "file":
            with open(path, "wb") as f:
                f.write(r.content)
        else:
            self._download_and_extract(path, r, kind, verbose)
        return path

    def _download_and_extract(self, path, r, kind, verbose):
        """ Download and extract a compressed archive.

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
        os.makedirs(path, exist_ok=True)
        archive.extractall(path)
        if verbose is True:
            print("Extracted output to {}".format(path))


def path_to_example(dataset):
    """ Construct a file path to an example dataset.

    This file defines helper functions to access data files in this directory,
    to support examples. Adapted from the PySAL package.

    Parameters
    ----------
    dataset: string
        Name of a dataset to access (e.g., "epsg.json", or "RGB.byte.tif")

    Returns
    -------
    A file path (string) to the dataset

    Example
    -------

        >>> import earthpy.io as eio
        >>> eio.path_to_example('rmnp-dem.tif')
        '...rmnp-dem.tif'
    """
    earthpy_path = os.path.split(earthpy.__file__)[0]
    data_dir = os.path.join(earthpy_path, "example-data")
    data_files = os.listdir(data_dir)
    if dataset not in data_files:
        raise KeyError(dataset + " not found in earthpy example data.")
    return os.path.join(data_dir, dataset)
