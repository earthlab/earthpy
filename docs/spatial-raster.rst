Earthpy Spatial Raster Data
===========================

The ``earthpy`` spatial module provides functions that wrap around the ``rasterio``
and ``geopandas`` to work with raster and vector data in Python.

Stack Raster Files
~~~~~~~~~~~~~~~~~~

The ``stack_raster_tifs`` function takes a list of raster paths and turns that list
into an

1. a stacked geotiff on your hard drive and
2. (optionally) an output raster stack in numpy format with associated metadata.

All files in the list must be in the same Coordinate Reference System (CRS) and
must have the same spatial extent for this to work properly.

``stack_raster_tifs`` takes 3 input parameters:

``band_paths``: list of file paths
      A list with paths to the bands you wish to stack. Bands
      will be stacked in the order given in this list.
``out_path``: string
      A path with a file name for the output stacked raster tif file.
``arr_out``: boolean
      A boolean argument to designate what is returned in the stacked
      raster tif output.

The default output of ``stack_raster_tiffs`` is:

* ``a geotiff``: saved at the ``destfile`` location specified


The stack_raster_tiffs function returns the following if ``arr_out=True``:

``arr``: a numpy array containing all of the stacked data

``meta``: dictionary - the updated metadata for the numpy array in rasterio metadata dictionary format

Example:

.. code-block:: python

    from glob import glob
    import earthpy.spatial as es

    # Create file name list
    all_file_paths = glob("path/here/*band*.tif")

    destfile = "data/location/filename.tif"

    # Stack landsat tif files
    arr, arr_meta = es.stack_raster_tifs(all__paths, destfile)


Plot Raster File Bands
~~~~~~~~~~~~~~~~~~~~~~

The ``plot_bands`` function displays a quick visualization of each raster file band
individually as matplotlib plot(s). This function is helpful when first exploring raster data.

``plot_bands`` takes 6 input parameters:

``arr``: numpy array
    a n dimension numpy array
``title``: str or list
    string for a single title of one band or list of x titles for x bands in plot
``cmap``: str
    cmap name, string the colormap that you wish to use (greys = default)
``cols``: int
    the number of columns you want to plot in
``figsize``: tuple - optional
    the figure size if you'd like to define it. default: (12, 12)
``extent``: list or geopandas dataframe - optional
    an extent object for plotting. Values should be in the order: minx, miny, maxx, maxy

Example:

.. code-block:: python

    import earthpy.spatial as es

    titles = ["Red Band", "Green Band", "Blue Band", "Near Infrared (NIR) Band"]

    # Plot all bands of a raster tif
    es.plot_bands(naip_image,
                  title=titles,
                  figsize=(12,5),
                  cols=2)


Crop Image
~~~~~~~~~~

The ``crop_image`` function takes a single rasterio object and crops the image
using specified geometry objects.

``crop_image`` takes 3 input parameters:

``raster``: rasterio DatasetReader object
      The rasterio object to be cropped. Ideally this object is opened in a
      context manager to ensure the file is properly closed.
``geoms``: geopandas object or list of polygons in GEOJSON-like structure
      If the crop extent is a list, then the format should be GEOJSON-like
      dictionaries specifying the boundaries of pixels in the raster to be kept.
      If the crop extent is a geopandas object then the total_bounds of the object
      is used to specify what pixels in the raster are kept. All data outside of
      the specified polygons will be set to nodata.
``all_touched``: boolean
      From rasterio: Include a pixel in the mask if it touches any of the shapes.
      If False, include a pixel only if its center is within one ofthe shapes,
      or if it is selected by Bresenham's line algorithm.
      Default is True in this function.

The ``crop_image`` function returns the following:

``out_image``: masked numpy array
      A masked numpy array that is masked / cropped to the geoms object extent.
``out_meta``: dictionary
      A dictionary containing the updated metadata for the cropped raster.
      Specifically the extent (shape elements) and transform properties are updated.

Example:

.. code-block:: python

    import geopandas as gpd
    import rasterio as rio
    import earthpy.spatial as es

    # Import geoms boundary
    geoms = gpd.read_file("path_here_geoms_filename.shp")

    # Open raster object in context manager
    with rio.open("path_here_raster_filename.tif") as raster:
        # Crop image using crop_image
        out_image, out_meta = es.crop_image(raster, geoms)


Hillshade
~~~~~~~~~

The ``hillshade`` function takes a numpy array containing elevation data and creates
a hillshade array.

``hillshade`` takes 3 input parameters:

``arr``: a n dimension numpy array
      The numpy array containing elevation data that will be used to calculate
      the hillshade array.
``azimuth``: float
      The angular direction of the sun, measured from north in clockwise degrees
      from 0 to 360.
      Default is 30.
``angle_altitude``: float
      The slope or angle of the illumination source above the horizon from 0 (on
      the horizon) to 90 (overhead).
      Default is 30.

The ``hillshade`` function returns the following:

``a numpy array``: numpy array
      A numpy array containing hillshade values.

Example:

.. code-block:: python

    import rasterio as rio
    import earthpy.spatial as es

    # Open arr numpy array
    with rio.open("path_her_arr_filename.tif") as src:
        arr = src.read()

    # Create hillshade numpy array
    hillshade = es.hillshade(arr, 315, 45)
