Earthpy Spatial Vector Data
===========================

The ``earthpy`` spatial module provides functions that wrap around the ``rasterio``
and ``geopandas`` to work with raster and vector data in Python.

Clip Vector Data
~~~~~~~~~~~~~~~~

The ``clip_shp`` function takes a geopandas dataframe and a point or bounding box clip object and spatially clips the dataframe to the clip object.

All inputs must be in the same Coordinate Refenence System (CRS).

``clip_shp`` takes 2 input parameters:

``shp``: geopandas dataframe you wish to clip

``clip_obj``: geopandas dataframe with the point or bounds you wish to clip to

The output of ``clip_shp`` is a geopandas dataframe clipped to the clip object.

Example:

.. code-block:: python

    import geopandas as gpd
    import earthpy.clip as cl

    # Open shapefiles as geopandas dataframes
    shp = gpd.read_file(shapefile.shp)
    clip_obj = gpd.read_file(clip.shp)

    # Clip data
    clip_shp = cl.clip_shp(shp, clip_obj)
