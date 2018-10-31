Earthpy Spatial Vector Data
===========================

The ``earthpy`` spatial module provides functions that wrap around the ``rasterio``
and ``geopandas`` to work with raster and vector data in Python.

Clip Points
-----------

The ``clip_points`` function clips vector points (Geopandas dataframe) to a
polygon vector object (Geopandas dataframe).

It can be executed independently or using the ``clip_shp`` function.

Both layers must be the same Coordinate Reference System (CRS).

``clip_points`` takes 2 input parameters:

``shp``: **geopandas dataframe**
    Point data to be clipped to clip_obj.

``clip_obj``: **geopandas dataframe**
    Vector layer (point, line, polygon) to be clipped to.

The ``clip_points`` function returns the following:

Points from shp clipped to polygon boundary of clip_obj.

Example:

.. code-block:: python

  import geopandas as gpd
  import clip_data as cl

  # Import shapefile using geopandas
  point_path = gpd.read_file("point_path_filename.shp")

  # Import clip object using geopandas
  boundary_path = gpd.read_file("boundary_path_filename.shp")

  point_clip = cl.clip_points(points, clip_obj)

Clip Vector Data
~~~~~~~~~~~~~~~~

The ``clip_shp`` function takes two geopandas GeoDataframe objects. The first
object is a point or line polygon GeoDataframe that needs to be spatially clipped.
The second object will be used as the spatial extent to clip the first object.

All inputs must be in the same Coordinate Refenence System (CRS).

``clip_shp`` takes 2 input parameters:

``shp``: geopandas GeoDataframe you wish to clip

``clip_obj``: geopandas GeoDataframe with the point or bounds you wish to clip to

The output of ``clip_shp`` is a geopandas GeoDataframe clipped to the clip object.

Example:

.. code-block:: python

    import geopandas as gpd
    import earthpy.clip as cl

    # Open shapefiles as geopandas GeoDataframe
    shp_2_clip = gpd.read_file(shapefile.shp)
    clip_obj = gpd.read_file(clip.shp)

    # Clip data
    clipped_gdf = cl.clip_shp(shp=shp_2_clip, clip_obj=clip_obj)
