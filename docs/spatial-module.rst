Earthpy Spatial
========================

The ``earthpy`` spatial module provides functions that wrap around the ``rasterio``
and ``geopandas`` to work with raster and vector data in Python.

Raster Data
-----------

Stack Raster Files
~~~~~~~~~~~~~~~~~~

The ``stack_raster_tifs`` function takes a list of raster paths and turns that list
into an

1. output raster stack in numpy format and
2. a stacked geotiff on your hard drive.

All files in the list must be in the same crs and must have the same spatial extent
for this to work properly.

stack_raster_tifs takes 2 input parameters:

``band_paths``: list of file paths
      A list with paths to the bands you wish to stack. Bands
      will be stacked in the order given in this list.
``out_path``: string
      A path with a file name for the output stacked raster tif file.

and returns:

``a geotiff``: saved at the file_path location specified

``arr``: a numpy array containing all of the stacked data

``meta``: DICT - the updated metadata for the numpy array in rasterio dictionary format

Example:

.. code-block:: python

    from glob import glob

    # Create file name list
    all_file_paths = glob("path/here/*band*.tif")

    file_path = "data/location/filename.tif"

    # Stack landsat tif files 
    arr, arr_meta = es.stack_raster_tifs(all__paths, file_path)
