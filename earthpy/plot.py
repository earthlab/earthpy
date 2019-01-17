"""
The ``earthpy`` spatial module provides functions that wrap around ``rasterio``
and ``geopandas`` to work with raster and vector data in Python.
"""

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import rasterio as rio
from skimage import exposure
import earthpy.spatial as es


def colorbar(mapobj, size="3%", pad=0.09, aspect=20):
    """Adjusts the height of a colorbar to match the axis height. Note that
    this function will not work properly using matplotlib v 3.0.0 in Jupyter
    or when exporting an image. Be sure to update to 3.0.1.

    Parameters
    ----------
    mapobj : the matplotlib axes element.
    size : char
        The percent width of the colorbar relative to the plot. default = 3%
    pad : int
        The space between the plot and the color bar. Default = .09

    Returns
    -------
    matplotlib.pyplot.colorbar

        Matplotlib color bar object with the correct width that matches the
        y-axis height.

    Examples
    --------

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import rasterio as rio
        >>> import earthpy.plot as ep
        >>> from earthpy.io import path_to_example
        >>> with rio.open(path_to_example('rmnp-dem.tif')) as src:
        ...     dem = src.read()
        ...     fig, ax = plt.subplots(figsize = (10, 5))
        >>> im = ax.imshow(dem.squeeze())
        >>> ep.colorbar(im)  #doctest: +ELLIPSIS
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

    Example
    -------
    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import earthpy.plot as ep
        >>> from earthpy.io import path_to_example
        >>> import rasterio as rio
        >>> titles = ['Red', 'Green', 'Blue']
        >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
        ...     ep.plot_bands(src.read(),
        ...                   title=titles,
        ...                   figsize=(8, 3)) #doctest: +ELLIPSIS
        (<Figure size ... with 3 Axes>, ...)
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
            ax.imshow(es.bytescale(arr[i]), cmap=cmap)
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
        ax.imshow(es.bytescale(arr), cmap=cmap, extent=extent)
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

    Example
    -------

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import rasterio as rio
        >>> import earthpy.plot as ep
        >>> from earthpy.io import path_to_example
        >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
        ...     img_array = src.read()
        >>> ep.plot_rgb(img_array) #doctest: +ELLIPSIS
        (<Figure size 1000x1000 with 1 Axes>, ...)

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
            (es.bytescale(rgb_bands), np.expand_dims(mask, axis=0))
        ).transpose([1, 2, 0])
    else:
        # Index bands for plotting and clean up data for matplotlib
        rgb_bands = es.bytescale(rgb_bands).transpose([1, 2, 0])

    # Then plot. Define ax if it's default to none
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = None
    ax.imshow(rgb_bands, extent=extent)
    ax.set_title(title)
    ax.set(xticks=[], yticks=[])
    return fig, ax


def hist(arr, title=None, colors="purple", figsize=(12, 12), cols=2, bins=20):
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
    cols: int the number of columns you want to plot in
    bins: the number of bins to calculate for the histogram
    figsize: tuple. the figsize if you'd like to define it. default: (12, 12)

    Returns
    ----------
    fig, ax or axs : figure object, axes object
        The figure and axes object(s) associated with the histogram.

    Example
    -------
    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import rasterio as rio
        >>> import earthpy.plot as ep
        >>> from earthpy.io import path_to_example
        >>> with rio.open(path_to_example('rmnp-rgb.tif')) as src:
        ...     img_array = src.read()
        >>> ep.hist(img_array,
        ...     colors=['r', 'g', 'b'],
        ...     title=['Red', 'Green', 'Blue'],
        ...     cols=3,
        ...     figsize=(8, 3)) #doctest: +ELLIPSIS
        (<Figure size 800x300 with 3 Axes>, ...)
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
    matplotlib.pyplot.legend

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
