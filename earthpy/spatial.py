import os
import sys
import contextlib
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.geometry import mapping, box
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
from skimage import exposure


def extent_to_json(ext_obj):
    """Convert bounds to a shapely geojson like spatial object.
    Helper function
    This format is what shapely uses. The output object can be used
    to crop a raster image.

    Parameters
    ----------
    ext_obj: list or geopandas geodataframe
        Extent values should be in the order: minx, miny, maxx, maxy
    Return
    ----------
    extent_json : dict
    A dictionary of corner coordinates for the new extent
    """

    if type(ext_obj) == gpd.geodataframe.GeoDataFrame:
        extent_json = mapping(box(*ext_obj.total_bounds))
    elif type(ext_obj) == list:
        assert ext_obj[0] <= ext_obj[2], "xmin must be <= xmax"
        assert ext_obj[1] <= ext_obj[3], "ymin must be <= ymax"
        extent_json = mapping(box(*ext_obj))
    else:
        raise ValueError("Please provide a GeoDataFrame or a list of values.")

    return extent_json


# Calculate normalized difference between two arrays
# Both arrays must be of the same size


def normalized_diff(b1, b2):
    """Take two numpy arrays and calculate the normalized difference
    Math will be calculated (b2-b1) / (b2+b1).

    Parameters
    ----------
    b1, b2 : arrays with the same shape
        Math will be calculated (b2-b1) / (b2+b1).

    Returns
    ----------
    n_diff : ndarray with the same shape as inputs
        The element-wise result of (b2-b1) / (b2+b1) with all nan values
        masked.

    Examples
    --------
    >>> import numpy as np
    >>> import earthpy.spatial as es

    >>> red_band = np.array([[1, 2, 3, 4, 5],[11,12,13,14,15]])
    >>> nir_band = np.array([[6, 7, 8, 9, 10],[16,17,18,19,20]])

    >>> # Calculate normalized difference
    >>> es.normalized_diff(b2=nir_band, b1=red_band)
    masked_array(
      data=[[0.7142857142857143, 0.5555555555555556, 0.45454545454545453,
             0.38461538461538464, 0.3333333333333333],
            [0.18518518518518517, 0.1724137931034483, 0.16129032258064516,
             0.15151515151515152, 0.14285714285714285]],
      mask=[[False, False, False, False, False],
            [False, False, False, False, False]],
      fill_value=1e+20)
    """
    if not (b1.shape == b2.shape):
        raise ValueError("Both arrays should be of the same dimensions")

    n_diff = (b2 - b1) / (b2 + b1)
    n_diff = np.ma.masked_invalid(n_diff)
    return n_diff


# TODO: include a no data value here if provided


def stack_raster_tifs(band_paths, out_path, arr_out=True):
    """Take a list of raster paths and turn into an output raster stack
    numpy array. Note that this function depends upon the stack() function.

    Parameters
    ----------
    band_paths : list of file paths
        A list with paths to the bands you wish to stack. Bands
        will be stacked in the order given in this list.
    out_path : string
        A path with a file name for the output stacked raster
         tif file.
    arr_out : boolean
        A boolean argument to designate what is returned in the stacked
        raster tif output.

    Returns
    ----------
    If arr_out keyword is True:
        tuple: The first value representing the result of src.read() of the
        stacked array and the second value
        representing the result of src.profile of the stacked array.
    If arr_out keyword is False:
        str : A path with a file name for the output stacked raster tif file.

    TODO: Instead of returning a file path when arr_out=False, consider
        returning None since the out_path is already
        an input given by the user. This will make the output type consistent.
    """
    # Set default import to read
    kwds = {"mode": "r"}

    out_dir = os.path.dirname(out_path)
    writing_to_cwd = out_dir == ""
    if not os.path.exists(out_dir) and not writing_to_cwd:
        raise ValueError(
            "The output directory path that you provided does not exist"
        )

    if len(band_paths) < 2:
        raise ValueError(
            """The list of file paths is empty. You need at least
                            2 files to create a stack."""
        )
    with contextlib.ExitStack() as context:
        sources = [
            context.enter_context(rio.open(path, **kwds))
            for path in band_paths
        ]

        # TODO: Check that the CRS and TRANSFORM are the same
        dest_kwargs = sources[0].meta
        dest_count = sum(src.count for src in sources)
        dest_kwargs["count"] = dest_count

        if arr_out:
            # Write stacked gtif file
            with rio.open(out_path, "w", **dest_kwargs) as dest:
                stack(sources, dest)
            # Read and return array
            with rio.open(out_path, "r") as src:
                return src.read(), src.profile
        else:
            # Write stacked gtif file
            with rio.open(out_path, "w", **dest_kwargs) as dest:
                return stack(sources, dest)


