
"""Tests for the spatial module"""

from earthpy import spatial as es
import numpy as np
import pytest


import pandas as pd
import numpy as np
import pytest
from shapely.geometry import Polygon, Point, LineString
import shapely
import geopandas as gpd
import earthpy.spatial as es
import earthpy.clip as cl

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
    df = pd.DataFrame(
        {'lat': [0, 1],
         'lon': [0, 1]}
    )
    df['coords'] = list(zip(df.lon, df.lat))
    df['coords'] = df['coords'].apply(Point)
    gdf = gpd.GeoDataFrame(df, geometry='coords')
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

def test_bytescale_high_low_val():
    """"Unit tests for earthpy.spatial.bytescale """
    
    arr = np.random.randint(300, size=(10,10))
    
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
        
        
    # Test scale value max is less equal to min
    es.bytescale(arr, cmin=100, cmax=100)
    # assert something    
        
    # Test scale value max is less equal to min
    scale_arr = es.bytescale(arr, cmin=10, cmax=240)
    assert scale_arr.min() == 0
    assert scale_arr.max() == 255

        
        
    

