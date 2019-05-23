"""
Plot Bands of Satellite Imagery with EarthPy
==================================================================

Learn how to use the EarthPy ``plot_bands()`` function to quickly plot
a single or many raster bands of an image. ``Plot_bands()`` can also
be used to plot single raster layers with legends. Additionally,
learn some of the customization possible when plotting bands.

"""

###############################################################################
# Plot Raster Data Layers Using EarthPy
# ------------------------------------------------------------------------
#
# .. note::
#    The examples below will show you how to use the ``plot_bands()`` function
#    to plot individual raster layers in images using python. To plot rgb data,
#    read help documentation related to ``ep.plot_rgb()``.
#
# In this vignette, you will use Landsat 8. To begin, you will create a stack of
# bands using Landsat 8 data and then plot the raster layers in various ways.

###############################################################################
# Import Packages
# ---------------
#
# In order to use the ``plot_bands()`` function with Landsat 8 data, the
# following packages need to be imported.

import os
from glob import glob
import matplotlib.pyplot as plt
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep

###############################################################################
# Import Example Data
# -------------------
#
# To get started, make sure your directory is set. Then, create a stack from all of
# the Landsat .tif files (one per band).

# Get data for example
data = et.data.get_data("vignette-landsat")
# Setting home directory
os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

# Stack the Landsat 8 bands
# This creates a numpy array with each "layer" representing a single band
landsat_path = glob(
    "data/vignette-landsat/LC08_L1TP_034032_20160621_20170221_01_T1_sr_band*_crop.tif"
)
landsat_path.sort()
array_stack, meta_data = es.stack(landsat_path)

###############################################################################
# Plot All Bands in a Stack
# --------------------------
#
# When you give ``ep.plot_bands()`` a three dimensional numpy array, as is created
# when ``es.stack()`` is ran, it will plot all layers of the numpy array. To title
# all of the images individually, you must submit a list of titles as an argument.
# The list must contain the same number of strings as there are bands in the stack.

titles = ["Ultra Blue", "Blue", "Green", "Red", "NIR", "SWIR 1", "SWIR 2"]
ep.plot_bands(array_stack, title=titles)
plt.show()

##################################################################################
# Plot One Band in a Stack
# ------------------------
#
# If you give ``ep.plot_bands()`` a one dimensional numpy array, such as one layer
# from the return of es.stack, it will just plot that band. You can turn off the
# colorbar using the cbar parameter (cbar=False).

ep.plot_bands(array_stack[4], cbar=False)
plt.show()

##################################################################################
# Turn Off Scaling
# -----------------
#
# ``ep.plot_bands()`` scales the imagery to a 0-255 scale by default. This range
# of values makes it easier for matplotlib to plot the data. To turn off
# scaling, simply set the scale parameter to ``False``. Below you
# plot NDVI with scaling turned off in order for the proper range of values
# (-1 to 1) to be displayed. You can use the ``cmap=`` parameter to adjust
# the colormap for the plot

NDVI = es.normalized_diff(array_stack[4], array_stack[3])
ep.plot_bands(NDVI, scale=False, cmap="RdYlGn")
plt.show()

##################################################################################
# Adjust the Number of Columns for a Multi Band Plot
# ---------------------------------------------------
#
# The number of columns used while plotting multiple bands can be changed in order
# to change the arrangement of the images overall.

ep.plot_bands(array_stack, cols=2)
plt.show()