# Function to be submitted to rasterio
# TODO: add unit tests - some are here:
# https://github.com/mapbox/rasterio/blob/master/rasterio/mask.py
# This function doesn't stand alone because it writes to an open object called
# in the other function
def stack(sources, dest):
    """Stack a set of bands into a single file.

    Parameters
    ----------
    sources : list of rasterio dataset objects
        A list with paths to the bands you wish to stack. Objects
        will be stacked in the order provided in this list.
    dest : a rio.open writable object that will store raster data.
    """

    try:
        for src in sources:
            src.profile

    except ValueError as ve:
        raise ValueError("The sources object should be Dataset Reader")
        sys.exit()

    else:
        pass

    for ii, ifile in enumerate(sources):
        bands = sources[ii].read()
        if bands.ndim != 3:
            bands = bands[np.newaxis, ...]
        for band in bands:
            dest.write(band, ii + 1)


def crop_image(raster, geoms, all_touched=True):
    """Crop a single file using geometry objects.

    Parameters
    ----------
    raster : rasterio object
        The rasterio object to be cropped. Ideally this object is opened in a
        context manager to ensure the file is properly closed.
    geoms : geopandas object or list of polygons
        Polygons are GeoJSON-like dicts specifying the boundaries of features
        in the raster to be kept. All data outside of specified polygons
        will be set to nodata.
    all_touched : bool
        From rasterio: Include a pixel in the mask if it touches any of the
        shapes. If False, include a pixel only if its center is within one of
        the shapes, or if it is selected by Bresenham's line algorithm.
        Default is True in this function.

    Returns
    ----------
    out_image: masked numpy array
        A masked numpy array that is masked / cropped to the geoms object
        extent
    out_meta:  dict
        A dictionary containing the updated metadata for the cropped raster.
        Specifically the extent (shape elements) and transform properties are
        updated.
    """

    if type(geoms) == gpd.geodataframe.GeoDataFrame:
        clip_ext = [extent_to_json(geoms)]
    else:
        clip_ext = geoms
    # Mask the input image and update the metadata
    out_image, out_transform = mask(
        raster, clip_ext, crop=True, all_touched=all_touched
    )
    out_meta = raster.meta.copy()
    out_meta.update(
        {
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        }
    )
    return (out_image, out_meta)


