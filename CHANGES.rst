Earthpy Release notes
=====================

January 2019 Updates
~~~~~~~~~~~~~~~~~~~~

We have made significant changes to ``earthpy`` in preparation for a 1.0 release
on pypi. If you have used ``earthpy`` previously, please review the changes below.
You may need to update your code accordingly.

Enhancements & New Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~

January 2019 Updates
--------------------

**Updates to existing functions**

Breaking Changes
----------------

* ``normalized_diff()`` function arguments have been flipped. Please update
all of your old code accordingly. Changes include:
    * arguments are now provided as normalized_diff(b1, b2)
    * Math will be calculated (b1-b2) / (b1+b2)
    * Example: ``ndvi = es.normalized_diff(b1=nir_band, b2=red_band)``
* ``normalized_diff`` now returns unmasked array by default
* ``normalized_diff`` now returns masked array if there are nan values present
* ``normalized_diff`` converts infinity values that result from division by zero to nan values
* ``stack_raster_tifs()`` is now deprecated and replaced with ``stack()``. You
should see a deprecation warning when calling it. The new ``stack()`` function
works similarly to ``stack_raster_tifs``. Inputs parameters are now a list of
filepaths and an optional filepath parameter that when populated saves the
stacked raster array as a geotiff file. The default return is a
numpy ndarray.
* The parameter order for ``bytescale`` has changed:
   - PREVIOUS ORDER: data, cmin=None, cmax=None, high=255, low=0
   - NEW ORDER: data, high=255, low=0, cmin=None, cmax=None

**Plot Function Updates**
All plot functions have moved to a new ``earthpy.plot`` module. To import plot
functions first import the plot module: ``import earthpy.plot as ep``. Then you
can call functions as follows:

* ``ep.plot_rgb()``
* ``ep.draw_legend()``
* ``ep.hist()``
* ``ep.colorbar()``
* ``ep.plot_bands()``

Enhancements
------------
* ``draw_legend()`` works now on different types of categorical raster plots.
* ``colorbar()`` has also been fixed to work given updates to ``matplotlib``
* A new mask function has been released as ``mask_pixels()``.

**Infrastructure Updates**
* **Enhanced testing:** We have updated our infrastructure to include ``pytest``
run via TravisCI continuous integration for all testing.
* **Docs:** We have implemented ``autodoc`` functionality through ReadTheDocs.io.
This ensures that documentation is automatically build using function docstrings.

Deprecations
------------
* ``stack_raster_tifs()`` has been deprecated and replaced with the ``stack()``
function. See details above.
