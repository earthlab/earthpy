Get Started With EarthPy
========================

EarthPy is a python package devoted to working with spatial and remote sensing
data. EarthPy also contains an IO module that supports downloading data for the
Earth Lab earth analytics courses and any user with a url and a zip file.

EarthPy Module and Function Documentation
-----------------------------------------

All functions are included in the 5 earthpy modules:

- spatial
- plot
- clip
- mask
- io


Install EarthPy
---------------

Dependencies
~~~~~~~~~~~~

Earthpy has several Python package dependencies including : ``rasterio, geopandas, numpy``.
The easiest way to install EarthPy is to use the .. _Python: earth-analytics-python conda
environment https://github.com/earthlab/earth-analytics-python-env . This will
ensure that you have all of the required dependencies needed to run EarthPy.

Alternatively, to install EarthPy, use pip. ``--upgrade`` is optional but it
ensures that the package overwrites when you install and you have the current
version. If you don't have the package yet you can still use the ``--upgrade`` argument.

``pip install earthpy``

Once EarthPy is installed you can import it into python.

    >>> import earthpy as et

You can also chose to import any of the individual modules as follows:

    >>> import earthpy.spatial as es
    >>> import earthpy.plot as ep
    >>> import earthpy.clip as ec
    >>> import earthpy.mask as em

Data
~~~~

EarthPy contains a helper class that supports downloaded sets of pre-created data subsets
designed for the Earth Lab Earth Analytics online courses (see https://www.earthdatascience.org).
You can access these data subsets by using:

    >>> import earthpy as et
    >>> # View all available data keys
    >>> et.data.get_data()
    Available Datasets: ['california-rim-fire', 'co-flood-extras', 'cold-springs-fire', 'cold-springs-modis-h5', 'colorado-flood', 'cs-test-landsat', 'cs-test-naip', 'ndvi-automation', 'spatial-vector-lidar']
    >>> # Download data subset to your `$HOME/earth-analytics/data` directory
    >>> data = et.data.get_data('cold-springs-fire', verbose=False)
