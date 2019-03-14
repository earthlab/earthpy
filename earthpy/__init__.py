"""Utility functions for the working with spatial data."""

from pkg_resources import resource_string
import json
from .io import Data


data = Data()

epsg = json.loads(
    resource_string("earthpy", "example-data/epsg.json").decode("utf-8")
)


def load_epsg():
    """ A function to return a dictionary of EPSG code to Proj4 string mappings."""

    return json.loads(
        resource_string("earthpy", "example-data/epsg.json").decode("utf-8")
    )
