""" Tests for the _stack_bands() method """

import numpy as np
import numpy.ma as ma
import pandas as pd
import pytest
import geopandas as gpd
import rasterio as rio
from shapely.geometry import Polygon, Point, LineString
import earthpy.spatial as es
import os


@pytest.fixture
def b1_b2_arrs():
    b1 = np.array([[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
    b2 = np.array([[1, 2, 3, 4, 5], [14, 12, 13, 14, 17]])
    return b1, b2


def test_stack_raster_tifs(b1_b2_arrs):
    """Unit test for stack_raster_tifs()."""

    # Test data
    b1, b2 = b1_b2_arrs

    # Check Warning for Deprecation
    with pytest.raises(Warning):
        es.stack_raster_tifs([b1, b2], out_path="test.tif")
