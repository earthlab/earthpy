"""Utility functions for the earthlab class."""

from .io import EarthlabData, list_files
from download import download
import json
import os.path as op
from . import utils, spatial

data = EarthlabData()

# This EPSG mapping converted from:
# https://github.com/jswhit/pyproj/blob/master/lib/pyproj/data/epsg
#with open(op.join(op.dirname(__file__), 'epsg.json'), 'r') as ff:
#    epsg = json.load(ff)

from pkg_resources import resource_string
epsg = json.loads(resource_string("earthpy", "data/epsg.json").decode('utf-8'))
