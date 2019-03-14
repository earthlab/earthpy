""" Tests for the hillshade function. """

import numpy as np
import pytest
import earthpy.spatial as es


@pytest.fixture
def hillshade_arr():
    """Create 2-dimensional array of shape (6,6) for testing
    input array to hillshade function. """
    arr = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1]])
    return arr


@pytest.fixture
def hillshade_result():
    """Create 2-dimensional array of shape (6,6) of expected
    returned array using hillshade_arr() as input. """
    result = np.array(
        [
            [
                217.6561146,
                217.6561146,
                217.6561146,
                217.6561146,
                217.6561146,
                236.3280573,
            ],
            [
                217.6561146,
                217.6561146,
                217.6561146,
                217.6561146,
                236.64794705,
                253.16381636,
            ],
        ]
    )
    return result


def test_hillshade_result(hillshade_arr, hillshade_result):
    """Returned array using hillshade_arr as input should equal
    hillshade_result."""

    # Tolerance used for floating point numbers
    assert np.allclose(
        es.hillshade(hillshade_arr, azimuth=315, angle_altitude=45),
        hillshade_result,
        atol=1e-10,
        rtol=1e-10,
    )


def test_hillshade_shape(hillshade_arr):
    """A 3-dimensional array should return a ValueError."""

    # Test 3-dimensional array
    hillshade_arr_3d = hillshade_arr[np.newaxis, :]

    # Check ValueError
    with pytest.raises(
        ValueError, match="Input array should be two-dimensional"
    ):
        es.hillshade(hillshade_arr_3d, azimuth=315, angle_altitude=45)


def test_hillshade_altitude(hillshade_arr):
    """An altitude value >90 returns a ValueError."""

    # Check ValueError
    with pytest.raises(
        ValueError,
        match="Altitude value should be less than or equal to 90 degrees",
    ):
        es.hillshade(hillshade_arr, azimuth=315, angle_altitude=100)


def test_hillshade_azimuth(hillshade_arr):
    """An azimuth value >360 returns a ValueError."""

    # Check ValueError
    with pytest.raises(
        ValueError,
        match="Azimuth value should be less than or equal to 360 degrees",
    ):
        es.hillshade(hillshade_arr, azimuth=375, angle_altitude=45)
