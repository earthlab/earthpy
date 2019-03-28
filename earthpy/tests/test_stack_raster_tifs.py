""" Tests for the _stack_raster_tifs() method """

import os
import numpy as np
import pytest
import earthpy.spatial as es


@pytest.fixture
def b1_b2_arrs():
    b1 = np.array([[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
    b2 = np.array([[1, 2, 3, 4, 5], [14, 12, 13, 14, 17]])
    return b1, b2


def test_stack_raster_tifs(b1_b2_arrs):
    """stack_raster_tifs() should return a Warning."""

    # Test data
    b1, b2 = b1_b2_arrs

    # Check Warning for Deprecation
    with pytest.raises(Warning, match="stack_raster_tifs is deprecated"):
        es.stack_raster_tifs([b1, b2], out_path="test.tif")
