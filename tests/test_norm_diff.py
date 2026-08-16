""" Tests for the normalized_diff function in the spatial module. """


import numpy as np
import numpy.ma as ma
import pytest
import earthpy.spatial as es


@pytest.fixture
def b1_b2_arrs():
    b1 = np.array([[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
    b2 = np.array([[1, 2, 3, 4, 5], [14, 12, 13, 14, 17]])
    return b1, b2


def test_normalized_diff_shapes(b1_b2_arrs):
    """Test that two arrays with different shapes returns a ValueError."""

    # Test data
    b1, b2 = b1_b2_arrs
    b2 = b2[0]

    # Check ValueError
    with pytest.raises(
        ValueError, match="Both arrays should have the same dimensions"
    ):
        es.normalized_diff(b1=b1, b2=b2)


def test_normalized_diff_no_mask(b1_b2_arrs):
    """Test that if result does not include nan values,
    the array is returned as unmasked."""

    # Test data
    b1, b2 = b1_b2_arrs

    n_diff = es.normalized_diff(b1=b1, b2=b2)

    # Output array unmasked
    assert not ma.is_masked(n_diff)


def test_normalized_diff_inf(b1_b2_arrs):
    """Test that inf values in result are set to nan and
    that array is returned as masked."""

    # Test data
    b1, b2 = b1_b2_arrs
    b2[1:, 4:] = -20

    # Check warning
    with pytest.warns(
        Warning, match="Divide by zero produced infinity values"
    ):
        n_diff = es.normalized_diff(b1=b1, b2=b2)

    # Inf values set to nan
    assert not np.isinf(n_diff).any()

    # Output array masked
    assert ma.is_masked(n_diff)


def test_normalized_diff_mask(b1_b2_arrs):
    """Test that if result does include nan values,
    the array is returned as masked."""

    # Test data
    b1, b2 = b1_b2_arrs
    b2 = b2.astype(float)
    b2[1:, 4:] = np.nan

    n_diff = es.normalized_diff(b1=b1, b2=b2)

    # Output array masked
    assert ma.is_masked(n_diff)
