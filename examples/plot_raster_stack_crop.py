"""
Stack and Crop Raster Data Using EarthPy
========================================

Learn how to stack and crop satellite imagery with GeoPandas objects in EarthPy
"""

###############################################################################
# Stacking and Cropping Rasters using EarthPy
# ---------------------------------------------
#
# .. note::
#       The examples below will show you how to use the ``es.stack()`` and
#       ``es.crop_image()`` functions from EarthPy.

###############################################################################
# Stacking Multi Band Imagery
# -----------------------------
# Some remote sensing datasets are stored with each band in a separate file. However,
# often you want to use all of the bands together in your analysis. For example if
# you wish to plot multiple bands together to create a color image you will need all
# of them in the same file or "stack". EarthPy has a stack function that allows you
# to take a set of .tif files that are all in the same spatial extent, CRS and resolution
# and either export them together a single stacked .tif file or work with them in Python
# directly as a stacked numpy array.
#
# To begin using the EarthPy stack function, import the needed packages
# and create an array to be plotted. Below we plot the data as continuous with a colorbar
# using the ``plot_bands()`` function.

###############################################################################
# Import Packages
# ------------------------------
#
# You will need several packages to stack your raster. Geopandas will allow you to quickly
# open up a shapefile that will be used later to crop your data. You will primarily be
# using the spatial module
# of EarthPy, but other packages will be needed as well.

import os
from glob import glob
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.plot import plotting_extent
import geopandas as gpd
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep


########################################################################################
# Get Example Data Ready for Stack
# ----------------------------------
# With EarthPy we can create a stack from all of the Landsat .tif files (one per band)
# in a folder with the `es.stack()` function.

###################################################################################
# Error found on Windows systems
# -------------------------------
# .. note::
#       If you are running this script on a Windows system, there is a
#       known bug with ``.to_crs()``, which is used in this script. If an error
#       occurs, you have to reset your os environment with the command
#       ```os.environ["PROJ_LIB"] = r"path-to-share-folder-in-environment"```.

# Getting sample data from EarthPy and setting your home working directory

data_path_1 = et.data.get_data("cs-test-landsat")
os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

# Preparing the landsat bands to be stacked using glob and sort

landsat_bands_data_path = "data/cs-test-landsat/LC08_L1TP_034032_20160621_20170221_01_T1_sr_band*[2-4]*.tif"
stack_band_paths = glob(landsat_bands_data_path)
stack_band_paths.sort()

# Creating output directory and the output path

output_dir = os.path.join("data", "outputs")
if os.path.isdir(output_dir) == False:
    os.mkdir(output_dir)
if os.path.isdir(os.path.join(output_dir + "outputraster")) == False:
    os.mkdir(os.path.join(output_dir + "outputraster"))

raster_out_path = os.path.join(output_dir, "raster.tiff")

####################################################################################
# Stacking the prepared bands
# ---------------------------
# The stack function has an optional output argument, where you can write the raster
# to a tiff file in a folder. If you want to use this functionality, make sure there
# is a folder to write your tiff file to.
# The Stack function also returns two object, an array and a RasterIO profile. Make
# sure to be catch both in variables.

# Stacking the Landsat bands

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

array, raster_prof = es.stack(stack_band_paths, out_path=raster_out_path)

####################################################################################
# Create Extent Object
# --------------------------------
# To get the extent of the raster, use the `plotting_extent` function on the
# array from `es.stack()` and the RasterIO profile. The function needs a single
# layer of a numpy array, which is why we use `arr[0]`, and the function also
# needs the extent of the RasterIO object, which can be acquired by accessing
# the `"transform"` key within the RasterIO Profile.

extent = plotting_extent(array[0], raster_prof["transform"])

################################################################################
# Plot Un-cropped Data
# ------------------------------
# You can see the boundary and the raster before the crop using `ep.plot_rgb()`

fig, ax = plt.subplots(figsize=(12, 12))
ep.plot_rgb(
    array,
    ax=ax,
    stretch=True,
    extent=extent,
    str_clip=0.5,
    title="Un-cropped Raster",
)
plt.show()

###########################################################################
# No Data Option
# ---------------
# `es.stack()` has an option for how to deal with no data values in a raster.
# If desired, a no data value can be provided to the function, which will
# then assign every instance of that value in the raster to null data.

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

array_nodata, raster_prof_nodata = es.stack(stack_band_paths, nodata=-9999)

# Recreate extent object for the No Data array

extent_nodata = plotting_extent(
    array_nodata[0], raster_prof_nodata["transform"]
)

################################################################################
# Plot Un-cropped Data
# ------------------------------
# You can see the boundary and the raster before the crop using `ep.plot_rgb()`

fig, ax = plt.subplots(figsize=(12, 12))
ep.plot_rgb(
    array_nodata,
    ax=ax,
    stretch=True,
    extent=extent,
    str_clip=0.5,
    title="Un-cropped Raster, No Data Value Selected",
)
plt.show()


#############################################################################
# Cropping the data
# ------------------
# To create the cropped raster, the fastest option is to crop each file
# individually, write out the cropped raster to a new file, and then stack
# the new files together. To do this, make sure you have a ShapeFile boundary
# in the form of a GeoPandas object you can use as the cropping object.
# Then, loop through every file you wish to crop and crop the image, then
# write it out to a file. Take the rasters created and stack them like
# we stack bands in the previous examples.

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

# Getting data for the fire boundary we are going to clip the raster too.

data_path_2 = et.data.get_data("cold-springs-fire")

# Opening the boundary with GeoPandas.

crop_bound = gpd.read_file(
    "data/cold-springs-fire/vector_layers/fire-boundary-geomac/co_cold_springs_20160711_2200_dd83.shp"
)

# If you are on windows, make sure to set your environment here!

# Change the Coordinate Reference System of the boundary to match that of the raster.
# To do this, open one of the rasters are a RasterIO object, and get the profile.
# You can use this profile to change the coordinate reference system of the boundary.

with rio.open(stack_band_paths[0]) as raster_crs:
    crop_raster_profile = raster_crs.profile
    crop_bound_utm13N = crop_bound.to_crs(crop_raster_profile["crs"])

# This step crops all of the bands one by one. It uses enumerate to do dynamic naming
# of raster outputs. The `i` variable will be an integer that counts up one with every
# loop that is completed, and `bands` will be the raster bands in the folder.
# It crops the rasters one at a time and writes them to an output directory.

for i, bands in enumerate(stack_band_paths):
    outpath = "data/outputs/outputraster" + str(i)
    with rio.open(bands) as currband:
        crop, meta = es.crop_image(currband, crop_bound_utm13N)
        with rio.open(outpath, "w", **meta) as dest:
            dest.write(crop)

# This section stacks the cropped rasters generated by the previous loop.

stack = glob("data/outputs/outputraster*")
cropped_array, array_raster = es.stack(stack, nodata=-9999)
crop_extent = plotting_extent(crop[0], meta["transform"])

# Plotting the cropped image
# sphinx_gallery_thumbnail_number = 5
fig, ax = plt.subplots(figsize=(12, 12))
crop_bound_utm13N.boundary.plot(ax=ax, color="red", zorder=10)
ep.plot_rgb(
    cropped_array,
    ax=ax,
    stretch=True,
    extent=crop_extent,
    title="Cropped Raster and Fire Boundary",
)
plt.show()
