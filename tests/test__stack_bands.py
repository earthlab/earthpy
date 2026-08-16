""" Tests for the _stack_bands() method """

import numpy as np
import pytest
import earthpy.spatial as es


@pytest.fixture
def b1_b2_arrs():
    b1 = np.array([[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
    b2 = np.array([[1, 2, 3, 4, 5], [14, 12, 13, 14, 17]])
    return b1, b2


def test__stack_bands(b1_b2_arrs):
    """_stack_bands input should be of type DatasetReader."""

    # Test data
    b1, b2 = b1_b2_arrs

    # Check ValueError for Dataset Reader
    with pytest.raises(
        AttributeError, match="The sources object should be Dataset Reader"
    ):
        es._stack_bands([b1, b2])
