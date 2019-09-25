"""
Plot Histograms of Pixel Values from Multi-band Imagery with EarthPy
====================================================================
Learn how to quickly plot distributions of pixel values in Python
using Earthpy. This examples shows you how to create histogram
plots for each raster band in a multi-band image such as
Landsat 8 data.
"""

###############################################################################
# Plot Raster Data Histograms Using EarthPy
# ------------------------------------------
#
# .. note::
#    This example shows you how to create histogram plots of pixel values
#    for each raster band of a multi-band image using the ``ep.hist()``
#    function from the ``earthpy.spatial`` module.
#
# In this example, you will learn how to plot histograms from multi-band
# imagery such as Landsat 8. Multi-band images store data as individual raster
# bands that contain reflectance values for various sections of the
# electromagnetic spectrum. For example, the second band of Landsat 8 provides
# surface reflectance within the blue wavelength of the electromagnetic
# spectrum, while the third and fourth bands of Landsat 8 provides surface
# reflectance within the green and red wavelengths, respectively.
# Histogram plots provide a quick way to review the distribution of pixel
# values for a specific band, which can be helpful to identify potential
# data quality issues or simply learn more about the surface area that was
# captured.
#
# To begin, you will create a stack of these individuals bands from
# Landsat 8 data and then use the ``ep.hist()`` function to plot the histograms
# for each band in the stack.

###############################################################################
# Import Packages
# ----------------
#
# In order to use the ``ep.hist()`` function from EarthPy, the following
# packages need to be imported.

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
# You can use the nodata parameter to mask nodata values
landsat_path = glob(os.path.join("data", "vignette-landsat", "*band*.tif"))
landsat_path.sort()
array_stack, meta_data = es.stack(landsat_path, nodata=-9999)

###############################################################################
# Plot All Histograms in a Stack With Custom Titles and Colors
# -------------------------------------------------------------
#
# You can create histograms for each band with unique colors and titles by
# first creating a list of colors and titles that will be provided to the
# ep.hist() function. The list for titles must contain the same number of
# strings as there are bands in the stack. You can also modify the colors for
# each image with a list of Matplotlib colors. If one color is provided in
# the list, every band will inherit that color. Otherwise, the list must
# contain the same number of strings as there are bands in the stack.

# Create the list of color names for each band
colors_list = [
    "midnightblue",
    "Blue",
    "Green",
    "Red",
    "Maroon",
    "Purple",
    "Violet",
]

# Create the list of titles for each band. The titles and colors listed
# in this example reflect the order and wavelengths of the Landsat 8 bands
titles = ["Ultra Blue", "Blue", "Green", "Red", "NIR", "SWIR 1", "SWIR 2"]

# Plot the histograms with the color and title lists you just created
# sphinx_gallery_thumbnail_number = 1
ep.hist(array_stack, colors=colors_list, title=titles)
plt.show()

###############################################################################
# Customize Bin Size and Arrangement of Histograms
# -------------------------------------------------
#
# You can customize the number of bins each histogram plot uses to group the
# data it is plotting. The default number is 20. This can be adjusted to match
# the data you are trying to display. Additionally, you can change the
# arrangement of the image overall by modifying the number of columns used
# to plot the data.

# Plot each histogram with 50 bins, arranged across three columns
ep.hist(array_stack, bins=50, cols=3)
plt.show()
