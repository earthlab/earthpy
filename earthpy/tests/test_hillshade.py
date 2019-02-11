""" Tests for the hillshade function. """

import numpy as np
import pytest
import earthpy.spatial as es
import os


@pytest.fixture
def hillshade_arr():
    """Create three-dimensional array for testing input array
    to hillshade function. """
    arr = np.array(
        [
            [
                [1100, 1500, 1200, 1000, 800, 700],
                [1000, 1400, 1300, 1200, 1000, 900],
            ]
        ]
    )
    return arr


def test_hillshade_shape(hillshade_arr):
    """If provided with input array that is two-dimensional,
    ValueError returned."""

    # Check ValueError
    with pytest.raises(
        ValueError, match="Input array should be two-dimensional"
    ):
        es.hillshade(hillshade_arr, azimuth=315, angle_altitude=45)


def test_hillshade_altitude(hillshade_arr):
    """If provided with altitude value greater than 90,
    ValueError returned."""

    # Test data
    squeezed_arr = hillshade_arr.squeeze()

    # Check ValueError
    with pytest.raises(
        ValueError,
        match="Altitude value should be less than or equal to 90 degrees",
    ):
        es.hillshade(squeezed_arr, azimuth=315, angle_altitude=100)


def test_hillshade_azimuth(hillshade_arr):
    """If provided with azimuth value greater than 360,
    ValueError returned."""

    # Test data
    squeezed_arr = hillshade_arr.squeeze()

    # Check ValueError
    with pytest.raises(
        ValueError,
        match="Azimuth value should be less than or equal to 360 degrees",
    ):
        es.hillshade(squeezed_arr, azimuth=375, angle_altitude=45)
