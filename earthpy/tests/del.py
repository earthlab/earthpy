import earthpy.spatial as es
import earthpy as et

et.data.get_data("spatial-vector-lidar")
import numpy as np
import matplotlib.pyplot as plt


# et.data.get_data(url="https://ndownloader.figshare.com/files/12459464")

# plot legend

class_bins = [-100, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8]
class_labels = [
    "nodata",
    "neg 1",
    "neg 2",
    "neg 3",
    "neg 4",
    "neg 5",
    "pos 1",
    "pos 2",
    "pos 3",
    "pos 4",
]


im_arr = a = np.random.randn(15, 15)

# the masked array assignments attempt to repro the ndvi example. feel free to remove
im_arr[im_arr < -1.0] = -9999  # can remove
im_arr = np.ma.masked_equal(im_arr, -9999)  # can remove
im_arr = np.clip(im_arr, -1, 1)
im_arr_bin = np.digitize(im_arr, class_bins)
im_arr_bin = np.ma.masked_equal(im_arr_bin, 0)  # can remove

# returns category X labels in legend, default imshow cmap (viridis) repeating colors
ax = plt.imshow(im_arr_bin)
es.draw_legend(ax)
plt.show()

# returns no visible legend in ndvi example, but works with random array
ax = plt.imshow(im_arr_bin)
es.draw_legend(ax, titles=class_labels)
plt.show()

# this plots with grayscale in legend but not matching CMAP in plt.imshow (default viridis)
ax = plt.imshow(im_arr_bin)
es.draw_legend(ax, classes=list(range(len(class_bins))), titles=class_labels)
plt.show()

# this plots with grayscale in legend but not matching CMAP in plt.imshow (default viridis)
ax = plt.imshow(im_arr_bin)
es.draw_legend(ax, classes=list(range(len(class_bins))))
plt.show()
