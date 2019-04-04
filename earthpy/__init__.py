"""

Utility functions for the working with spatial data.

"""

from pkg_resources import resource_string
import json
from .io import Data

data = Data()
"""
Example datasets for EarthPy

The ``earthpy.data`` object allows quick access to a variety of datasets,
via the :class:`earthpy.io.Data` class and the
:meth:`earthpy.io.Data.get_data` method.
"""

epsg = json.loads(
    resource_string("earthpy", "example-data/epsg.json").decode("utf-8")
)
""" A dictionary of EPSG code to Proj4 string mappings.

Proj4 string values can be received via epsg['epsg-code-here'].

Return
------
epsg: dictionary
    Mappings of EPSG integer string keys to Proj4 strings values.

Example
-------
>>> import earthpy as et
>>> # Get Proj4 string for EPSG code 4326
>>> et.epsg['4326']
'+proj=longlat +datum=WGS84 +no_defs'
"""
