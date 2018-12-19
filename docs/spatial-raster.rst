Earthpy Spatial Raster Data
===========================

The ``earthpy`` spatial module provides functions that wrap around the
``rasterio`` and ``geopandas`` to work with raster and vector data in Python.

Stack Raster Files
~~~~~~~~~~~~~~~~~~
The ``stack`` function turns a list of raster paths into:
1. a stacked geotiff on your hard drive and
2. (optional) an output raster stack in numpy format with associated metadata.

All files in the list must be in the same Coordinate Reference System (CRS) and
must have the same spatial extent for this to work properly.

``stack`` takes 3 input parameters:

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

``meta``: dictionary - the updated metadata for the numpy array in rasterio
metadata dictionary format

Example:

    >>> import os
    >>> import earthpy.spatial as es
    >>> from earthpy.io import path_to_example

    >>> band_fnames = ["red.tif", "green.tif", "blue.tif"]
    >>> band_paths = [path_to_example(fname) for fname in band_fnames]
    >>> destfile = "./stack_result.tif"
    >>> arr, arr_meta = es.stack(band_paths, out_path=destfile, write_raster=True)
    >>> arr.shape
    (3, 373, 485)
    >>> os.path.isfile(destfile)
    True

    >>> # optionally, clean up example output
    >>> os.remove(destfile)


Draw Legend
~~~~~~~~~~~

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

Calculate Normalized Difference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``normalized_diff`` function takes two numpy arrays of the same shape and
calculates the normalized difference from them.

``normalized_diff`` takes two input parameters:

``b1``, ``b2``: arrays with the same shape
      Math will be calculated (b2-b1) / (b2+b1)

The ``normalized_diff`` function returns a masked array of the normalized difference with the same shape as the input arrays.

Example:

    >>> import numpy as np
    >>> import earthpy.spatial as es

    >>> red_band = np.array([[1, 2, 3, 4, 5],[11,12,13,14,15]])
    >>> nir_band = np.array([[6, 7, 8, 9, 10],[16,17,18,19,20]])
    >>> es.normalized_diff(b2=nir_band, b1=red_band)
    masked_array(
      data=[[0.7142857142857143, 0.5555555555555556, 0.45454545454545453,
             0.38461538461538464, 0.3333333333333333],
            [0.18518518518518517, 0.1724137931034483, 0.16129032258064516,
             0.15151515151515152, 0.14285714285714285]],
      mask=[[False, False, False, False, False],
            [False, False, False, False, False]],
      fill_value=1e+20)


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

    >>> import matplotlib.pyplot as plt
    >>> import earthpy.spatial as es
    >>> from earthpy.io import path_to_example
    >>> import rasterio as rio

    >>> titles = ['Red', 'Green', 'Blue']
    >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
    ...     es.plot_bands(src.read(), title=titles) #doctest: +ELLIPSIS
    (<Figure size 1200x1200 with 3 Axes>, ...)




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

    >>> import geopandas as gpd
    >>> import rasterio as rio
    >>> import earthpy.spatial as es

    >>> # clip an RGB image to the extent of Rocky Mountain National Park
    >>> rmnp = gpd.read_file(path_to_example("rmnp.shp"))
    >>> with rio.open(path_to_example("rmnp-rgb.tif")) as raster:
    ...     src_image = raster.read()
    ...     out_image, out_meta = es.crop_image(raster, rmnp)
    >>> out_image.shape
    (3, 265, 281)
    >>> src_image.shape
    (3, 373, 485)



Plot RGB
~~~~~~~~

The ``plot_rgb`` function takes a 3 dimensional numpy array that contains image data and plots the 3 bands together to create a composite image.

``plot_rgb`` takes 8 input parameters:

``arr``: numpy ndarray
      A numpy N-dimensional array in rasterio band order (bands, x, y)
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
      The figure and axes object associated with the 3 band image.  If the ax
      keyword is specified, the figure return will be None.

Example:

    >>> import matplotlib.pyplot as plt
    >>> import rasterio as rio
    >>> import earthpy.spatial as es
    >>> from earthpy.io import path_to_example

    >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
    ...     img_array = src.read()
    >>> es.plot_rgb(img_array) #doctest: +ELLIPSIS
    (<Figure size 1000x1000 with 1 Axes>, ...)

Histogram
~~~~~~~~~

The ``hist()`` function plots a histogram of each layer in a raster stack
converted into a numpy array for quick visualization.

``hist()`` takes 6 input parameters:

``arr``: numpy array
      An dimension numpy array
``title``: list
      A list of title values that should either equal the number of bands or be
      empty, default = none
``colors``: list
      A list of color values that should either equal the number of bands or be
      a single color, (purple = default)
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

    >>> import matplotlib.pyplot as plt
    >>> import rasterio as rio
    >>> import earthpy.spatial as es
    >>> from earthpy.io import path_to_example

    >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
    ...     img_array = src.read()

    >>> es.hist(img_array,
    ...     colors=['r', 'g', 'b'],
    ...     title=['Red', 'Green', 'Blue'],
    ...     cols=3,
    ...     figsize=(8, 3)) #doctest: +ELLIPSIS
    (<Figure size 800x300 with 3 Axes>, ...)


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

    >>> import matplotlib.pyplot as plt
    >>> import rasterio as rio
    >>> import earthpy.spatial as es
    >>> from earthpy.io import path_to_example

    >>> with rio.open(path_to_example('rmnp-dem.tif')) as src:
    ...     dem = src.read()
    >>> print(dem.shape)
    (1, 187, 152)

    >>> squeezed_dem = dem.squeeze() # remove first dimension
    >>> print(squeezed_dem.shape)
    (187, 152)

    >>> shade = es.hillshade(squeezed_dem)
    >>> plt.imshow(shade) #doctest: +ELLIPSIS
    <matplotlib.image.AxesImage object at 0x...>
