""" __init__ file for example data module

This file defines helper functions to access data files in this directory,
to support examples. Adapted from:
https://github.com/pysal/pysal/blob/master/pysal/examples/__init__.py
"""

import os
import earthpy


__all__ = ['get_path']


def get_path(dataset):
    """ Construct a file path to a dataset.

    Parameters
    ----------
    dataset: string
        Name of a dataset to access (e.g., "epsg.json", or "RGB.byte.tif")

    Returns
    -------
    A file path (string) to the dataset
    """
    earthpy_path = os.path.split(earthpy.__file__)[0]
    data_dir = os.path.join(earthpy_path, "data")
    data_files = os.listdir(data_dir)
    if dataset in data_files:
        return os.path.join(data_dir, dataset)
    else:
        raise KeyError(dataset + " not found in earthpy example data.")
