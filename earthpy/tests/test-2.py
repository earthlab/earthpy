import numpy as np
import matplotlib.pyplot as plt
import earthpy.spatial as es

class_bins = [-100, -0.8, -0.2, 0.2, 0.8, np.Inf]
im_arr_neg = np.random.uniform(-2, 1, (15, 15))
im_arr_class = np.digitize(im_arr_neg, class_bins)


def test_neg_vals():
    """Test that the things plot when positive and negative vales
    are provided"""

    im_ax = plt.imshow(im_arr_class)
    leg_neg = es.draw_legend(im_ax)
    legend_cols = [i.get_facecolor() for i in leg_neg.get_patches()]
    assert len(legend_cols) == len(class_bins) - 1


import numpy as np

arr = np.arange(9).reshape((4, 3, 3))
rgb = (0, 1, 2)  # the default value for the rgb parameter
rgb_bands = arr[rgb]
rgb_bands

arr = np.random.uniform(0, 255, (4, 15, 15))
# Imagine a 4 band NAIP image
arr.shape
# The rgb bands are the first 3 bands of the array for NAIP
# For landsat however it's like the 3,4,5 or something
rgb = [0, 1, 2]
# Subset just the red, green and blue bands.
rgb_bands = arr[1]
