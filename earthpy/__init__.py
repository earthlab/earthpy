"""Utility functions for the working with spatial data."""

from pkg_resources import resource_string
import json
from .io import Data


def load_epsg():
    """ A function to return a dictionary of EPSG code to Proj4 string mappings.
    
    This function supports calling epsg['code-here'].
    
    Return
    ------
    epsg: dictionary
        The epsg dictionary contains mappings of EPSG integer string codes to Proj4 strings.
    
    Example
    -------
    >>> import earthpy as et
    >>> # Get Proj4 string for EPSG code 4326 
    >>> et.epsg['4326']  
    '+proj=longlat +datum=WGS84 +no_defs'
    """

    epsg = json.loads(
        resource_string("earthpy", "example-data/epsg.json").decode("utf-8")
    )
    return epsg


data = Data()

epsg = load_epsg()
