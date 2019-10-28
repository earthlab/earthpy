"""
Download Data with EarthPy
==================================================================

Learn how to download data subsets available in EarthPy and other
data accessible via URLs using EarthPy.

"""

###############################################################################
# Download Data Using EarthPy
# ----------------------------
#
# .. note::
#    The example below will show you how to use the ``data.get_data()``
#    function to download data from URLs and EarthPy data subsets.
#
# The example below walks you through a typical workflow for downloading
# data using EarthPy. You can use ``data.get_data()`` to download data
# subsets available in EarthPy using a key name for the desired data
# subset. The descriptions of available data keys can be found
# in the documentation on
# `EarthPy data keys <https://earthpy.readthedocs.io/en/latest/earthpy-data-subsets.html>`_.
#
# In addition, you can use ``data.get_data()`` to download data from a URL.
# The URL can host a single file (e.g. .csv) or a compressed .zip file,
# which will be extracted as a directory with the same name.
#
# By default, the function ``data.get_data()`` will download data to a
# subdirectory called earth-analytics in the user's home directory. If the
# earth-analytics directory does not already exist, the function will create it.

###############################################################################
# Import Packages
# ---------------
#
# To begin, import the needed packages.

import os
import earthpy as et

###############################################################################
# View List of EarthPy Data Subsets
# ----------------------------------
#
# You can view a list of available data subsets in EarthPy by calling the
# function ``data.get_data()`` with no parameters.
#
# To see descriptions of these data subsets, you can review the documentation on
# `EarthPy data keys <https://earthpy.readthedocs.io/en/latest/earthpy-data-subsets.html>`_.

et.data.get_data()

###############################################################################
# Download EarthPy Data Subsets
# ------------------------------
#
# Once you have identified which data subset you want to download, you can provide
# the data key (e.g. vignette-elevation) as a parameter to the ``data.get_data()``
# function.
#
# By default, data downloaded using an EarthPy data key will be
# saved to a data subdirectory in the earth-analytics directory
# (e.g. earth-analytics/data/).

data = et.data.get_data("vignette-elevation")

# You can now define the path to the downloaded data
os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

raster_path = os.path.join("data", "vignette-elevation", "pre_DTM.tif")

###############################################################################
# Download Data From URLs
# ------------------------
#
# If you have the URL to a single file (e.g. .csv) or a compressed .zip file,
# you can provide the URL as a parameter value called ``url`` to the
# ``data.get_data()`` function.
#
# By default, data downloaded from a URL will be
# saved to a subdirectory called earthpy-downloads under the data directory
# (e.g. earth-analytics/data/earthpy-downloads/).

# Example download of a file called monthly-precip-2002-2013.csv
url = "https://ndownloader.figshare.com/files/12707792"
data = et.data.get_data(url=url)

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

csv_path = os.path.join(
    "data", "earthpy-downloads", "monthly-precip-2002-2013.csv"
)

# Example download of a compressed .zip file called boulder_county.zip
# which contains a shapefile (.shp) of the Boulder County, CO boundary
url = "https://ndownloader.figshare.com/files/14535518"
data = et.data.get_data(url=url)

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

vector_path = os.path.join(
    "data", "earthpy-downloads", "boulder_county", "boulder_county.shp"
)

###############################################################################
# Replace Previously Downloaded Data
# -----------------------------------
#
# If the data already exist in a directory, the default action of ``data.get_data()``
# function is to not replace the existing data with the new download. If you want
# to replace the file, you can add the parameter ``replace`` and set it
# equal to True.

url = "https://ndownloader.figshare.com/files/12707792"
data = et.data.get_data(url=url, replace=True)
