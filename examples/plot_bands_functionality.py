"""
Plot Bands of Satellite Imagery with EarthPy
==================================================================

Learn how to plot each individual band from satellite imagery with
EarthPy. This guide will demonstrate how to plot every band from a
satellite, as well as individual bands. It will also go over some
of the customization possible when plotting bands.

"""

###############################################################################
# Plotting Satellite Imagery Bands in Python Using EarthPy
# ---------------------------------------------------------
#
# .. note::
#    The examples below will show you how to use the ``plot_bands()`` function
#    to plot individual satellite bands in python. To plot rgb data, read help
#    documentation related to `ep.plot_rgb()`.
#
# The example below walks you through a typical workflow for plotting all bands
# found in Landsat 8 data with EarthPy.
#
# First, you will create a stack of bands using Landsat 8 data and then

###############################################################################
# Import Packages
# ---------------
#
# To begin, import the needed packages. You will use a combination of several EarthPy
# modules including spatial and plot.

import os
from glob import glob
import matplotlib.pyplot as plt
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep

# Get data for example
data = et.data.get_data("cold-springs-fire")


###############################################################################
# Import Example Data
# -------------------
#
# To get started, make sure your directory is set. Then, create a stack from all of
# the Landsat .tif files (one per band).

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

# Stack the Landsat 8 bands
# This creates a numpy array with each "layer" representing a single band
landsat_path = glob(
    "data/cold-springs-fire/landsat_collect/LC080340322016072301T1-SC20180214145802/crop/*band*.tif"
)
landsat_path.sort()
array_stack, meta_data = es.stack(landsat_path)

###############################################################################
# Plot All Bands in a Stack
# --------------------------
#
# When `ep.plot_bands()` is handed a three dimensional numpy array, as is created
# when `es.stack()` is ran, it will plot all layers of the numpy array.

ep.plot_bands(array_stack)
plt.show()

##################################################################################
# Plot One Band in a Stack
# ------------------------
#
# When `ep.plot_bands` is handed a one dimensional numpy array, such as one layer
# from the return of `es.stack`, it will just plot that band.

ep.plot_bands(array_stack[0])
plt.show()

##################################################################################
# Turn Off Scaling
# -----------------
#
# `ep.plot_bands()` scales the imagery to a 0-255 scale by default. This can make
# values easier to compare between images that are scaled differently. To turn off
# scaling, simply set the argument to false, and the original values will be
# displayed.

ep.plot_bands(array_stack[0], scale=False)
plt.show()

##################################################################################
# Assign Titles
# --------------
#
# To assign titles, either a list of titles or a string can be passed to the
# function. If you are plotting all the bands in a stack, a list must be provided.
# If you are only plotting one band, just a string will suffice.

titles = ["Ultra Blue", "Blue", "Green", "Red", "NIR", "SWIR 1", "SWIR 2"]
ep.plot_bands(array_stack, title=titles)
plt.show()

##################################################################################
# Change Shape of Plot
# ---------------------
#
# The number of columns used while plotting multiple bands can be changed in order
# to change the arrangement of the images overall.

ep.plot_bands(array_stack, cols=2)
plt.show()
