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

Calculate Normalized Difference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``normalized_diff`` function takes two numpy arrays of the same shape and
calculates the normalized difference from them.

``normalized_diff`` takes two input parameters:

``b1``, ``b2``: arrays with the same shape
      Math will be calculated (b2-b1) / (b2+b1)

The ``normalized_diff`` function returns a masked array of the normalized difference with the same shape as the input arrays.

Example:

.. code-block:: python
    import numpy as np
    import earthpy.spatial as es

    b1 = np.array([[1, 2, 3, 4, 5],[11,12,13,14,15]])
    b2 = np.array([[6, 7, 8, 9, 10],[16,17,18,19,20]])

    # Calculate normalized difference
    ndiff = es.normalized_diff(b1, b2)
