
---
title: EarthPy: A Python package that makes it easier to explore and plot raster and vector data using open source Python tools.'
tags:
  - Python
  - gis
  - raster data
  - vector data
  - remote sensing
authors:
  - name: Leah Wasser 
    orcid: 0000-0002-8177-6550
    affiliation: "Earth Lab, University of Colorado - Boulder" # (Multiple affiliations must be quoted)
  - name: Maxwell B. Joseph
    orcid: 0000-0002-7745-9990
    affiliation: "Earth Lab, University of Colorado - Boulder"
  - name: Korinek, Nathan
    orcid: 0000-0003-0859-7246
    affiliation: "Earth Lab, University of Colorado - Boulder"
  - name: Jenny Palomino 
    orcid: 0000-0003-4879-9299
    affiliation: "Earth Lab, University of Colorado - Boulder"
  - name: Chris Holdgraf 
    orcid: 0000-0002-2391-0678
    affiliation: "Berkely, Project Jupyter"
date: 23 October 2019
bibliography: paper.bib??
# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# We have a zenodo doi -- how does JOSS handle this?
---

# Summary & Purpose

`EarthPy` makes commonly performed spatial data exploration tasks easier by building upon commonly used functionality available in the widely used packages: `Rasterio` and `GeoPandas`. `EarthPy` is designed for users who are new to `Python` and spatial data with a focus on scientific data. 

When a user is working with spatial data for research, there are a suite of data exploration activities that are often performed including: 

1. Viewing histograms and plots of single bands within a remote sensing image to explore potential calibration and other data quality issues.
2. Creating basemaps that have legends with unique symbology.
3. Creating plots of images with colorbars.
4. Rendering RGB (and other composite) images of multi band spectral remote sensing images. 
5. Masking clouds from a remote sensing image.

The above operations are crucial to understanding a dataset and identifying issues that may need to be addressed with further data processing when beginning an analysis. In the `R` world, these tasks are quickly performed using the `raster` and `sp` packages. However, there isn't a tool that makes these tasks easy for users in the `Python` open source package landscape. 


## EarthPy Audience 

`EarthPy` was originally designed to support the Earth Analytics Education program at Earth Lab - University of Colorado, Boulder. Our program teaches students how to work with a suite of earth and environmental data using open source `Python`. All lessons are published as free open education resources on our online learning portal (https://www.earthdatascience.org). Through this publication process, we identified that suites of spatial data exploration and cleanup tasks that were performed regularly required many steps that could be easily wrapped into helper functions. We modeled these functions after those available in the `R` ecosystem given the experience of many years of teaching with `R`. 

# EarthPy Functionality

`EarthPy` is organized into several modules: 

* [io: Input/output for data](https://earthpy.readthedocs.io/en/latest/api/earthpy.io.html): utility functions to download existing teaching data subsets or other data into a user's working directory (by default, this directory is: `~/earth-analytics/data`). The IO module supports downloading data for the Earth Lab Earth Analytics courses as well as any user with a URL to a compressed file.
* [mask: Mask out cloud and shadow covered pixels from raster data](https://earthpy.readthedocs.io/en/latest/api/earthpy.mask.html): helper functions to mask remote sensing images using a cloud mask or QA layer. 
* [plot: Visualizing spatial data](https://earthpy.readthedocs.io/en/latest/api/earthpy.plot.html): plotting utilities including plotting a set of bands saved in a numpy array format, creating a custom colorbar, and custom legends with unique symbology.
* [spatial: Raster processing and analysis](https://earthpy.readthedocs.io/en/latest/api/earthpy.spatial.html): utilities to crop a set of bands to a defined spatial extent, create a hillshade, stack bands, and calculate normalized difference rasters.


## EarthPy Vignettes 

In addition to detailed API documentation and example code executed by doctest, 
`EarthPy` documentation includes a long-form [examples gallery](https://earthpy.readthedocs.io/en/latest/gallery_vignettes/index.html) 
that demonstrates functionality using case studies. These longer case studies 
provide an opportunity to document how to integrate the functionality contained in 
different `EarthPy` modules, with an emphasis on compelling visualizations that 
convey key concepts for spatial data processing.


# EarthPy in Context

## EarthPy Focus on Integration of Spatial Data By Scientists

`EarthPy` is an open source `Python` package that makes it easier to plot and work with both spatial raster and vector data using open source tools. `EarthPy`'s goal is to make working with spatial data easier for scientists who want to use open source `Python` tools, rather than proprietary packages (e.g. `ArcPy`) or graphical user interface (GUI) based tools (e.g. QGIS), to plot and analyze data. 

`Earthpy` depends upon `GeoPandas`, which has a focus on vector data handling and analysis, and `Rasterio`, which facilitates input and output of raster data files. It also requires `Matplotlib` for plotting operations. 

To simplify dependency management and installation for non-experts, we maintain a version of EarthPy on the `conda-forge` channel, which installs the system 
libraries upon which `EarthPy` depends. This combined with high-level wrapper 
around `GeoPandas`, `Rasterio`, and `Matplotlib` lowers the barrier to entry for 
people, particularly scientists, who are learning how to work with spatial data in 
`Python`. 

While there are other useful `Python` packages for working independently with either vector (e.g. `PySAL`) or raster data (e.g. `GeoRasters`), `EarthPy` draws from both `GeoPandas` and `Rasterio` to integrate functionality for vector and raster into one package. 


## EarthPy in the Classroom

`EarthPy` also supports education and teaching. The `io` module makes it easier for a student to download a suite of teaching data subsets and other data to a standard working directory (that is automatically created if it does not exist). This supports reproducibility of workflows in a classroom (or other) setting. 

The `plot` module facilitates quick and early data exploration by introductory-level students for whom the intricancies of customizing plots with `Matplotlib` might be overwhelming. The `mask` and `spatial` modules both reduce the technical learning curve for spatial analysis with `Python`, which supports instructors in focusing on the key scientific concepts behind the code. 

The vignettes developed with `EarthPy` also provide easily adaptable starting points for in-class exercises that help students learn key spatial concepts using scientific data. 


## References

* [Rasterio](https://rasterio.readthedocs.io/en/stable/intro.html)
* [GeoPandas](http://geopandas.org/)
* [ArcPy](https://pro.arcgis.com/en/pro-app/arcpy/get-started/what-is-arcpy-.htm)
* [QGIS](https://qgis.org/en/site/)
* [PySAL](http://pysal.org/pysal/)
* [GeoRasters](https://github.com/ozak/georasters)


## Acknowledgements

There have been many [contributors to earthpy](https://github.com/earthlab/earthpy/graphs/contributors) that we are thankful for. We are also thankful for the feedback that we recieved through the software review implemented by pyOpenSci. Specifically we thank Luiz Irber who has served as an editor for this review and the two reviewers: Sean Gillies and Rohit Goswami. 
