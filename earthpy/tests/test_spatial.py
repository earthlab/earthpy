""" Tests for the spatial module. """

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import Polygon, Point
import geopandas as gpd
import earthpy.spatial as es


def test_extent_to_json():
    """"Unit tests for extent_to_json()."""
    # Giving a list [minx, miny, maxx, maxy] makes a polygon
    list_out = es.extent_to_json([0, 0, 1, 1])
    assert list_out['type'] == 'Polygon'

    # The polygon is the unit square
    list_poly = Polygon(list_out['coordinates'][0])
    assert list_poly.area == 1
    assert list_poly.length == 4

    # Providing a GeoDataFrame creates identical output
    points_df = pd.DataFrame(
        {'lat': [0, 1],
         'lon': [0, 1]}
    )
    points_df['coords'] = list(zip(points_df.lon, points_df.lat))
    points_df['coords'] = points_df['coords'].apply(Point)
    gdf = gpd.GeoDataFrame(points_df, geometry='coords')
    gdf_out = es.extent_to_json(gdf)
    assert gdf_out == list_out

    # Giving non-list or GeoDataFrame input raises a ValueError
    with pytest.raises(ValueError):
        es.extent_to_json({'a': 'dict'})

    # Giving minima that exceed maxima raises an error for both x and y coords
    with pytest.raises(AssertionError):
        es.extent_to_json([1, 0, 0, 1])

    with pytest.raises(AssertionError):
        es.extent_to_json([0, 1, 1, 0])


def test_normalized_diff_shapes():
    """If provided with arrays of different shapes,
    normalized_diff returns ValueError."""

    # Test data
    b2_1d = np.array([[6, 7, 8, 9, 10, 16, 17, 18, 19, 20]])
    b1_2d = np.array([[1, 2, 3, 4, 5], [14, 12, 13, 14, 17]])

    with pytest.raises(ValueError):
        es.normalized_diff(b2=b2_1d, b1=b1_2d)


def test_normalized_diff_nomask():
    """If result of normalized_diff does not include nan values,
    array is returned as unmasked."""

    # Test data
    b2_2d = np.array([[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
    b1_2d = np.array([[1, 2, 3, 4, 5], [14, 12, 13, 14, 17]])

    n_diff = es.normalized_diff(b2=b2_2d, b1=b1_2d)

    # Output array unmasked
    assert ma.is_masked(n_diff) == False


def test_normalized_diff_mask():
    """Inf values are set to nan. If result of normalized_diff
    includes nan values, array is returned as masked."""

    # Test data
    b2_2d_inf = np.array([[6, 7, 8, 9, 10], [16, 17, 18, np.nan, 15]])
    b1_2d_inf = np.array([[1, 2, 3, 4, 5], [np.nan, 12, 13, 14, -15]])

    n_diff = es.normalized_diff(b2=b2_2d_inf, b1=b1_2d_inf)

    # Inf values set to nan
    assert np.isinf(n_diff).any() == False

    # Output array masked
    assert ma.is_masked(n_diff)


def test_bytescale_high_low_val():
    """"Unit tests for earthpy.spatial.bytescale """

    arr = np.random.randint(300, size=(10, 10))

    # Bad high value
    with pytest.raises(ValueError):
        es.bytescale(arr, high=300)

    # Bad low value
    with pytest.raises(ValueError):
        es.bytescale(arr, low=-100)

    # High value is less than low value
    with pytest.raises(ValueError):
        es.bytescale(arr, high=100, low=150)

    # Valid case. should also take care of if statements for cmin/cmax
    val_arr = es.bytescale(arr, high=255, low=0)

    assert val_arr.min() == 0
    assert val_arr.max() == 255

    # Test scale value max is less than min
    with pytest.raises(ValueError):
        es.bytescale(arr, cmin=100, cmax=50)

    # TODO: write test case for cmax == cmin
    # Commented out because it breaks for unknown reasons.
    # es.bytescale(arr, cmin=100, cmax=100)

    # Test scale value max is less equal to min
    scale_arr = es.bytescale(arr, cmin=10, cmax=240)
    assert scale_arr.min() == 0
    assert scale_arr.max() == 255
