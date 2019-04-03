""" Tests for the stack() method """

import os
import numpy as np
import pytest
import earthpy.spatial as es


@pytest.fixture
def out_path(tmpdir):
    """ A path for an output .tif file. """
    return os.path.join(str(tmpdir), "out.tif")


@pytest.fixture
def in_paths(basic_image_tif):
    """ Input file paths for tifs to stack. """
    return [basic_image_tif] * 4


def test_stack_no_file_ext(in_paths):
    """Test for error raised when no file extension provided in output file."""

    # Test that out_path needs a file extension to be valid
    out_fi = "test_stack"
    with pytest.raises(
        ValueError, match="Please specify a valid file name for output."
    ):
        stack_arr, stack_prof = es.stack(in_paths, out_path=out_fi)


def test_stack_yes_file_ext(out_path):
    """Test for valid file extension."""

    # Test that out_path needs a file extension to be valid
    with pytest.raises(ValueError, match="The list of"):
        stack_arr, stack_prof = es.stack([], out_path=out_path)


def test_stack_out_format(in_paths):
    """Test that output format matches input format."""

    # Test that the output file format is same as inputs
    # This can be flexible but for now forcing the same format
    out_fi = "test_stack.jp2"
    with pytest.raises(ValueError, match="Source"):
        stack_arr, stack_prof = es.stack(in_paths, out_path=out_fi)


def test_stack_outputfile(in_paths, out_path):
    """Test successful creation of output file."""

    # Test valid use case specifying output file.
    stack_arr, stack_prof = es.stack(in_paths, out_path)

    assert os.path.exists(out_path)


def test_stack_return_array(in_paths):
    """ Test returning only array."""

    # Test valid use case of just getting back the array.
    n_bands = len(in_paths)
    stack_arr, stack_prof = es.stack(in_paths)
    assert stack_arr.shape[0] == n_bands and stack_prof["count"] == n_bands


def test_stack_nodata(in_paths, out_path):
    """Test nodata parameter for masking stacked array."""

    stack_arr, stack_prof = es.stack(in_paths, out_path, nodata=0)

    # basic_image has 91 0 values, which should be masked
    assert 0 not in stack_arr and np.sum(stack_arr.mask) == 91 * len(in_paths)


def test_stack_nodata_outfile(in_paths, out_path):
    """Test nodata parameter for masking stacked array and writing output file."""

    stack_arr, stack_prof = es.stack(in_paths, out_path, nodata=0)

    # basic_image has 91 0 values, which should be masked
    assert 0 not in stack_arr and np.sum(stack_arr.mask) == 91 * len(in_paths)
    assert os.path.exists(out_path)


def test_stack_invalid_out_paths_raise_errors():
    """ If users provide an output path that doesn't exist, raise error. """

    with pytest.raises(ValueError, match="not exist"):
        es.stack(
            band_paths=["fname1.tif", "fname2.tif"],
            out_path="nonexistent_directory/output.tif",
        )
