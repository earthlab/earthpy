[![DOI](https://zenodo.org/badge/122149160.svg)](https://zenodo.org/badge/latestdoi/122149160)
[![Build Status](https://travis-ci.org/earthlab/earthpy.svg?branch=master)](https://travis-ci.org/earthlab/earthpy)
[![Build status](https://ci.appveyor.com/api/projects/status/xgf5g4ms8qhgtp21?svg=true)](https://ci.appveyor.com/project/earthlab/earthpy)
[![codecov](https://codecov.io/gh/earthlab/earthpy/branch/master/graph/badge.svg)](https://codecov.io/gh/earthlab/earthpy)
[![Docs build](https://readthedocs.org/projects/earthpy/badge/?version=latest)](https://earthpy.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://img.shields.io/badge/code%20style-black-000000.svg)

# EarthPy

[![PyPI version](https://badge.fury.io/py/earthpy.svg)](https://badge.fury.io/py/earthpy)
![PyPI - Downloads](https://img.shields.io/pypi/dm/earthpy.svg?color=purple&label=pypi%20downloads&style=plastic)
![Conda](https://img.shields.io/conda/dn/conda-forge/earthpy.svg?color=purple&label=conda-forge%20downloads&style=popout)

EarthPy is makes it easier to plot and manipulate spatial data in Python.

## Why EarthPy?

Python is a generic programming language designed to support many different applications. Because of this, many commonly
performed spatial tasks for science including plotting and working with spatial data take many steps of code. EarthPy 
takes advantage of functionality developed for raster data (rasterio) and vector data (geopandas) and simplifies the 
code needed to :

* Stack raster bands from data such as Landsat into an easy to use numpy array
* Plot rgb and other 3 band combination images
* View histograms of sets of raster 
* Create discrete (categorical) legends

EarthPy also has an io module that allows users to 

1. Quickly access pre-created datasubsets used in the earth-analytics courses hosted 
on [earthdatascience.org](https://www.earthdatascience.org) 
2. Download other datasets that they may want to use in their workflows.

## View Example EarthPy Applications in Our Documentation Gallery  

Check out our [vignette gallery](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/index.html) for 
applied examples of using earthpy in common spatial workflows. 


## Install

To install, use `pip` or `conda-forge`. We encourage you to use `conda-forge` if you are a conda users. 

### Install via Pip

To install earthPy via `pip` use:

```bash
$ pip install --upgrade earthpy
```

### Install Using Conda / conda-forge Channel

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


Once you have successfully installed EarthPy, you can import it into Python.

```python
>>> import earthpy as et
```

Below is a quick example of plotting multiple bands in a numpy array format.

```python
>>> arr = np.random.randint(4, size=(3, 5, 5))
>>> ep.plot_bands(arr, titles=["Band 1", "Band 2", "Band 3"])
>>> plt.show()
```

## Active Contributors

- Leah Wasser
- Max Joseph
- Joe McGlinchy
- Tim Head
- Chris Holdgraf
- Jenny Palomino

## License

[BSD-3](https://github.com/earthlab/earthpy/blob/master/LICENSE)

