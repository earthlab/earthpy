from earthpy import spatial as es
import numpy as np
import pytest


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

        
        
    