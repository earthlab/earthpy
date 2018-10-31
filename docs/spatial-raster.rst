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

    red_band = np.array([[1, 2, 3, 4, 5],[11,12,13,14,15]])
    nir_band = np.array([[6, 7, 8, 9, 10],[16,17,18,19,20]])

    # Calculate normalized difference
    ndiff = es.normalized_diff(b2=nir_band, b1=red_band)


Plot Raster File Bands
~~~~~~~~~~~~~~~~~~~~~~

The ``plot_bands`` function displays a quick visualization of each raster file band
individually as matplotlib plot(s). This function is helpful when first exploring raster data.

``plot_bands`` takes 6 input parameters:


``arr``: numpy array
  An n-dimensional numpy array
``title``: str or list
  Title of one band, or list of titles with one title per band
``cmap``: str
  Colormap name ("greys" by default)
``cols``: int
  Number of columns for plot grid
``figsize``: tuple - optional
  Figure size in inches ((12, 12) by default)
``extent``: tuple - optional
  Bounding box that the data will fill: (minx, miny, maxx, maxy)

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

Plot RGB 
~~~~~~~~

The ``plot_rgb`` function takes a 3 dimensional numpy array that contains image data and plots the 3 bands together to create a composite image.

``plot_rgb`` takes 8 input parameters:

``arr``: numpy array
      An n-dimension numpy array in rasterio band order (bands, x, y)
``rgb``: list
      Indices of the three bands to be plotted (default = 0,1,2)
``extent``: tuple - optional
      The extent object that matplotlib expects (left, right, bottom, top)
``title``:  string- optional 
      String representing the title of the plot
``ax``: matplotlib AxesSubplot 
      The ax object where the ax element should be plotted. Default = none
``figsize``: tuple
      The x and y integer dimensions of the output plot if preferred to set.
``stretch``: boolean
      If True, a linear stretch will be applied
``str_clip``: int
      The % of clip to apply to the stretch. Default = 2 (2 and 98)

The ``plot_rgb`` function returns the following:

``fig, ax``: figure object, axes object
      The figure and axes object associated with the 3 band image.  If the ax keyword is specified, the figure return will be None.

Example:

.. code-block:: python

    import matplotlib as plt
    import earthpy.spatial as es

    fig, ax1 = plt.subplots(figsize=(12, 6))
    es.plot_rgb(naip_image,
                rgb=[0, 1, 2],
                extent=naip_extent,
                title="NAIP 2017 Post Fire RGB Image",
                ax=ax1)

Histogram 
~~~~~~~~~

The ``hist()`` function plots a histogram of each layer in a raster stack converted into a numpy array for quick visualization.

``hist()`` takes 6 input parameters:

``arr``: numpy array
      An dimension numpy array
``title``: list
      A list of title values that should either equal the number of bands or be empty, default = none
``colors``: list
      A list of color values that should either equal the number of bands or be a single color, (purple = default)
``cols``: int 
      The number of columns you want to plot in
``bins``: int
      The number of bins to calculate for the histogram
``figsize``: tuple
      The figsize if you'd like to define it. default: (12, 12)
    
The ``hist()`` function returns the following:

``fig, ax or axs`` : figure object, axes object
      The figure and axes object(s) associated with the histogram.

Example:

.. code-block:: python

    import earthpy.spatial as es

    colors = ['r', 'k', 'b', 'g', 'k', 'y', 'y']
    titles = ["Red Band", "Near Infrared (NIR) Band", "Blue/Green Band",
              "Green Band", "Near Infrared (NIR) Band",
              "Mid-infrared Band", "Mid-infrared Band"]

    # Plot histogram
    es.hist(modis_bands_pre_data,
            colors=colors,
            title=titles,
            cols=2)

Hillshade
~~~~~~~~~

The ``hillshade`` function takes a numpy array containing elevation data and creates a hillshade array.

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

