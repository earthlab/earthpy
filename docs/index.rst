.. Earthpy documentation master file, created by
   sphinx-quickstart on Wed Sep 19 15:56:28 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Earthpy's documentation!
===================================
Earthpy is a python package devoted to working with spatial and remote sensing data.

Earthpy's Index (Table of Contents)
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   get-started
   spatial-raster
   spatial-vector

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

About Earthpy's Documents
===================

Get-Started Document
--------------------
The ``get-started`` document provides a description of Earthpy's modules, the installation process, and dependencies.
Earthpy's Modules: 
 * Spatial
 * IO
 * Utils
 
Spatial-Raster Document
-----------------------
The ``spatial-raster`` document describes earthpy's spatial module, its functions, and provides an example code of how a function handles raster data in Python.
The specific example in the document highlights the ``stack_raster_tifs`` function, which was created to stack raster files (such as Landsat imagery). 

Spatial-Vector Document
-----------------------
The ``spatial-vector`` document describes earthpy's spatial module, its functions, and provides an example code of how a function handles vector data in Python.
The specific example in the document highlights the ``clip_shp`` function, which was created to take two GeoDataframe objects, spatially clip the first object, and use the second object as the spatial extent (clip extent).


