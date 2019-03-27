""" Tests for the _stack_bands() method """

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


def test_stack_raster(basic_image_tif):
    """Unit tests for raster stacking with es.stack()."""

    # Create list of 4 basic_image_tif files (filepaths)
    band_files = [basic_image_tif] * 4

    # Test that out_path needs a file extension to be valid
    out_fi = "test_stack"
    with pytest.raises(
        ValueError, match="Please specify a valid file name for output."
    ):
        stack_arr, stack_prof = es.stack(band_files, out_path=out_fi)

    # Test that out_path needs a file extension to be valid
    out_fi = "test_stack.tif"
    with pytest.raises(ValueError, match="The list of"):
        stack_arr, stack_prof = es.stack([], out_path=out_fi)

    # Test that the output file format is same as inputs
    # This can be flexible but for now forcing the same format
    out_fi = "test_stack.jp2"
    with pytest.raises(ValueError, match="Source"):
        stack_arr, stack_prof = es.stack(band_files, out_path=out_fi)

    # Test valid use case specifying output file.
    # Make sure the output file exists and then clean it up
    out_fi = "test_stack.tif"
    stack_arr, stack_prof = es.stack(band_files, out_path=out_fi)

    assert os.path.exists(out_fi)
    if os.path.exists(out_fi):
        os.remove(out_fi)

    # Test valid use case of just getting back the array.
    stack_arr, stack_prof = es.stack(band_files)

    assert stack_arr.shape[0] == len(band_files)
    assert stack_prof["count"] == len(band_files)

    # Test the nodata parameter
    stack_arr, stack_prof = es.stack(band_files, nodata=0)

    assert 0 not in stack_arr
