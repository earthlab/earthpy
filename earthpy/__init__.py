"""Utility functions for the working with spatial data."""

from pkg_resources import resource_string
import json
from .io import Data


data = Data()

epsg = json.loads(
    resource_string("earthpy", "example-data/epsg.json").decode("utf-8")
)