def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    """
    Byte scales an array (image).
    Byte scaling means converting the input image to uint8 dtype and scaling
    the range to ``(low, high)`` (default 0-255).
    If the input image already has dtype uint8, no scaling is done.
    Source code adapted from scipy.misc.bytescale (deprecated in scipy-1.0.0)

    Parameters
    ----------
    data : ndarray
        image data array.
    cmin : scalar, optional
        Bias scaling of small values. Default is ``data.min()``.
    cmax : scalar, optional
        Bias scaling of large values. Default is ``data.max()``.
    high : scalar, optional
        Scale max value to `high`.  Default is 255.
    low : scalar, optional
        Scale min value to `low`.  Default is 0.
    Returns
    -------
    img_array : uint8 ndarray
        The byte-scaled array.
    Examples
    --------
    >>> import numpy as np
    >>> from earthpy.spatial import bytescale
    >>> img = np.array([[ 91.06794177,   3.39058326,  84.4221549 ],
    ...                 [ 73.88003259,  80.91433048,   4.88878881],
    ...                 [ 51.53875334,  34.45808177,  27.5873488 ]])
    >>> bytescale(img)
    array([[255,   0, 236],
           [205, 225,   4],
           [140,  90,  70]], dtype=uint8)
    >>> bytescale(img, high=200, low=100)
    array([[200, 100, 192],
           [180, 188, 102],
           [155, 135, 128]], dtype=uint8)
    >>> bytescale(img, cmin=0, cmax=255)
    array([[255,   0, 236],
           [205, 225,   4],
           [140,  90,  70]], dtype=uint8)
    """
    if data.dtype == "uint8":
        return data

    if high > 255:
        raise ValueError("`high` should be less than or equal to 255.")
    if low < 0:
        raise ValueError("`low` should be greater than or equal to 0.")
    if high < low:
        raise ValueError("`high` should be greater than or equal to `low`.")

    if cmin is None or (cmin < data.min()):
        cmin = data.min()

    if (cmax is None) or (cmax > data.max()):
        cmax = data.max()

    # Calculate range of values
    crange = cmax - cmin
    if crange < 0:
        raise ValueError("`cmax` should be larger than `cmin`.")
    elif crange == 0:
        raise ValueError(
            "`cmax` and `cmin` should not be the same value. Please specify `cmax` > `cmin`"
        )

    scale = float(high - low) / crange

    # If cmax is less than the data max, then this scale parameter will create data > 1.0. clip the data to cmax first.
    data[data > cmax] = cmax
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype("uint8")


def colorbar(mapobj, size="3%", pad=0.09, aspect=20):
    """Adjusts the height of a colorbar to match the axis height. Note that
    this function will not work properly using matplotlib v 3.0.0 in Jupyter
    or when exporting an image. Be sure to update to 3.0.1.

    ----------
    mapobj : the matplotlib axes element.
    size : char
        The percent width of the colorbar relative to the plot. default = 3%
    pad : int
        The space between the plot and the color bar. Default = .09
    Returns
    -------
    Matplotlib color bar object with the correct width that matches the y axis
    height.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import rasterio as rio
    >>> import earthpy.spatial as es
    >>> from earthpy.io import path_to_example
    >>> with rio.open(path_to_example('rmnp-dem.tif')) as src:
    ...     dem = src.read()
    ...     fig, ax = plt.subplots(figsize = (10, 5))
    >>> im = ax.imshow(dem.squeeze())
    >>> es.colorbar(im)  #doctest: +ELLIPSIS
    <matplotlib.colorbar.Colorbar object at 0x...>
    >>> ax.set(title="Rocky Mountain National Park DEM") #doctest: +ELLIPSIS
    [Text(...'Rocky Mountain National Park DEM')]
    >>> ax.set_axis_off()
    >>> plt.show()
    """

    try:
        ax = mapobj.axes
    except AttributeError:
        raise AttributeError(
            """The colorbar function requires a matplotlib
                             axis object. You have provided
                             a {}.""".format(
                type(mapobj)
            )
        )
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size=size, pad=pad)
    return fig.colorbar(mapobj, cax=cax)


