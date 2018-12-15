""" Tests for example data. """

import os
import pytest
import earthpy.data as ed


def test_invalid_datasets_raise_errors():
    """ Raise errors when users provide nonexistent datasets. """
    with pytest.raises(KeyError):
        ed.get_path("Non-existent dataset")


def test_missing_datasets_raise_errors():
    """ Raise errors when users forget to provide a dataset. """
    with pytest.raises(KeyError):
        ed.get_path("")


def test_valid_datasets_get_returned():
    """ If users give a valid dataset name, return a valid path. """
    epsg_path = ed.get_path("epsg.json")
    assert os.path.isfile(epsg_path)
