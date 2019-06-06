"""
Create A Hillshade Layer Using EarthPy
========================================

Learn how to create a hillshade Layer from a DEM using EarthPy
"""

###############################################################################
# Create A Hillshade Layer Using EarthPy
# ---------------------------------------
#
# .. note::
#       The examples below will show you how to use the ``es.hillshade()``
#       function from EarthPy.

###############################################################################
# Create hillshade from DEM
# -----------------------------
# Creating a hillshade layer can be a great way to help visualize elevation
# data, and make your map more presentable. This vignette will show you
# how to create a hillshade layer using EarthPy, and the different ways to
# modify the layer to get the hillshade to look exactly how you want it to.
#
# To begin using the EarthPy ``hillshade()`` function, import the needed
# packages and create an array to be plotted.

###############################################################################
# Import Packages
# ------------------------------
#
# You will need several packages to plot hillshade. You will use RasterIO to
# open up the DEM file you will use to create the hillshade layer. You will
# primarily be using the EarthPy spatial module in this vignette.

import os
import numpy as np
import matplotlib.pyplot as plt
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
import rasterio as rio

# Downloading the data needed for this vignette

data = et.data.get_data("colorado-flood")

####################################################################################
# Opening up the DEM layer
# -------------------------
# To create a hillshade layer, we first need a DEM layer opened up as a numpy array.
# We can do this with RasterIO. We will read in the elevation data, and take out any
# data that is bad by setting values below 0 to numpy's not a number value. We then
# plot the data with ``ep.plot_bands()`` to show that the data was read in properly.

# Setting the home directory and getting the data for the exercise

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))
dtm = "data/vignette-elevation/pre_DTM.tif"

# Opening the DEM with RasterIO

with rio.open(dtm) as src:
    elevation = src.read(1)
    # Fixing bad values
    elevation[elevation < 0] = np.nan

# Plotting the data

ep.plot_bands(elevation, scale=False, cmap="gist_earth")
plt.show()

####################################################################################
# Creating the hillshade layer
# ----------------------------
# Once the DEM numpy array is created, simply use ``es.hillshade()`` with the DEM
# numpy array as an input to create the hillshade layer.

# Creating the hillshade layer

hillshade = es.hillshade(elevation)

# Plotting the hillshade layer

ep.plot_bands(hillshade, scale=False, cbar=False)
plt.show()

####################################################################################
# Changing the azimuth of the sun
# -------------------------------
# In hillshade, the angle that the light hits the DEM at will change how the output
# layer looks. You can adjust this by setting the azimuth angle. Azimuth numbers can
# range from 0 to 360 degrees, where 0 is due North. The default value for azimuth
# in ``es.hillshade()`` is 30 degrees.

# Changing the azimuth of the hillshade layer

hillshade_azimuth_210 = es.hillshade(elevation, azimuth=210)

# Plotting the hillshade layer with the modified azimuth

ep.plot_bands(hillshade_azimuth_210, scale=False, cbar=False)
plt.show()

####################################################################################
# Changing the angle altitude of the sun
# ---------------------------------------
# Another variable you can adjust for hillshade is what angle altitude the sun is
# shining from. These values range from 0 to 90, with 90 being the sun shining from
# directly above the scene. The default value for the angle altitude in
# ``es.hillshade()`` is 30 degrees.

# Changing the angle altitude of the sun

hillshade_angle_10 = es.hillshade(elevation, angle_altitude=10)

# Plotting the hillshade layer with the modified angle altitude

ep.plot_bands(hillshade_angle_10, scale=False, cbar=False)
plt.show()

####################################################################################
# Overlaying a DEM and hillshade layer
# -------------------------------------
# One of the benefits of hillshade is to visually enhance DEM layers to add clarity.
# To do this, the layers have to be plotted together. This can be done very simply
# with the ``ep.plot_bands()`` function in EarthPy.

# Plotting the DEM and hillshade at the same time
# sphinx_gallery_thumbnail_number = 5
fig, ax = plt.subplots(figsize=(10, 6))
ep.plot_bands(
    elevation,
    ax=ax,
    scale=False,
    cmap="terrain",
    title="Lidar Digital Elevation Model (DEM)\n overlayed on top of a hillshade",
)
ax.imshow(hillshade, cmap="Greys", alpha=0.5)
plt.show()