# Function to plot all layers in a stack
def plot_bands(
    arr, title=None, cmap="Greys_r", figsize=(12, 12), cols=3, extent=None
):
    """Plot each layer in a raster stack read from rasterio in
    (band, row , col) order as a numpy array. plot_bands will create an
    individual plot for each band in a grid.

    Parameters
    ----------
    arr: numpy array
        An n-dimensional numpy array with the order and numpy shape: (nbands, nrows, ncols)
    title: str or list
        Title of one band, or list of titles with one title per band
    cmap: str
        Colormap name ("greys" by default)
    cols: int
        Number of columns for plot grid (default: 3)
    figsize: tuple - optional
        Figure size in inches ((12, 12) by default)
    extent: tuple - optional
        Bounding box that the data will fill: (minx, miny, maxx, maxy)

    Returns
    ----------
    fig, ax or axs : figure object, axes object
        The figure and axes object(s) associated with the plot.

    Examples
    --------
    >>> import numpy as np
    >>> import earthpy.spatial as es
    >>> im = np.random.randint(10, size=(2, 4, 5))
    >>> titles = ["Red Band", "Green Band"]
    >>> es.plot_bands(im,
    ...               title=titles,
    ...               figsize=(12,5),
    ...               cols=2)  #doctest: +ELLIPSIS
    (<Figure size 1200x500 with 2 Axes>, ...)
    """

    try:
        arr.ndim
    except AttributeError:
        "Input arr should be a numpy array"

    if title:
        if (arr.ndim == 2) and (len(title) > 1):
            raise ValueError(
                """Plot_bands() expects one title for a single
                             band array. You have provided more than one
                             title."""
            )
        elif not (len(title) == arr.shape[0]):
            raise ValueError(
                """Plot_bands() expects the number of plot titles
                             to equal the number of array raster layers."""
            )

    # If the array is 3 dimensional setup grid plotting
    if arr.ndim > 2 and arr.shape[0] > 1:

        # Calculate the total rows that will be required to plot each band
        plot_rows = int(np.ceil(arr.shape[0] / cols))
        total_layers = arr.shape[0]

        # Plot all bands
        fig, axs = plt.subplots(plot_rows, cols, figsize=figsize)
        axs_ravel = axs.ravel()
        for ax, i in zip(axs_ravel, range(total_layers)):
            band = i + 1
            ax.imshow(bytescale(arr[i]), cmap=cmap)
            if title:
                ax.set(title=title[i])
            else:
                ax.set(title="Band %i" % band)
            ax.set(xticks=[], yticks=[])
        # This loop clears out the plots for axes which are empty
        # A matplotlib axis grid is always uniform with x cols and x rows
        # eg: an 8 band plot with 3 cols will always be 3 x 3
        for ax in axs_ravel[total_layers:]:
            ax.set_axis_off()
            ax.set(xticks=[], yticks=[])
        plt.tight_layout()
        return fig, axs

    elif arr.ndim == 2 or arr.shape[0] == 1:
        # If it's a 2 dimensional array with a 3rd dimension
        arr = np.squeeze(arr)

        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(bytescale(arr), cmap=cmap, extent=extent)
        if title:
            ax.set(title=title)
        ax.set(xticks=[], yticks=[])
        return fig, ax


