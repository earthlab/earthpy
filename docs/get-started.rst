Get Started With Earthpy
========================

Earthpy is a python package devoted to working with spatial and remote sensing data.
Earthpy Also contains an IO module that supports downloading data for the earth
lab earth analytics courses.

Earthpy Modules
---------------

- Spatial: Various functions for loading, manipulating, and displaying raster data
  - ``create_raster_stack``: generates a single multi-band raster from separate raster TIFs,
  such as a collection of single-band TIFs from Landsat
  - ``normalized_diff``: calculate a normalized difference for two bands of a multi-band raster
  - ``hillshade``: create a hillshade array from image elevation data
  - ``crop_image``: crop raster data to a polygon
  - Custom plotting shortcuts, such as ``colorbar`` for appropriately sized legends, ``create_legend`` for
  legends showing a color for each class of a raster, ``plot_bands`` for creating a grid of images
  showing each individual band of a raster, and ``plot_rgb`` for quickly generating
  composite images or false color images from raster bands.

- IO: Handles data search and retrieval from EarthLab, supporting analytics courses
  available `here <https://www.earthdatascience.org/courses/>`_.

- Utils: Handles path fixes for EarthLab image retrieval -- new utils module forthcoming

Installation
------------

Dependencies
~~~~~~~~~~~~

Earthpy has several Python package dependencies including : ``rasterio, geopandas, numpy``.

To install earthpy, use pip. ``--upgrade`` is optional but it ensures that the package
overwrites when you install and you have the current version. If you don't have
the package yet you can still use the ``--upgrade argument``.

``pip install --upgrade git+https://github.com/earthlab/earthpy.git``

Then import it into python.

    >>> import earthpy as et

To import the spatial module use:

    >>> import earthpy.spatial as es
