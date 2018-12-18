Earthpy Spatial Vector Data
===========================

The ``earthpy`` spatial module provides functions that wrap around ``rasterio``
and ``geopandas`` to work with raster and vector data in Python.


Clip Vector Data
~~~~~~~~~~~~~~~~

The ``clip_shp`` function takes two geopandas GeoDataframe objects. The first
object is a point or line polygon GeoDataframe to be spatially clipped.
The second object will be used as the spatial extent to clip the first object.

All inputs must be in the same Coordinate Refenence System (CRS).

``clip_shp`` takes 2 input parameters:

``shp``: geopandas GeoDataframe you wish to clip

``clip_obj``: geopandas GeoDataframe with the clip points or bound

The output of ``clip_shp`` is a geopandas GeoDataframe.

Example of clipping points (glacier locations in the state of Colorado) with
a polygon (the boundary of Rocky Mountain National Park):

    >>> import geopandas as gpd
    >>> import earthpy.clip as cl
    >>> from earthpy.io import path_to_example

    >>> rmnp = gpd.read_file(path_to_example('rmnp.shp'))
    >>> glaciers = gpd.read_file(path_to_example('colorado-glaciers.geojson'))
    >>> glaciers.shape
    (134, 2)
    >>> rmnp_glaciers = cl.clip_shp(glaciers, rmnp)
    >>> rmnp_glaciers.shape
    (36, 2)

Example of clipping a line (the Continental Divide Trail) with a
polygon (the boundary of Rocky Mountain National Park):

    >>> import geopandas as gpd
    >>> import earthpy.clip as cl
    >>> from earthpy.io import path_to_example

    >>> rmnp = gpd.read_file(path_to_example('rmnp.shp'))
    >>> cdt = gpd.read_file(path_to_example('continental-div-trail.geojson'))
    >>> rmnp_cdt_section = cl.clip_shp(cdt, rmnp)
    >>> cdt['geometry'].length > rmnp_cdt_section['geometry'].length
    0    True
    dtype: bool

Example of clipping a polygon (Colorado counties) with another polygon
(the boundary of Rocky Mountain National Park):

    >>> import geopandas as gpd
    >>> import earthpy.clip as cl
    >>> from earthpy.io import path_to_example

    >>> rmnp = gpd.read_file(path_to_example('rmnp.shp'))
    >>> counties = gpd.read_file(path_to_example('colorado-counties.geojson'))
    >>> counties.shape
    (64, 13)
    >>> rmnp_counties = cl.clip_shp(counties, rmnp)
    >>> rmnp_counties.shape
    (4, 13)
