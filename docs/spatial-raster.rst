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
~~~~~~~~~~~~~~~~~~

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
