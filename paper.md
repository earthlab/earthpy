
---
title: 'EarthPy: A Python package that makes it easier to explore and plot raster and vector data using open source Python tools.'
tags:
  - Python
  - gis
  - raster data
  - vector data
  - remote sensing
authors:
  - name: Leah Wasser
    orcid: 0000-0002-8177-6550
    affiliation: 1
  - name: Maxwell B. Joseph
    orcid: 0000-0002-7745-9990
    affiliation: 1
  - name: Joe McGlinchy
    orcid: 0000-0003-2135-0168
    affiliation: 1
  - name: Jenny Palomino
    orcid: 0000-0003-4879-9299
    affiliation: 1
  - name: Korinek, Nathan
    orcid: 0000-0003-0859-7246
    affiliation: 1
  - name: Chris Holdgraf
    orcid: 0000-0002-2391-0678
    affiliation: 2
  - name: Tim Head
    orcid: 0000-0003-0931-3698
    affiliation: 3
affiliations:
  - name: "Earth Lab, University of Colorado - Boulder"
    index: 1
  - name: "University of California - Berkeley, Project Jupyter"
    index: 2
  - name: ""Wild Tree Tech""
    index: 3
date: 28 October 2019
bibliography: paper.bib
---

# Summary & Purpose

`EarthPy` makes commonly performed spatial data exploration tasks easier for scientist by building upon functions in the widely used packages: `Rasterio` and `GeoPandas`. `EarthPy` is designed for users who are new to `Python` and spatial data with a focus on scientific data.

When a user is working with spatial data for research, there are a suite of data exploration activities that are often performed including:

1. Viewing histograms and plots of single bands within a remote sensing image to explore potential calibration and other data quality issues.
2. Creating basemaps that have legends with unique symbology.
3. Creating plots of images with colorbars.
4. Rendering RGB (and other composite) images of multi band spectral remote sensing images.
5. Masking clouds from a remote sensing image.
6. Limiting geographic extent of spatial data

The above operations are crucial to understanding a dataset and identifying issues that may need to be addressed with further data processing when beginning an analysis. In the `R` world, these tasks are quickly performed using the `raster` and `sp` packages. However, there isn't a tool that makes these tasks easy for users in the `Python` open source package landscape.


## EarthPy Audience

`EarthPy` was originally designed to support the Earth Analytics Education program at Earth Lab - University of Colorado, Boulder. Our program teaches students how to work with a suite of earth and environmental data using open source `Python`. All lessons are published as free open education resources on our online learning portal (https://www.earthdatascience.org). Through this publication process, we identified that many spatial data exploration and cleanup tasks which were performed regularly required many steps that could be easily wrapped into helper functions. We modeled these functions after those available in the `R` ecosystem, given the experience of the developers' many years of working and teaching with `R`.

`EarthPy` allows the user to streamline common geospatial data operations in a modular way. This reduces the amount of repetitive coding required to open and stack raster datasets, clip  the data to a defined area, and in particular, plotting data for investigation.   

# EarthPy Functionality

`EarthPy` is organized into several modules:

* [io: Input/output for data](https://earthpy.readthedocs.io/en/latest/api/earthpy.io.html): utility functions to download existing teaching data subsets or other data into a user's working directory (by default, this directory is: `~/earth-analytics/data`). The IO module supports downloading data for the Earth Lab Earth Analytics courses as well as any user with a URL to a compressed file.
* [mask: Mask out cloud and shadow covered pixels from raster data](https://earthpy.readthedocs.io/en/latest/api/earthpy.mask.html): helper functions to mask remote sensing images using a cloud mask or QA (i.e. quality) layer.
* [plot: Visualizing spatial data](https://earthpy.readthedocs.io/en/latest/api/earthpy.plot.html): plotting utilities including plotting a set of bands saved in a numpy array format, creating a custom colorbar, and custom legends with unique symbology.
* [spatial: Raster processing and analysis](https://earthpy.readthedocs.io/en/latest/api/earthpy.spatial.html): utilities to crop a set of bands to a defined spatial extent, create a hillshade, stack bands, and calculate normalized difference rasters.
* [clip: Vector data subsetting](https://earthpy.readthedocs.io/en/latest/api/earthpy.clip.html): A module to clip vector data using GeoPandas. Allows for clipping of points, lines, and polygon data within a specified polygon.

## EarthPy Vignettes

In addition to detailed API documentation and example code executed by doctest,
`EarthPy` documentation includes a long-form [examples gallery](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/index.html)
that demonstrates functionality using case studies. These longer case studies
provide an opportunity to document how to integrate the functionality contained in
different `EarthPy` modules, with an emphasis on compelling visualizations that
convey key concepts for spatial data processing.


# EarthPy in Context

## EarthPy Focus on Integration of Spatial Data By Scientists

`EarthPy` is an open source `Python` package that makes it easier to plot and work with both spatial raster and vector data using open source tools. `EarthPy`'s goal is to make working with spatial data easier for scientists who want to use open source `Python` tools for analysis and visualization.

`Earthpy` depends upon `GeoPandas` [@kelsey_jordahl_2019_3483425], which has a focus on vector data handling and analysis, and `Rasterio` [@gillies_2019], which facilitates input and output of raster data files as numpy arrays. It also requires `Matplotlib` for plotting operations.

To simplify dependency management and installation for non-experts, we maintain a version of EarthPy on the `conda-forge` channel, which installs the system
libraries upon which `EarthPy` depends. This combined with high-level wrapper
around `GeoPandas`, `Rasterio`, and `Matplotlib` [@Hunter:2007] lowers the barrier to entry for
people, particularly scientists, who are learning how to work with spatial data in
`Python`.

While there are other useful `Python` packages for working with vector data such as `PySAL` [@pysal2007] or raster data such as `GeoRasters`, `EarthPy` draws from both `GeoPandas` and `Rasterio` to integrate functionality for vector and raster into one package.


## EarthPy in the Classroom

`EarthPy` also supports education and teaching. The `io` module makes it easier for a student to download a suite of teaching data subsets and other data to a standard working directory (that is automatically created if it does not exist). This supports reproducibility of workflows in a classroom (or other) setting.

The `plot` module facilitates quick and early data exploration by introductory-level students for whom the intricancies of customizing plots with `Matplotlib` might be overwhelming. The `mask` and `spatial` modules both reduce the technical learning curve for spatial analysis with `Python`, which supports instructors in focusing on the key scientific concepts behind the code.

The vignettes developed with `EarthPy` also provide easily adaptable starting points for in-class exercises that help students learn key spatial concepts using scientific data.

# Acknowledgements

There have been many [contributors to earthpy](https://github.com/earthlab/earthpy/graphs/contributors) that we are thankful for. We are also thankful for the feedback that we recieved through the software review implemented by pyOpenSci. Specifically we thank Luiz Irber who has served as an editor for this review and the two reviewers: Sean Gillies and Rohit Goswami.

# References
