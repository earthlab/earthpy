from earthpy import spatial

def test_extent_to_json():
    '''Check that a polygon is generated with 5 vertices'''
    json = spatial.extent_to_json(minx=0, miny=0, maxx=1, maxy=1)
    assert json.get('type') == 'Polygon'

    vertices = json.get('coordinates')[0]
    assert len(vertices) == 5
