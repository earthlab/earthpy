import pytest
import numpy as np
import earthpy.spatial as es


@pytest.fixture
def byte_arr():
    return np.random.randint(300, size=(10, 10))


def test_high_val_range(byte_arr):
    """Bad high value """

    with pytest.raises(
        ValueError, match="`high` should be less than or equal to 255."
    ):
        es.bytescale(byte_arr, high=300)


def test_low_val_range(byte_arr):
    """Bad high value """

    # Bad low value
    with pytest.raises(
        ValueError, match="`low` should be greater than or equal to 0."
    ):
        es.bytescale(arr, low=-100)


def test_high_lessthan_low(byte_arr):
    """Bad high value """

    # High value is less than low value
    with pytest.raises(
        ValueError, match="`high` should be greater than or equal to `low`."
    ):
        es.bytescale(arr, high=100, low=150)


def test_bytescale_high_low_val():
    """"Unit tests for earthpy.spatial.bytescale """
    arr = np.random.randint(300, size=(10, 10))

    # Valid case. should also take care of if statements for cmin/cmax
    val_arr = es.bytescale(arr, high=255, low=0)

    assert val_arr.min() == 0
    assert val_arr.max() == 255

    # Test scale value max is less than min
    with pytest.raises(
        ValueError, match="`cmax` should be larger than `cmin`."
    ):
        es.bytescale(arr, cmin=100, cmax=50)

    # Test scale value max is less equal to min. Commented out for now because it breaks stuff somehow.
    with pytest.raises(
        ValueError,
        match="`cmax` and `cmin` should not be the same value. Please specify `cmax` > `cmin`",
    ):
        es.bytescale(arr, cmin=100, cmax=100)

    # Test scale value max is less equal to min
    scale_arr = es.bytescale(arr, cmin=10, cmax=240)

    assert scale_arr.min() == 0
    assert scale_arr.max() == 255
