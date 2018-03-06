def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    """
    Code from the original scipy package to resolve non 8 bit images to 8 bit for easy plotting
    Note that this will scale values <0 to 0 and values >255 to 255

    Parameters
    ----------
    data : numpy array
        The dataset to be scaled.
    cmin : number
        minvalue in the dataset. by default set to data.min()
    cmax : maxvalue in the dataset. by default set to data.min()

    """
    if high > 255:
        raise ValueError("`high` should be less than or equal to 255.")
    if low < 0:
        raise ValueError("`low` should be greater than or equal to 0.")
    if high < low:
        raise ValueError("`high` should be greater than or equal to `low`.")

    if cmin is None:
        cmin = data.min()
    if cmax is None:
        cmax = data.max()
    cscale = cmax - cmin
    if cscale < 0:
        raise ValueError("`cmax` should be larger than `cmin`.")
    elif cscale == 0:
        cscale = 1
    scale = float(high - low) / cscale
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype(np.int8)


test = np.array([1,4,6,7,-127])
bytescale(test)

import numpy as np

# scale an input array-like to a mininum and maximum number
# the input array must be of a floating point array
# if you have a non-floating point array, convert to floating using `astype('float')`
# this works with n-dimensional arrays
# it will mutate in place
# min and max can be integers
def scale_range (input_array, min, max, clip=True):
    # coerce to float if int
    if input_array.dtype == "int":
        input_array = input_array.astype(np.float16)

    input_array += -(np.min(input_array))
    input_array /= np.max(input_array) / (max - min)
    input_array += min
    # if the data have negative values that the user wishes to clip, clip them
    if clip:
        input_array.clip(min, max)
    return ((input_array+ 0.5).astype(np.int8))

test = np.array([1,4,6,7,-127])
min = 1
max = 5
input = test
scale_range(input_array=test, min= 0, max=255, clip=False)


test = np.array([1,4,6,7,-127])
scale_range(input=test, min= 1, max=5)

if test.dtype == "int":
    print("yes")
    test = test.astype(np.float16)


cmin = test.min()
cmax = test.max()
cscale = cmax - cmin
high=255
low=0
scale = float(high - low) / cscale
scale
bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype(np.int8)