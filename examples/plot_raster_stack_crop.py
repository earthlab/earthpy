"""
Stack and Crop Rasters with EarthPy
====================================

Learn how to stack and crop satellite imagery with GeoPandas objects in EarthPy
"""

###############################################################################
# Stacking and Cropping Rasters using EarthPy
# ---------------------------------------------
#
# .. note:: The examples below will show you how to use the ``es.stack()`` and ``es.crop_image()`` functions.


###############################################################################
# Stacking Multi Band Imagery
# -----------------------------
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


###############################################################################
# Get Example Data Ready for Stack
# ----------------------------------
# Create a stack from all of the Landsat .tif files (one per band) with the
# `es.stack()` function. Make sure you output a raster with the `out_path`
# argument, as it will be needed for the crop.
#
# .. note:: If you are running this script on a Windows system, there is a
# known bug with ``.to_crs()``, which is used in this script. If an error
# occurs, you have to reset your os environment with the command
# ``os.environ["PROJ_LIB"] = r"path-to-share-folder-in-environment".

# Get data and set your home working directory

data_path_1 = et.data.get_data("cs-test-landsat")
data_path_2 = et.data.get_data("cold-springs-fire")
os.chdir(os.path.join(et.io.HOME, "earth-analytics"))


# Opening up boundary layer to use for the cropping

crop_bound = gpd.read_file(
    "data/cold-springs-fire/vector_layers/fire-boundary-geomac/co_cold_springs_20160711_2200_dd83.shp"
)

# Stacking the landsat bands needed

landsat_bands_data_path = "data/cs-test-landsat/LC08_L1TP_034032_20160621_20170221_01_T1_sr_band*[2-4]*.tif"
stack_band_paths = glob(landsat_bands_data_path)
stack_band_paths.sort()
output_dir = os.path.join("data", "outputs")
if os.path.isdir(output_dir) == False:
    os.mkdir(output_dir)
# Creating an output path for the raster

raster_out_path = os.path.join(output_dir, "raster.tiff")
arr, rast = es.stack(stack_band_paths, out_path=raster_out_path, nodata=-9999)

# Changing the Coordinate Reference System of the boundary to match that of the raster.

crop_bound = crop_bound.to_crs(rast["crs"])

#################################
# Create Extent Object
# --------------------------------
# To get the extent of the raster, use the `plotting_extent` function on the
# array from `es.stack()` and the RasterIO profile. The function needs a single
# layer of a numpy array, which is why we use `arr[0]`, and the function also
# needs the extent of the RasterIO object, which can be acquired by accessing
# the `"transform"` key within the RasterIO Profile.

extent = plotting_extent(arr[0], rast["transform"])

####################
# Plotting Pre Crop
# ------------------------------
# You can see the boundary and the raster before the crop using `ep.plot_rgb()`

fig, ax = plt.subplots(figsize=(12, 12))
crop_bound.plot(ax=ax, color="red", zorder=10)
ep.plot_rgb(
    arr,
    ax=ax,
    stretch=True,
    extent=extent,
    str_clip=0.5,
    title="Un-cropped Raster and Fire Boundary",
)
plt.show()

######################
# Cropping the data
# ~~~~~~~~~~~~~~~~~~~
# To create the cropped raster, open the raster as a RasterIO object. Use a
# with statement so no memory leaks are created. Inside the with statement,
# use the RasterIO object with the boundary to get the cropped array and the
# meta data. You can then use those to create the extent of the cropped data
# to aid in plotting.

with rio.open(
    os.path.join(et.io.HOME, "earth-analytics", raster)
) as rioobject:
    crop, meta = es.crop_image(rioobject, boundary)
    # Getting the extent of the cropped object in order to plot it
    crop_extent = plotting_extent(crop[0], meta["transform"])

# Plotting the cropped image
# sphinx_gallery_thumbnail_number = 5
fig, ax = plt.subplots(figsize=(12, 12))
crop_bound.boundary.plot(ax=ax, color="red", zorder=10)
ep.plot_rgb(
    crop,
    ax=ax,
    stretch=True,
    extent=crop_extent,
    title="Cropped Raster and Fire Boundary",
)
plt.show()
