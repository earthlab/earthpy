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


import os
from glob import glob
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.plot import plotting_extent
import earthpy as et
import geopandas as gpd
import earthpy.spatial as es
import earthpy.plot as ep

# Setting the home directory to be ubiquitous

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

data = et.data.get_data("cs-test-landsat")
data2 = et.data.get_data("cold-springs-fire")

landsat_bands = "data/cs-test-landsat/LC08_L1TP_034032_20160621_20170221_01_T1_sr_band*[2-4]*.tif"
stack_bands = glob(landsat_bands)
stack_bands.sort()
if os.path.isdir("data/outputs") == False:
    os.mkdir("data/outputs")
raster = "data/outputs/raster.tiff"
arr, rast = es.stack(stack_bands, out_path=raster)
rioobject = rio.open(raster)
boundary = gpd.read_file("data/cold-springs-fire/vector_layers/fire-boundary-geomac/co_cold_springs_20160711_2200_dd83.shp")

arr = es.bytescale(arr, cmin=0)

extent = plotting_extent(arr[0], rast["transform"])

boundary = boundary.to_crs(rast['crs'])

fig, ax = plt.subplots(figsize=(12, 12))
boundary.plot(ax=ax,color='red', zorder=10)
ep.plot_rgb(arr, ax=ax, stretch=True, extent=extent)
ax.set_title("plswork", fontsize=20)
plt.show()

crop, meta = es.crop_image(rioobject, boundary)
crop_extent = plotting_extent(crop[0], meta["transform"])
fig, ax = plt.subplots(figsize=(12, 12))
boundary.boundary.plot(ax=ax,color='red', zorder=10)
ep.plot_rgb(crop, ax=ax, stretch=True, extent=crop_extent)
ax.set_title("plswork", fontsize=20)
plt.show()