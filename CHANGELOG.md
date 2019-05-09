# EarthPy Release Notes

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]
* A multi-point, polygon and line support to clip function (@lwasser, @nkorinek, #236)

## [0.6.8]
* Add multi-panel plotting to plot_bands (@lwasser, #316)
* Fix bug in plot_rgb where multipanel plots are blank (@lwasser, #313)
* Add example vignette for calculating and classifying NDVI with EarthPy (@jlpalomino, #266)

## [0.6.7]
* Add NoData masking support for `stack()` (@joemcglinchy, #282)
* Fix multiline messages to use `"` vs `"""` (@lwasser, #270)

## [0.6.6]
* Add sphinx gallery for vignettes and update get started page (@lwasser #279, #203)
* Add two example vignettes for using EarthPy with raster data (@lwasser)
* Fix bug in `bytescale()` - ensure math to calc range is floating point vals (@lwasser #282)
* Fix tests for `bytescale()` to ensure the bug raised in #282 is fixed / tested; also added comment to plot_rgb docs to ensure users consider nodata values before plotting (@lwasser #282)

## [0.6.5] - 2019-03-37
* Add continuous integration testing on osx via Travis CI (@mbjoseph #228)
* Add cbar legend to `plot_bands()` and scaling parameters (@lwasser #274)
* BUGFIX: `plot_bands()` doesn't plot single string titles properly + add test (@lwasser #258)
* Remove dependency on download library (@mbjoseph #249)
* BUGFIX: `draw_legend()` fails when classes are provided (@lwasser #253)
* Remove `earthpy.utils.fix_paths()` as it is not used in the package (@lwasser #259)
* Adding tests for `hillshade()` and improved docs (@jpalomino #260)
* Closing plots in tests (@lwasser #257)
* Added a code of conduct (@mbjoseph, #27)
* Added CI testing across python versions and on Windows (@mbjoseph, #228)
* Added tests for `EarthlabData` class (@mbjoseph, #37)

## [0.6.2] - 2019-02-19
We have made significant changes in preparation for a 1.0 release
on PyPI. If you have used EarthPy previously, please review the changes below.
You may need to update your code accordingly.

### Changed
- `normalized_diff()` function arguments have been flipped. Please update
all of your old code accordingly. Changes include:
    * Arguments are now provided as normalized_diff(b1, b2)
    * Math will be calculated (b1-b2) / (b1+b2)
    * Example: `ndvi = es.normalized_diff(b1=nir_band, b2=red_band)`
- `normalized_diff()` now:
    * returns unmasked array by default
    * returns masked array if there are nan values present
    * converts infinity values that result from division by zero to nan values
- `stack()` replaces `stack_raster_tifs()`, which is now deprecated.
The new `stack()` function
works similarly to `stack_raster_tifs`. Inputs parameters are now a list of
filepaths and an optional filepath parameter that when populated saves the
stacked raster array as a geotiff file. The default return is a
numpy ndarray.
- The parameter order for `bytescale` has changed:
   * PREVIOUS ORDER: data, cmin=None, cmax=None, high=255, low=0
   * NEW ORDER: data, high=255, low=0, cmin=None, cmax=None
- All plot functions moved to a new `earthpy.plot` module. To import plot
functions first import the plot module: `import earthpy.plot as ep`. Then you
can call functions as follows:
  * `ep.plot_rgb()`
  * `ep.draw_legend()`
  * `ep.hist()`
  * `ep.colorbar()`
  * `ep.plot_bands()`

### Added
* `draw_legend()` works now on different types of categorical raster plots.
* `colorbar()` has also been fixed to work given updates to `Matplotlib`
* A new mask function has been released as `mask_pixels()`.
* We now have tests through `pytest` that run on Travis CI.
* API documentation is now generated automatically from docstrings with `autodoc`.
* Example code in documentation is tested using `doctest`

### Deprecated
* `stack_raster_tifs()` has been deprecated and replaced with `stack()`.
