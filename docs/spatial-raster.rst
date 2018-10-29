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

All files in the list must be in the same Coordinate Refenence System (CRS) and
must have the same spatial extent for this to work properly.

``stack_raster_tifs`` takes 2 input parameters:

``band_paths``: list of file paths
      A list with paths to the bands you wish to stack. Bands
      will be stacked in the order given in this list.
``out_path``: string
      A path with a file name for the output stacked raster tif file.

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


Draw Legend
~~~~~~~~~~~~~~~~~~

The ``draw_legend`` function creates a custom legend with a box for each class in a raster using a maptplotlib image object, the unique classes in the image, and titles for each class.

This function requires the matplotlib Python plotting library.

The ``draw_legend`` function takes five input parameters, two of which are optional:

``im``: matplotlib image object
      This is the image returned from a call to imshow().
``classes``: list
      This is a list of unique values found in the numpy array that you wish to plot.
``titles``: list
      This is a list of a title or category for each unique value in your raster. This will act as a label that will go next to each box in your legend.
``bbox``: tuple (optional)
      This is the bbox_to_anchor argument that will place the legend anywhere on or around your plot.  The default value is (1.05, 1).
``loc``: integer (optional)
      This is the maptplotlib location value that can be used to specify the location of the legend on your plot. The default value is 2.        


The default output of ``draw_legend`` is:

* A matplotlib legend object to be displayed as part of your plot.


Example:

.. code-block:: python

    import matplotlib.pyplot as plt
    import earthpy.spatial as es

    # Create list of category names for legend labels
    category_names = ["Extreme",
                      "Very High",
                      "Moderate",
                      "Low",
                      "Very Low"]

   # Create list of values from the numpy array
   values = np.unique(example_raster.ravel())

    # Plot the data with earthpy custom legend
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(example_raster,
                   cmap=PiYG,
                   extent=example_extent)

    es.draw_legend(im, 
                   classes=values,
                   titles=category_names)