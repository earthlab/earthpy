"""
Plot Bands of Satellite Imagery with EarthPy
==================================================================

Learn how to use the EarthPy ``ep.hist()`` function to quickly plot
histograms for each raster bands in an image.

"""

###############################################################################
# Plot Raster Data Histograms Using EarthPy
# ------------------------------------------
#
# .. note::
#    The examples below will show you how to use the ``ep.hist()`` function
#    to plot individual raster layers histograms using python.
#
# In this vignette, you will use Landsat 8 data. To begin, you will create a
# stack of bands using Landsat 8 data. You will then plot the raster histograms.

###############################################################################
# Import Packages
# ---------------
#
# In order to use the ``ep.hist()`` function with Landsat 8 data, the
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
# To get started, make sure your directory is set. Then, create a stack from all
# of the Landsat .tif files (one per band).

# Get data for example
data = et.data.get_data("vignette-landsat")
# Set working directory
os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

# Stack the Landsat 8 bands
# This creates a numpy array with each "layer" representing a single band
# You can use the nodata= parameter to mask nodata values
landsat_path = glob("data/vignette-landsat/*band*.tif")
landsat_path.sort()
array_stack, meta_data = es.stack(landsat_path, nodata=-9999)

###############################################################################
# Plot All Histograms in a Stack With Custom Titles and Colors
# -------------------------------------------------------------
#
# When you give ``ep.hist()`` a three dimensional numpy array,it will plot
# histograms for each layer in the numpy array. You can create unique titles for
# each image by providing a list of titles using the ``title=`` parameter.
# The list must contain the same number of strings as there are bands in the
# stack. You can also modify the colors for each image with a list of Matplotlib
# colors. If one color is provided in the list, every band will inherit that color.
# Otherwise, the list must contain the same number of strings as there are bands
# in the stack.

# Create the list of color names and titles for each band
colors_list = [
    "midnightblue",
    "Blue",
    "Green",
    "Red",
    "Maroon",
    "Purple",
    "Violet",
]
titles = ["Ultra Blue", "Blue", "Green", "Red", "NIR", "SWIR 1", "SWIR 2"]

ep.hist(array_stack, colors=colors_list, title=titles)
plt.show()

###############################################################################
# Change the Bin Size and Adjust the Number of Columns
# -----------------------------------------------------
#
# To further modify your histograms, you can modify the number of bins each
# histogram plot uses to group the data. The default number is 20. This can
# be adjusted to match the data you are trying to display. Additionally, you
# can change the arrangement of the image overall by modifying the number of
# columns used to plot the data.

ep.hist(array_stack, bins=50, cols=3)
plt.show()