def plot_rgb(
    arr,
    rgb=(0, 1, 2),
    ax=None,
    extent=None,
    title="",
    figsize=(10, 10),
    stretch=None,
    str_clip=2,
):
    """Plot three bands in a numpy array as a composite RGB image.

    Parameters
    ----------
    arr: numpy ndarray
        N-dimensional array in rasterio band order (bands, rows, columns)
    rgb: list
        Indices of the three bands to be plotted (default = 0,1,2)
    extent: tuple
        The extent object that matplotlib expects (left, right, bottom, top)
    title: string (optional)
        String representing the title of the plot
    ax: object
        The axes object where the ax element should be plotted. Default = none
    figsize: tuple (optional)
        The x and y integer dimensions of the output plot if preferred to set.
    stretch: Boolean
        If True a linear stretch will be applied
    str_clip: int (optional)
        The % of clip to apply to the stretch. Default = 2 (2 and 98)

    Returns
    ----------
    fig, ax : figure object, axes object
        The figure and axes object associated with the 3 band image. If the
        ax keyword is specified,
        the figure return will be None.
    """

    if len(arr.shape) != 3:
        raise Exception(
            """Input needs to be 3 dimensions and in rasterio
                           order with bands first"""
        )

    # Index bands for plotting and clean up data for matplotlib
    rgb_bands = arr[rgb, :, :]

    if stretch:
        s_min = str_clip
        s_max = 100 - str_clip
        arr_rescaled = np.zeros_like(rgb_bands)
        for ii, band in enumerate(rgb_bands):
            lower, upper = np.percentile(band, (s_min, s_max))
            arr_rescaled[ii] = exposure.rescale_intensity(
                band, in_range=(lower, upper)
            )
        rgb_bands = arr_rescaled.copy()

    # If type is masked array - add alpha channel for plotting
    if ma.is_masked(rgb_bands):
        # Build alpha channel
        mask = ~(np.ma.getmask(rgb_bands[0])) * 255

        # Add the mask to the array & swap the axes order from (bands,
        # rows, columns) to (rows, columns, bands) for plotting
        rgb_bands = np.vstack(
            (bytescale(rgb_bands), np.expand_dims(mask, axis=0))
        ).transpose([1, 2, 0])
    else:
        # Index bands for plotting and clean up data for matplotlib
        rgb_bands = bytescale(rgb_bands).transpose([1, 2, 0])

    # Then plot. Define ax if it's default to none
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None
    ax.imshow(rgb_bands, extent=extent)
    ax.set_title(title)
    ax.set(xticks=[], yticks=[])
    return fig, ax


def hist(
    arr, title=None, colors=["purple"], figsize=(12, 12), cols=2, bins=20
):
    """
    Plot histogram for each layer in a numpy array.

    Parameters
    ----------
    arr: a n dimension numpy array
    title: str
        A list of title values that should either equal the number of bands
        or be empty, default = none
    colors: list
        a list of color values that should either equal the number of bands
        or be a single color, (purple = default)
    cols: int the number of columsn you want to plot in
    bins: the number of bins to calculate for the histogram
    figsize: tuple. the figsize if you'd like to define it. default: (12, 12)
    Returns
    ----------
    fig, ax or axs : figure object, axes object
        The figure and axes object(s) associated with the histogram.
    """

    # If the array is 3 dimensional setup grid plotting
    if arr.ndim > 2:
        # Test if there are enough titles to create plots
        if title:
            if not (len(title) == arr.shape[0]):
                raise ValueError(
                    """"The number of plot titles should be the
                                     same as the number of raster layers in
                                      your array."""
                )
        # Calculate the total rows that will be required to plot each band
        plot_rows = int(np.ceil(arr.shape[0] / cols))
        total_layers = arr.shape[0]

        fig, axs = plt.subplots(
            plot_rows, cols, figsize=figsize, sharex=True, sharey=True
        )
        axs_ravel = axs.ravel()
        # TODO: write test case for just one color
        for band, ax, i in zip(arr, axs.ravel(), range(total_layers)):
            if len(colors) == 1:
                the_color = colors[0]
            else:
                the_color = colors[i]
            ax.hist(band.ravel(), bins=bins, color=the_color, alpha=0.8)
            if title:
                ax.set_title(title[i])
        # Clear additional axis elements
        for ax in axs_ravel[total_layers:]:
            ax.set_axis_off()

        return fig, axs
    elif arr.ndim == 2:
        # Plot all bands
        fig, ax = plt.subplots(figsize=figsize)
        ax.hist(
            arr.ravel(),
            range=[np.nanmin(arr), np.nanmax(arr)],
            bins=bins,
            color=colors[0],
        )
        if title:
            ax.set(title=title[0])
        return fig, ax


