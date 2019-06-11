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
# Create a Hillshade from a Digital Elevation Model (DEM)
# -------------------------------------------------------
# A hillshade is a 3D representation of a surface. Hillshades are generally
# rendered in greyscale. The darker and lighter colors represent the shadows
# and highlights that you would visually expect to see in a terrain model.
# Hillshades are often used as an underlay in a map, to make the data appear
# more 3-Dimensional and thus visually interesting. This vignette will show
# you how to create a hillshade from a DEM using EarthPy. It will highlight
# how to adjust the azimuth and other settings that will impact how the
# shadows are modeled in the data.
#
# The hillshade function is a part of the spatial module in EarthPy.
# To begin using the EarthPy hillshade() function, import the needed
# packages and create an array to be plotted.

###############################################################################
# Import Packages
# ----------------
#
# You will need several packages to plot hillshade. You will use Rasterio to
# open up the DEM file you will use to create the hillshade layer. You will
# primarily be using the EarthPy spatial module in this vignette.

import os
import numpy as np
import matplotlib.pyplot as plt
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
import rasterio as rio

# Download the data needed for this vignette
data = et.data.get_data("colorado-flood")

####################################################################################
# Open up the DEM layer
# -------------------------
# To create a hillshade layer, you first need a DEM layer opened up as a numpy array.
# You can do this with RasterIO. You will read in the elevation data, and take out any
# data that is bad by setting values below 0 to numpy's not a number value. You then
# plot the data with ``ep.plot_bands()`` to show that the data was read in properly.

# Set the home directory and get the data for the exercise
os.chdir(os.path.join(et.io.HOME, "earth-analytics"))
dtm = "data/colorado-flood/spatial/boulder-leehill-rd/pre-flood/lidar/pre_DTM.tif"

# Open the DEM with RasterIO
with rio.open(dtm) as src:
    elevation = src.read(1)
    # Set masked values to np.nan
    elevation[elevation < 0] = np.nan

# Plott the data
ep.plot_bands(elevation, scale=False, cmap="gist_earth")
plt.show()

####################################################################################
# Create the hillshade layer
# ----------------------------
# Once the DEM numpy array is created, simply use ``es.hillshade()`` with the DEM
# numpy array as an input to create the hillshade layer.

# Create the hillshade layer
hillshade = es.hillshade(elevation)

# Plot the hillshade layer
ep.plot_bands(hillshade, scale=False, cbar=False)
plt.show()

####################################################################################
# Change the azimuth of the sun
# -------------------------------
# The angle that sun light hits the landscape, impacts the shadows and highlights
# created on the landscape. You can adjust the azimuth values to adjust highlights
# and shadows that are created in your output hillshade. Azimuth numbers can
# range from 0 to 360 degrees, where 0 is due North. The default value for azimuth
# in ``es.hillshade()`` is 30 degrees.

# Change the azimuth of the hillshade layer
hillshade_azimuth_210 = es.hillshade(elevation, azimuth=210)

# Plot the hillshade layer with the modified azimuth
ep.plot_bands(hillshade_azimuth_210, scale=False, cbar=False)
plt.show()

####################################################################################
# Change the angle altitude of the sun
# ---------------------------------------
# Another variable you can adjust for hillshade is what angle altitude the sun is
# shining from. These values range from 0 to 90, with 90 being the sun shining from
# directly above the scene. The default value for the angle altitude in
# ``es.hillshade()`` is 30 degrees.

# Adjust the azimuth value
hillshade_angle_10 = es.hillshade(elevation, angle_altitude=10)

# Plot the hillshade layer with the modified angle altitude
ep.plot_bands(hillshade_angle_10, scale=False, cbar=False)
plt.show()

####################################################################################
# Overlay a DEM and hillshade layer
# -------------------------------------
# One of the benefits of hillshade is to visually enhance DEM layers to add clarity.
# To do this, the layers have to be plotted together. This can be done very simply
# with the ``ep.plot_bands()`` function in EarthPy.

# Plot the DEM and hillshade at the same time
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
