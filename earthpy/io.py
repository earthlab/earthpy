"""File Input/Output utilities."""
## This module will move to a new module for downloading data
## and building lessons

import os
import os.path as op
from download import download


# Data URLs, structured as {'week_name': [(URL, FILENAME, FILETYPE)]}
# If zipfile, tarfile, etc, unzip to a folder w/ the name
DATA_URLS = {

    'co-flood-extras': [('https://ndownloader.figshare.com/files/7010681', 'boulder-precip.csv', 'file'),
                        ('https://ndownloader.figshare.com/files/7010681', 'temperature_example.csv', 'file')],
    'colorado-flood': ('https://ndownloader.figshare.com/files/12395030', '.', 'zip'),
    'spatial-vector-lidar': ('https://ndownloader.figshare.com/files/12459464', '.', 'zip'),
    'cold-springs-modis-h5': ('https://ndownloader.figshare.com/files/10960112', '.', 'zip'),
    'cold-springs-fire': ('https://ndownloader.figshare.com/files/10960109', '.', 'zip'),
    'cs-test-naip': ('https://ndownloader.figshare.com/files/10960211?private_link=18f892d9f3645344b2fe', '.', 'zip'),
    'cs-test-landsat': ('https://ndownloader.figshare.com/files/10960214?private_link=fbba903d00e1848b423e', '.', 'zip'),
    'ndvi-automation': ('https://ndownloader.figshare.com/files/13431344', '.', 'zip'),

}

ALLOWED_FILE_TYPES = ['zip', 'tar', 'tar.gz', 'file']

HOME = op.join(op.expanduser('~'))
DATA_NAME = op.join('earth-analytics', 'data')


class EarthlabData(object):
    """
    Data storage and retrieval functionality for Earthlab.

    Parameters
    ----------
    path : string | None
        The path where data is stored.
    """
    def __init__(self, path=None):
        if path is None:
            path = op.join(HOME, DATA_NAME)
        self.path = path
        self.data_keys = list(DATA_URLS.keys())

    def __repr__(self):
        s = 'Available Datasets: {}'.format(self.data_keys)
        return s

    def get_data(self, key=None, replace=False):
        """
        Retrieve the data for a given week and return its path.

        This will retrieve data from the internet if it isn't already
        downloaded, otherwise it will only return a path to that dataset.

        Parameters
        ----------
        key : str
            The dataset to retrieve. Possible options can be found in
            ``self.data_keys``.
        replace : bool
            Whether to replace the data for this key if it is
            already downloaded.

        Returns
        -------
        path_data : str
            The path to the downloaded data.
        """
        if key is None:
            print('Available datasets: {}'.format(
                list(DATA_URLS.keys())))
        elif key not in DATA_URLS:
            raise ValueError("Don't understand key "
                             "{}\nChoose one of {}".format(
                             key, DATA_URLS.keys()))
        else:
            this_root = op.join(self.path, key)
            this_data = DATA_URLS[key]
            if not isinstance(this_data, list):
                this_data = [this_data]
            data_paths = []
            for url, name, kind in this_data:
                if kind not in ALLOWED_FILE_TYPES:
                    raise ValueError('kind must be one of {}, got {}'.format(ALLOWED_FILE_TYPES, kind))

                # If kind is not 'file' it will be un-archived to a folder w/ `name`
                # else create a file called `name`
                this_path = download(url, os.path.join(this_root, name),
                                     replace=replace, kind=kind,
                                     verbose=False)
                data_paths.append(this_path)
            if len(data_paths) == 1:
                data_paths = data_paths[0]
            return data_paths


# Potential functionality for website build.
# Move to new utils package

def list_files(path, depth=3):
    """
    List files in a directory up to a specified depth.

    Parameters
    ----------
    path : str
        A path to a folder whose contents you want to list recursively.
    depth : int
        The depth of files / folders you want to list inside of ``path``.
    """
    if not os.path.isdir(path):
        raise ValueError('path: {} is not a directory'.format(path))
    depth_str_base = '  '
    if not path.endswith(os.sep):
        path = path + os.sep

    for ii, (i_path, folders, files) in enumerate(os.walk(path)):
        folder_name = op.basename(i_path)
        path_wo_base = i_path.replace(path, '')
        this_depth = len(path_wo_base.split('/'))
        if this_depth > depth:
            continue

        # Define the string for this level
        depth_str = depth_str_base * this_depth
        print(depth_str + folder_name)

        if this_depth + 1 > depth:
            continue
        for ifile in files:
            print(depth_str + depth_str_base + ifile)
