import pytest
import numpy as np
import earthpy.spatial as es


@pytest.fixture
def byte_arr():
    return np.random.randint(300, size=(10, 10))


def test_high_val_range():
    """A 16 bit int arr with values at the range end should be scaled properly.

    This test explicitly hits the user case of someone providing an array of a
    dtype at the end of it's range of values. Bytescale should not fail.
    """

    # The valid range of dtype int16 values is -32768 to 32767
    rgb_bands = np.array([1, 32767, 3, -32768]).astype("int16")
    arr = es.bytescale(rgb_bands)

    assert arr.min() == 0
    assert arr.max() == 255


def test_high_val_greater_255(byte_arr):
    """A high value >255 should fail gracefully. """

    with pytest.raises(
        ValueError, match="`high` should be less than or equal to 255."
    ):
        es.bytescale(byte_arr, high=300)


def test_low_val_range(byte_arr):
    """A low value <0 should fail gracefully. """

    # Bad low value
    with pytest.raises(
        ValueError, match="`low` should be greater than or equal to 0."
    ):
        es.bytescale(byte_arr, low=-100)


def test_high_lessthan_low(byte_arr):
    """Fail gracefully when the high value is lower than the low value."""

    # High value is less than low value
    with pytest.raises(
        ValueError, match="`high` should be greater than or equal to `low`."
    ):
        es.bytescale(byte_arr, high=100, low=150)


def test_low_high_vals_work(byte_arr):
    """The high/low param vals determine the min and max of the output arr."""

    # Valid case. should also take care of if statements for cmin/cmax
    val_arr = es.bytescale(byte_arr, high=255, low=0)

    assert val_arr.min() == 0
    assert val_arr.max() == 255


def test_cmax_higher_than_cmin(byte_arr):
    """Fail gracefully when the cmax is smaller than the cmin."""

    with pytest.raises(
        ValueError, match="`cmax` should be larger than `cmin`."
    ):
        es.bytescale(byte_arr, cmin=100, cmax=50)


def test_cmax_equals_cmin(byte_arr):
    """Fail gracefully when the cmax is smaller than the cmin."""

    with pytest.raises(
        ValueError, match="`cmax` and `cmin` should not be the same value. "
    ):
        es.bytescale(byte_arr, cmin=100, cmax=100)


def test_cmax_cmin_work(byte_arr):
    """"Cmax and min values returns an arr with the range 0-255."""

    scale_arr = es.bytescale(byte_arr, cmin=10, cmax=240)

    assert scale_arr.min() == 0
    assert scale_arr.max() == 255