def hillshade(arr, azimuth=30, angle_altitude=30):
    """Create hillshade from a numpy array containing elevation data.

    Parameters
    ----------
    arr: a numpy ndarray of shape (rows, columns) containing elevation values
    azimuth:  default (30)
    angle_altitude: default (30)

    Return
    ----------
    numpy array containing hillshade values
    """
    azimuth = 360.0 - azimuth

    x, y = np.gradient(arr)
    slope = np.pi / 2.0 - np.arctan(np.sqrt(x * x + y * y))
    aspect = np.arctan2(-x, y)
    azimuthrad = azimuth * np.pi / 180.0
    altituderad = angle_altitude * np.pi / 180.0

    shaded = np.sin(altituderad) * np.sin(slope) + np.cos(
        altituderad
    ) * np.cos(slope) * np.cos((azimuthrad - np.pi / 2.0) - aspect)

    return 255 * (shaded + 1) / 2


def make_col_list(unique_vals, nclasses=None, cmap=None):
    """
    Take a defined matplotlib colormap, and create a list of colors based on
    a set of values. This is useful when you need to plot a series of
    classified numpy arrays that are missing some of the sequential classes.
    """
    if not nclasses:
        nclasses = len(unique_vals)

    increment = 1 / (nclasses - 1)

    # Create increments to grab colormap colors
    col_index = [(increment * c) for c in range(nclasses - 1)]
    col_index.append(1.0)

    # Create cmap list of colors
    cm = plt.cm.get_cmap(cmap)

    return [cm(c) for c in col_index]


def draw_legend(im_ax, titles=None, cmap=None, classes=None, bbox=(1.05, 1)):
    """Create a custom legend with a box for each class in a raster using the
       image object, the unique classes in the image and titles for each class.

    Parameters
    ----------
    im : matplotlib image object created using imshow()
        This is the image returned from a call to imshow().
    classes : list (optional)
        A list of unique values found in the numpy array that you wish to plot.
    titles : list (optional)
        A list of a title or category for each unique value in your raster.
        This is the label that will go next to each box in your legend. If
        nothing is provided, a generic "Category x" will be populated.
    bbox : tuple (optional)
        This is the bbox_to_anchor argument that will place the legend
        anywhere on or around your plot.

    Returns
    ----------
    matplotlib legend object to be placed on our plot.
    """

    try:
        im_ax.axes
    except AttributeError:
        raise AttributeError(
            """Oops. The legend function requires a matplotlib
                         axis object to run properly. You have provided
                         a {}.""".format(
                type(im_ax)
            )
        )

    # If classes not provided, get them from the im array in the ax object
    # Else use provided vals
    if classes:
        try:
            # Get the colormap from the mpl object
            cmap = im_ax.cmap.name
        except AssertionError:
            raise AssertionError(
                """Looks like we can't find the colormap
                                 name which means a custom colormap was likely
                                 used. Please provide the draw_legend function
                                  with a cmap= argument to ensure your
                                  legend draws properly."""
            )
        # If the colormap is manually generated from a list
        if cmap == "from_list":
            cmap = ListedColormap(im_ax.cmap.colors)

        colors = make_col_list(
            nclasses=len(classes), unique_vals=classes, cmap=cmap
        )
    else:
        classes = list(np.unique(im_ax.axes.get_images()[0].get_array()))
        # Remove masked values, could next this list comp but keeping it simple
        classes = [
            aclass for aclass in classes if aclass is not np.ma.core.masked
        ]
        colors = [im_ax.cmap(im_ax.norm(aclass)) for aclass in classes]

    # If titles are not provided, create filler titles
    if not titles:
        titles = ["Category {}".format(i + 1) for i in range(len(classes))]

    if not len(classes) == len(titles):
        raise ValueError(
            """The number of classes should equal the number of
                                 titles. You have provided {0} classes and {1}
                                 titles.""".format(
                len(classes), len(titles)
            )
        )

    patches = [
        mpatches.Patch(color=colors[i], label="{l}".format(l=titles[i]))
        for i in range(len(titles))
    ]
    # Get the axis for the legend
    ax = im_ax.axes
    return ax.legend(
        handles=patches,
        bbox_to_anchor=bbox,
        loc=2,
        borderaxespad=0.0,
        prop={"size": 13},
    )
