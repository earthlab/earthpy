"""
Stack and Crop Rasters with EarthPy
===========================

Learn how to stack and crop satellite imagery with GeoPandas objects in EarthPy
"""

###############################################################################
# Stacking and Cropping Rasters using EarthPy
# -------------------------------------
#
# .. note:: The examples below will show you how to use the ``es.stack()`` and ``es.crop_image()`` functions.


###############################################################################
# Stacking Multi Band Imagery
# ---------------------
#
# Let's explore a simple raster stack using EarthPy. To begin, import the needed packages
# and create an array to be plotted. Below we plot the data as continuous with a colorbar
# using the ``plot_bands()`` function.

###############################################################################
# Import Packages
# ------------------------------
#
# To begin, import the needed packages. You will primarily be using the spatial module
# of EarthPy, but other packages will be needed as well.

import os
from glob import glob
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.plot import plotting_extent
import earthpy as et
import geopandas as gpd
import earthpy.spatial as es
import earthpy.plot as ep

# Get data and set your home working directory
data = et.data.get_data("cs-test-landsat")
data2 = et.data.get_data("cold-springs-fire")
os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

###############################################################################
# Get Example Data Ready for Stack
# ------------------------------
# Create a stack from all of the Landsat .tif files (one per band) with the
# `es.stack()` function. Make sure you output a raster with the `out_path`
# argument, as it will be needed for the crop.

# Stacking the landsat bands needed
landsat_bands = "data/cs-test-landsat/LC08_L1TP_034032_20160621_20170221_01_T1_sr_band*[2-4]*.tif"
stack_bands = glob(landsat_bands)
stack_bands.sort()
if os.path.isdir("data/outputs") == False:
    os.mkdir("data/outputs")
# Creating an output path for the raster
raster = "data/outputs/raster.tiff"
arr, rast = es.stack(stack_bands, out_path=raster, nodata=-9999)

###############################################################################
# Create a RasterIO Object and a Geopandas Object
# ------------------------------
# With the .tiff file made from the last step, create a RasterIO object.
# Additionally, to make the crop boundaries, open your boundary vector file with
# GeoPandas.


rioobject = rio.open(raster)
boundary = gpd.read_file("data/cold-springs-fire/vector_layers/fire-boundary-geomac/co_cold_springs_20160711_2200_dd83.shp")

###############################################################################
# Create Extent and Fix Boundary
# ------------------------------
# To get the extent of the raster, use the `plotting_extent` function on the
# array from `es.stack()` and the RasterIO profile. The function needs a single
# layer of a numpy array, which is why we use `arr[0]`, and the function also
# needs the extent of the RasterIO object, which can be acquired by accessing
# the `"transform"` key within the RasterIO Profile. Additionally, you can
# access the Coordinate Reference System(CRS) of a RasterIO object by looking up
# `"crs"` in it's profile, which is what we use to to put the boundary in the
# same CRS as the raster so their extents overlap.


extent = plotting_extent(arr[0], rast["transform"])

boundary = boundary.to_crs(rast['crs'])

###############################################################################
# Plotting Pre Crop
# ------------------------------
# You can see the boundary and the raster before the crop using `ep.plot_rgb()`

fig, ax = plt.subplots(figsize=(12, 12))
boundary.plot(ax=ax,color='red', zorder=10)
ep.plot_rgb(arr, ax=ax, stretch=True, extent=extent, str_clip=-.5)
ax.set_title("plswork", fontsize=20)
plt.show()

###############################################################################
# Cropping the data
# ------------------------------
# To create the cropped raster, the RasterIO object that was made earlier, as
# well as the boundary with the fixed CRS are needed. `es.crop_image()` will
# return the cropped image as a numpy array, as well as the meta data associated
# with the image.

crop, meta = es.crop_image(rioobject, boundary)
# Getting the extent of the cropped object in order to plot it
crop_extent = plotting_extent(crop[0], meta["transform"])
# Plotting the cropped image
fig, ax = plt.subplots(figsize=(12, 12))
boundary.boundary.plot(ax=ax,color='red', zorder=10)
ep.plot_rgb(crop, ax=ax, stretch=True, extent=crop_extent)
ax.set_title("plswork", fontsize=20)
plt.show()