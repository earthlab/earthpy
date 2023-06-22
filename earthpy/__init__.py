"""

Utility functions for the working with spatial data.

"""

import importlib.resources
import json
from .io import Data

data = Data()
"""
Example datasets for EarthPy

The ``earthpy.data`` object allows quick access to a variety of datasets,
via the :class:`earthpy.io.Data` class and the
:meth:`earthpy.io.Data.get_data` method.
"""
try:
    ref = importlib.resources.files("earthpy").joinpath(
        "example-data/epsg.json"
    )
except AttributeError:
    import importlib_resources

    ref = importlib_resources.files("earthpy").joinpath(
        "example-data/epsg.json"
    )
contents = ref.read_bytes().decode("utf-8")

epsg = json.loads(contents)
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
