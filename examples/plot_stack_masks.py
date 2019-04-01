"""
Mask and Plot Remote Sensing Data with EarthPy
==============================================

Learn how to mask out pixels in a raster dataset. This example shows how to apply a cloud mask to
Landsat 8 data.

"""

###############################################################################
# Plotting with EarthPy
# ---------------------
#
# .. note:: Below we walk through a typical workflow using Landsat data with EarthPy.
#
# The example below uses Landsat 8 data. In the example below, the landsat_qa layer is the
# quality assurance data layer that comes with Landsat 8 to identify pixels that may represent
# cloud, shadow and water. The mask values used below are suggested values associated with the
# landsat_qa layer that represent pixels with clouds and cloud shadows.


###############################################################################
# Import Packages
# ------------------------------
#
# To begin, import the needed packages. You will use a combination of several EarthPy
# modules including spatial, plot and mask.

from glob import glob
import os
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.plot import plotting_extent
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
import earthpy.mask as em

# Get data and set your home working directory
data = et.data.get_data("cold-springs-fire")

###############################################################################
# Import Example Data
# ------------------------------
# To get started, make sure your directory is set. Create a stack from all of the
# Landsat .tif files (one per band) and import the ``landsat_qa`` layer which provides
# the locations of cloudy and shadowed pixels in the scene.

os.chdir(os.path.join(et.io.HOME, "earth-analytics"))

# Stack the landsat bands
# This creates a numpy array with each "layer" representing a single band
landsat_paths_pre = glob(
    "data/cold-springs-fire/landsat_collect/LC080340322016070701T1-SC20180214145604/crop/*band*.tif"
)
landsat_paths_pre.sort()
arr_st, meta = es.stack(landsat_paths_pre)

# Import the landsat qa layer
with rio.open(
    "data/cold-springs-fire/landsat_collect/LC080340322016070701T1-SC20180214145604/crop/LC08_L1TP_034032_20160707_20170221_01_T1_pixel_qa_crop.tif"
) as landsat_pre_cl:
    landsat_qa = landsat_pre_cl.read(1)
    landsat_ext = plotting_extent(landsat_pre_cl)

###############################################################################
# Plot Histogram of Each Band in Your Data
# ----------------------------------------
# You can view a histogram for each band in your dataset by using the
# ``hist()`` function from the ``earthpy.plot`` module.

ep.hist(arr_st)
plt.show()

###############################################################################
# Customize Histogram Plot with Titles and Colors
# -----------------------------------------------

ep.hist(
    arr_st,
    colors=["blue"],
    title=[
        "Band 1",
        "Band 2",
        "Band 3",
        "Band 4",
        "Band 5",
        "Band 6",
        "Band 7",
    ],
)
plt.show()

###############################################################################
# View Single Band Plots
# -----------------------------------------------
# Next, have a look at the data, it looks like there is a large cloud that you
# may want to mask out.

ep.plot_bands(arr_st)
plt.show()


###############################################################################
# Mask the Data
# -----------------------------------------------
# You can use the EarthPy ``mask()`` function to handle this cloud.
# To begin you need to have a layer that defines the pixels that
# you wish to mask. In this case, the ``landsat_qa`` layer will be used.

ep.plot_bands(
    landsat_qa,
    title="The Landsat QA Layer Comes with Landsat Data\n It can be used to remove clouds and shadows",
)
plt.show()


###############################################################################
# Plot The Masked Data
# ~~~~~~~~~~~~~~~~~~~~~
# Now apply the mask and plot the masked data. The mask applies to every band in your data.
# The mask values below are values documented in the Landsat 8 documentation that represent
# clouds and cloud shadows.

# Generate array of all possible cloud / shadow values
cloud_shadow = [328, 392, 840, 904, 1350]
cloud = [352, 368, 416, 432, 480, 864, 880, 928, 944, 992]
high_confidence_cloud = [480, 992]

# Mask the data
all_masked_values = cloud_shadow + cloud + high_confidence_cloud
arr_ma = em.mask_pixels(arr_st, landsat_qa, vals=all_masked_values)

# sphinx_gallery_thumbnail_number = 5
ep.plot_rgb(
    arr_ma, rgb=[4, 3, 2], title="Array with Clouds and Shadows Masked"
)
plt.show()
