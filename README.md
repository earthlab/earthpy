[![DOI](https://joss.theoj.org/papers/10.21105/joss.01886/status.svg)](https://doi.org/10.21105/joss.01886)
[![pyOpenSci](https://tinyurl.com/y22nb8up)](https://github.com/pyOpenSci/software-review/issues/3)
[![Build Status](https://travis-ci.org/earthlab/earthpy.svg?branch=master)](https://travis-ci.org/earthlab/earthpy)
[![Build status](https://ci.appveyor.com/api/projects/status/xgf5g4ms8qhgtp21?svg=true)](https://ci.appveyor.com/project/earthlab/earthpy)
[![codecov](https://codecov.io/gh/earthlab/earthpy/branch/master/graph/badge.svg)](https://codecov.io/gh/earthlab/earthpy)
[![Docs build](https://readthedocs.org/projects/earthpy/badge/?version=latest)](https://earthpy.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://img.shields.io/badge/code%20style-black-000000.svg)

# EarthPy

![PyPI](https://img.shields.io/pypi/v/earthpy.svg?color=purple&style=plastic)
![PyPI - Downloads](https://img.shields.io/pypi/dm/earthpy.svg?color=purple&label=pypi%20downloads&style=plastic)
![Conda](https://img.shields.io/conda/v/conda-forge/earthpy.svg?color=purple&style=plastic)
![Conda](https://img.shields.io/conda/dn/conda-forge/earthpy.svg?color=purple&label=conda-forge%20downloads&style=plastic)

EarthPy makes it easier to plot and manipulate spatial data in Python.

## Why EarthPy?

Python is a generic programming language designed to support many different applications. Because of this, many commonly
performed spatial tasks for science including plotting and working with spatial data take many steps of code. EarthPy
builds upon the functionality developed for raster data (rasterio) and vector data (geopandas) in Python and simplifies the
code needed to:

* [Stack and crop raster bands from data such as Landsat into an easy to use numpy array](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_raster_stack_crop.html)
* [Work with masks to set bad pixels such a those covered by clouds and cloud-shadows to NA (`mask_pixels()`)](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_stack_masks.html#sphx-glr-gallery-vignettes-plot-stack-masks-py)
* [Plot rgb (color), color infrared and other 3 band combination images (`plot_rgb()`)](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_rgb.html)
* [Plot bands of a raster quickly using `plot_bands()`](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_bands_functionality.html)
* [Plot histograms for a set of raster files.](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_hist_functionality.html)
* [Create discrete (categorical) legends](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_draw_legend_docs.html)
* [Calculate vegetation indices such as Normalized Difference Vegetation Index (`normalized_diff()`)](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_calculate_classify_ndvi.html)
* [Create hillshade from a DEM](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/plot_dem_hillshade.html)

EarthPy also has an `io` module that allows users to

1. Quickly access pre-created data subsets used in the earth-analytics courses hosted
on [www.earthdatascience.org](https://www.earthdatascience.org)
2. Download other datasets that they may want to use in their workflows.

EarthPy's design was inspired by the `raster` and `sp` package functionality available to `R` users.

## View Example EarthPy Applications in Our Documentation Gallery  

Check out our [vignette gallery](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/index.html) for
applied examples of using EarthPy in common spatial workflows.

## Install

EarthPy can be installed using `pip`, but we **strongly** recommend that you install it using conda and the `conda-forge` channel.

### Install Using Conda / conda-forge Channel (Preferred)

If you are working within an Anaconda environment, we suggest that you install EarthPy using
`conda-forge`

```bash
$ conda install -c conda-forge earthpy
```

Note: if you want to set conda-forge as your default conda channel, you can use the following install workflow.
We recommmend this approach. Once you have run conda config, you can install earthpy without specifying a channel.

```bash
$ conda config --add channels conda-forge
$ conda install earthpy
```


### Install via Pip

We strongly suggest that you install EarthPy using conda-forge given pip can be more prone to 
spatial library dependency conflicts. However, you can install earthpy using pip.

To install EarthPy via `pip` use:

```bash
$ pip install --upgrade earthpy
```

Once you have successfully installed EarthPy, you can import it into Python.

```python
>>> import earthpy.plot as ep
```

Below is a quick example of plotting multiple bands in a numpy array format.

```python
>>> arr = np.random.randint(4, size=(3, 5, 5))
>>> ep.plot_bands(arr, titles=["Band 1", "Band 2", "Band 3"])
>>> plt.show()
```

## Active Maintainers

We welcome contributions to EarthPy. Below are the current active package maintainers. Please see our
[contributors file](https://earthpy.readthedocs.io/en/latest/contributors.html) for a complete list of all
of our contributors.

<a title="Leah Wasser" href="https://www.github.com/lwasser"><img width="60" height="60" alt="Leah Wasser" class="pull-left" src="https://avatars.githubusercontent.com/u/7649194?size=120" /></a>
<a title="Max Joseph" href="https://www.github.com/mbjoseph"><img width="60" height="60" alt="Max Joseph" class="pull-left" src="https://avatars.githubusercontent.com/u/2664564?size=120" /></a>
<a title="Joseph McGlinchy" href="https://www.github.com/joemcglinchy"><img width="60" height="60" alt="Joseph McGlinchy" class="pull-left" src="https://avatars.githubusercontent.com/u/4762214?size=120" /></a>
<a title="Jenny Palomino" href="https://www.github.com/jlpalomino"><img width="60" height="60" alt="Jenny Palomino" class="pull-left" src="https://avatars.githubusercontent.com/u/4017492?size=120" /></a>
<a title="Nathan Korinek" href="https://www.github.com/nkorinek"><img width="60" height="60" alt="Nathan Korinek" class="pull-left" src="https://avatars.githubusercontent.com/u/38253680?size=120" /></a>


## Contributors

We've welcome any and all contributions. Below are some of the
contributors to EarthPy. We are currently trying to update this list!!

<a title="Sean Gillies" href="https://www.github.com/sgillies"><img width="60" height="60" alt="Michelle Roby" class="pull-left" src="https://avatars.githubusercontent.com/u/33697?size=120" /></a>
<a title="Tim Head" href="https://www.github.com/betatim"><img width="60" height="60" alt="Tim Head" class="pull-left" src="https://avatars.githubusercontent.com/u/1448859?size=120" /></a>
<a title="Chris Holdgraf" href="https://www.github.com/choldgraf"><img width="60" height="60" alt="Michelle Roby" class="pull-left" src="https://avatars.githubusercontent.com/u/1839645?size=120" /></a>
<a title="Michelle Roby" href="https://www.github.com/mirob9363"><img width="60" height="60" alt="Michelle Roby" class="pull-left" src="https://avatars.githubusercontent.com/u/42818395?size=120" /></a>

## How to Contribute

We welcome contributions to EarthPy! Please be sure to check out our
[contributing guidelines](https://earthpy.readthedocs.io/en/latest/contributing.html)
for more information about submitting pull requests or changes to EarthPy.

## License & Citation

[BSD-3](https://github.com/earthlab/earthpy/blob/master/LICENSE)

### Citation Information

When citing EarthPy, please cite our [JOSS paper](https://doi.org/10.21105/joss.01886):

```
@article{Wasser2019EarthPy,
	journal = {Journal of Open Source Software},
	doi = {10.21105/joss.01886},
	issn = {2475-9066},
	number = {43},
	publisher = {The Open Journal},
	title = {EarthPy: A Python package that makes it easier to explore and plot raster and vector data using open source Python tools.},
	url = {https://doi.org/10.21105/joss.01886},
	volume = {4},
	author = {Wasser, Leah and Joseph, Maxwell and McGlinchy, Joe and Palomino, Jenny and Korinek, Nathan and Holdgraf, Chris and Head, Tim},
	pages = {1886},
	date = {2019-11-13},
	year = {2019},
	month = {11},
	day = {13},
}

```
