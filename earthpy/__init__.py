"""Utility functions for the working with spatial data."""

from pkg_resources import resource_string
import json
from .io import Data


data = Data()

epsg = json.loads(
    resource_string("earthpy", "example-data/epsg.json").decode("utf-8")
)


def load_epsg():
    """ A function to return a dictionary of EPSG code to Proj4 string mappings.
    
    Return
    ------
    epsg: dictionary
        The epsg dictionary contains mappings of EPSG integer string codes to Proj4 strings.
    
    Example
    -------
    >>> import earthpy as et
    >>> epsg = et.load_epsg()
    >>> epsg4326_proj4 = epsg['4326']  # extracting the Proj4 string for EPSG code 4326 
    """

    epsg = json.loads(
        resource_string("earthpy", "example-data/epsg.json").decode("utf-8")
    )
    return epsg
