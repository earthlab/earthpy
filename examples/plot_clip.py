"""
Clip Vector Data with EarthPy
==================================================================

Learn how to clip point, line, or polygon geometries with a
polygon geometry using EarthPy.

"""

###############################################################################
# Clip Vector Data in Python Using EarthPy
# ---------------------------------------------
#
# The example below walks you through a typical workflow for clipping one
# vector data file to the shape of another. Both vector data files must be
# opened with GeoPandas as GeoDataFrames and be in the same Coordinate
# Reference System (CRS) for the ``clip_shp()`` function in EarthPy to work.
# The object to be clipped will be clipped to the full extent of the clip
# object.
#
# .. note::
#    If there are multiple polygons in clip object, data from shp will be clipped
#    to the total boundary of all polygons in clip object.

###############################################################################
# Import Packages
# ---------------
#
# To begin, import the needed packages. You will primarily use EarthPy's clip
# utility alongside GeoPandas.

import os
import matplotlib.pyplot as plt
import geopandas as gpd
import earthpy as et
import earthpy.clip as ec

###############################################################################
# Import Example Data
# -------------------
#
# Once the packages have been imported, download the data needed for this
# example: one line shapefile containing all major roads in North America,
# and one polygon shapefile containing the United States border.

data = et.data.get_data("spatial-vector-lidar")

###############################################################################
# Open Files with GeoPandas and Reproject the Data
# -------------------------------------------------
#
# The first step to clipping geometries with EarthPy is to open them with
# GeoPandas as GeoDataFrames. To easily access both files, it is best to set
# your home environment. Once they are open, you must ensure they are in the
# same CRS, as ``clip_shp()`` won't work if there is a discrepancy in
# projections between the two objects. If there is a discrepancy, you can
# fix it with the function ``to_crs()`` from GeoPandas, as shown below.

# Set your home environment
os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

# Open both files with GeoPandas
roads = gpd.read_file(
    r"data/spatial-vector-lidar/global/ne_10m_roads/ne_10m_n_america_roads.shp"
)
country_boundary = gpd.read_file(
    r"data/spatial-vector-lidar/usa/usa-boundary-dissolved.shp"
)

# Reproject the roads layer to match the US boundary CRS
roads = roads.to_crs(country_boundary.crs)

# Plot the unclipped data
# The plot below shows the data before it has been clipped
fig, ax = plt.subplots(figsize=(12, 8))
roads.plot(ax=ax)
country_boundary.boundary.plot(ax=ax, color="red")
ax.set_title("Major NA Roads Unclipped to US Border", fontsize=20)
ax.set_axis_off()
plt.show()

###############################################################################
# Clip the Data
# --------------
#
# Now that the data are in the same projection and opened as GeoDataFrame
# objects, they can be clipped! To clip the data, make sure you put the object
# to be clipped as the first argument in ``clip_shp()``, followed by the
# object who's extent you want the first object clipped to. The function
# will return the clipped GeoDataFrame

roads_clipped = ec.clip_shp(roads, country_boundary)

# Plot the clipped data
# The plot below shows the results of the clip function
# sphinx_gallery_thumbnail_number = 5
fig, ax = plt.subplots(figsize=(12, 8))
roads_clipped.plot(ax=ax)
country_boundary.boundary.plot(ax=ax, color="red")
ax.set_title("Major NA Roads Clipped to US Border", fontsize=20)
ax.set_axis_off()
plt.show()
