""" Tests for the stack() method """

import os
import numpy as np
import pytest
import earthpy.spatial as es


def test_stack_no_file_ext(basic_image_tif):
    """Test for error raised when no file extension provided in output file."""

    # Create list of 4 basic_image_tif files (filepaths)
    band_files = [basic_image_tif] * 4

    # Test that out_path needs a file extension to be valid
    out_fi = "test_stack"
    with pytest.raises(
        ValueError, match="Please specify a valid file name for output."
    ):
        stack_arr, stack_prof = es.stack(band_files, out_path=out_fi)


def test_stack_yes_file_ext(basic_image_tif):
    """Test for valid file extension."""

    # Test that out_path needs a file extension to be valid
    out_fi = "test_stack.tif"
    with pytest.raises(ValueError, match="The list of"):
        stack_arr, stack_prof = es.stack([], out_path=out_fi)


def test_stack_out_format(basic_image_tif):
    """Test that output format matches input format."""

    # Create list of 4 basic_image_tif files (filepaths)
    band_files = [basic_image_tif] * 4

    # Test that the output file format is same as inputs
    # This can be flexible but for now forcing the same format
    out_fi = "test_stack.jp2"
    with pytest.raises(ValueError, match="Source"):
        stack_arr, stack_prof = es.stack(band_files, out_path=out_fi)


def test_stack_outputfile(basic_image_tif):
    """Test successful creation of output file."""

    # Create list of 4 basic_image_tif files (filepaths)
    band_files = [basic_image_tif] * 4

    # Test valid use case specifying output file.
    # Make sure the output file exists and then clean it up
    out_fi = "test_stack.tif"
    stack_arr, stack_prof = es.stack(band_files, out_path=out_fi)

    assert os.path.exists(out_fi)
    if os.path.exists(out_fi):
        os.remove(out_fi)


def test_stack_return_array(basic_image_tif):
    """ Test returning only array."""

    # Create list of 4 basic_image_tif files (filepaths)
    band_files = [basic_image_tif] * 4

    # Test valid use case of just getting back the array.
    stack_arr, stack_prof = es.stack(band_files)

    assert stack_arr.shape[0] == len(band_files)
    assert stack_prof["count"] == len(band_files)


def test_stack_nodata(basic_image_tif):
    """Test nodata parameter for masking stacked array."""

    # Create list of 4 basic_image_tif files (filepaths)
    band_files = [basic_image_tif] * 4

    # Test the nodata parameter
    stack_arr, stack_prof = es.stack(band_files, nodata=0)

    assert 0 not in stack_arr


def test_stack_nodata_outfile(basic_image_tif):
    """Test nodata parameter for masking stacked array and writing output file."""

    # Create list of 4 basic_image_tif files (filepaths)
    band_files = [basic_image_tif] * 4

    out_fi = "test_stack.tif"
    stack_arr, stack_prof = es.stack(band_files, out_path=out_fi, nodata=0)

    assert 0 not in stack_arr
    assert os.path.exists(out_fi)
    if os.path.exists(out_fi):
        os.remove(out_fi)
