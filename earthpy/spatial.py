"""
earthpy.spatial
===============

Functions to manipulate spatial raster and vector data.

"""

import os
import sys
import contextlib
import warnings
import numpy as np
from shapely.geometry import mapping, box
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask


def extent_to_json(ext_obj):
    """Convert bounds to a shapely geojson like spatial object.

    This format is what shapely uses. The output object can be used
    to crop a raster image.

    Parameters
    ----------
    ext_obj: list or geopandas geodataframe
        If provided with a geopandas geodataframe, the extent
        will be generated from that. Otherwise, extent values
        should be in the order: minx, miny, maxx, maxy.

    Return
    ------
    extent_json: A GeoJSON style dictionary of corner coordinates
    for the extent
        A GeoJSON style dictionary of corner coordinates representing
        the spatial extent of the provided spatial object.

    Example
    -------
    >>> import geopandas as gpd
    >>> import earthpy.spatial as es
    >>> from earthpy.io import path_to_example
    >>> rmnp = gpd.read_file(path_to_example('rmnp.shp'))
    >>> es.extent_to_json(rmnp)
    {'type': 'Polygon', 'coordinates': (((-105.4935937, 40.1580827), ...),)}
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


def normalized_diff(b1, b2):
    """Take two n-dimensional numpy arrays and calculate the normalized
    difference.

    Math will be calculated (b1-b2) / (b1 + b2).

    Parameters
    ----------
    b1, b2 : numpy arrays
        Two numpy arrays that will be used to calculate the normalized
        difference. Math will be calculated (b1-b2) / (b1+b2).

    Returns
    ----------
    n_diff : numpy array
        The element-wise result of (b1-b2) / (b1+b2) calculation. Inf values
        are set to nan. Array returned as masked if result includes nan values.

    Examples
    --------
    >>> import numpy as np
    >>> import earthpy.spatial as es
    >>> # Calculate normalized difference vegetation index
    >>> nir_band = np.array([[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
    >>> red_band = np.array([[1, 2, 3, 4, 5], [11, 12, 13, 14, 15]])
    >>> ndvi = es.normalized_diff(b1=nir_band, b2=red_band)
    >>> ndvi
    array([[0.71428571, 0.55555556, 0.45454545, 0.38461538, 0.33333333],
           [0.18518519, 0.17241379, 0.16129032, 0.15151515, 0.14285714]])

    >>> # Calculate normalized burn ratio
    >>> nir_band = np.array([[8, 10, 13, 17, 15], [18, 20, 22, 23, 25]])
    >>> swir_band = np.array([[6, 7, 8, 9, 10], [16, 17, 18, 19, 20]])
    >>> nbr = es.normalized_diff(b1=nir_band, b2=swir_band)
    >>> nbr
    array([[0.14285714, 0.17647059, 0.23809524, 0.30769231, 0.2       ],
           [0.05882353, 0.08108108, 0.1       , 0.0952381 , 0.11111111]])
    """
    if not (b1.shape == b2.shape):
        raise ValueError("Both arrays should have the same dimensions")

    # Ignore warning for division by zero
    with np.errstate(divide="ignore"):
        n_diff = (b1 - b2) / (b1 + b2)

    # Set inf values to nan and provide custom warning
    if np.isinf(n_diff).any():
        warnings.warn(
            "Divide by zero produced infinity values that will be replaced "
            "with nan values",
            Warning,
        )
        n_diff[np.isinf(n_diff)] = np.nan

    # Mask invalid values
    if np.isnan(n_diff).any():
        n_diff = np.ma.masked_invalid(n_diff)

    return n_diff


def stack(band_paths, out_path="", nodata=None):
    """Convert a list of raster paths into a raster stack numpy darray.

    Parameters
    ----------
    band_paths : list of file paths
        A list with paths to the bands to be stacked. Bands
        will be stacked in the order given in this list.
    out_path : string (optional)
        A path with a file name for the output stacked raster
        tif file.
    nodata : numeric (optional)
        A value (int or float) that represents invalid or missing values to
        mask in the output.

    Returns
    ----------
    tuple :

        numpy array
            N-dimensional array created by stacking the raster files provided.
        rasterio profile object
            A rasterio profile object containing the updated spatial metadata
            for the stacked numpy array.

    Example
    -------
        >>> import os
        >>> import earthpy.spatial as es
        >>> from earthpy.io import path_to_example
        >>> band_fnames = ["red.tif", "green.tif", "blue.tif"]
        >>> band_paths = [path_to_example(fname) for fname in band_fnames]
        >>> destfile = "./stack_result.tif"
        >>> arr, arr_meta = es.stack(band_paths, destfile)
        >>> arr.shape
        (3, 373, 485)
        >>> os.path.isfile(destfile)
        True
        >>> # optionally, clean up example output
        >>> os.remove(destfile)
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
            "The list of file paths is empty. You need at least 2 files to "
            "create a stack."
        )

    # Invalid filename specified and write_raster == True.
    # Tell user to specify valid filename
    if (len(out_path) > 0) and (
        len(os.path.basename(out_path).split(".")) < 2
    ):
        raise ValueError("Please specify a valid file name for output.")

    # Set write_raster flag if valid filename provided
    write_raster = False
    if len(os.path.basename(out_path).split(".")) == 2:
        write_raster = True

    with contextlib.ExitStack() as context:
        sources = [
            context.enter_context(rio.open(path, **kwds))
            for path in band_paths
        ]

        # Check that the CRS and TRANSFORM are the same
        dest_crs = [src.meta["crs"].to_string() for src in sources]
        dest_aff = [src.meta["transform"] for src in sources]
        dest_shps = [
            (src.meta["height"], src.meta["width"]) for src in sources
        ]

        if not len(set(dest_crs)) == 1:
            raise ValueError(
                "Please ensure all source rasters have the same CRS."
            )

        if not len(set(dest_aff)) == 1:
            raise ValueError(
                "Please ensure all source rasters have same affine transform."
            )

        if not len(set(dest_shps)) == 1:
            raise ValueError(
                "Please ensure all source rasters have same dimensions "
                "(nrows, ncols)."
            )

        # Update band count
        dest_kwargs = sources[0].meta
        dest_count = sum(src.count for src in sources)
        dest_kwargs["count"] = dest_count

        if nodata is not None:
            dest_kwargs["nodata"] = nodata

        # Stack the bands and return an array, but don't write to disk
        if not write_raster:

            arr, meta = _stack_bands(sources)

            # If user specified nodata, mask the array
            if nodata is not None:
                # Mask and input data types must be identical for mask_equal()
                nodata = np.array([nodata]).astype(arr.dtype)[0]
                arr = np.ma.masked_equal(arr, nodata)

            return arr, meta

        # Write out the stacked array and return a numpy array
        else:
            # Valid output path checked above
            file_fmt = os.path.basename(out_path).split(".")[-1]

            # Check that file format for output is the same as source driver
            rio_driver = sources[0].profile["driver"]
            if file_fmt not in rio_driver.lower():
                raise ValueError(
                    "Source data is {}. Please specify corresponding output "
                    "extension.".format(rio_driver)
                )

            # Write stacked gtif file
            with rio.open(out_path, "w", **dest_kwargs) as dest:
                _stack_bands(sources, write_raster, dest)

            # Read and return array
            with rio.open(out_path, "r") as src:
                arr = src.read()
                meta = src.profile

                # If user specified nodata, mask the array
                if nodata is not None:
                    # Make sure value is same data type
                    nodata = np.array([nodata]).astype(arr.dtype)[0]

                    # Mask the array
                    arr = np.ma.masked_equal(arr, nodata)

                return arr, meta


def _stack_bands(sources, write_raster=False, dest=None):
    """Stack a set of bands into a single file.

    Parameters
    ----------
    sources : list of rasterio dataset objects
        A list of rasterio dataset objects you wish to stack. Objects
        will be stacked in the order provided in this list.
    dest : string (optional)
        Path to the where the output raster containing the stacked
        layers will be stored.
    write_raster : bool (default=False)
        Boolean to determine whether or not to write out the raster.

    Returns
    ----------
    tuple

        numpy array
            Numpy array generated from the stacked array combining all
            bands that were provided in the list.
        ret_prof : rasterio profile
            Updated rasterio spatial metadata object updated to represent
            the number of layers in the stack
    """

    try:
        for src in sources:
            src.profile

    except AttributeError:
        raise AttributeError("The sources object should be Dataset Reader")
        sys.exit()

    else:
        pass

    if write_raster:
        for ii, ifile in enumerate(sources):
            bands = sources[ii].read()
            if bands.ndim != 3:
                bands = bands[np.newaxis, ...]
            for band in bands:
                dest.write(band, ii + 1)

    else:
        stacked_arr = []
        for ii, ifile in enumerate(sources):
            bands = sources[ii].read()
            if bands.shape[0] == 1:
                bands = np.squeeze(bands)
            stacked_arr.append(bands)

        # Update the profile to have count==number of bands
        ret_prof = sources[0].profile.copy()
        ret_prof["count"] = len(stacked_arr)

        return np.array(stacked_arr), ret_prof


def crop_image(raster, geoms, all_touched=True):
    """Crop a single file using geometry objects.

    Parameters
    ----------
    raster : rasterio.io.DatasetReader object
        The rasterio object to be cropped.
    geoms : geopandas geodataframe or list of polygons
        The spatial polygon boundaries in GeoJSON-like dict format
        to be used to crop the image. All data outside of the polygon
        boundaries will be set to nodata and/or removed from the image.
    all_touched : bool (default=True)
        Include a pixel in the mask if it touches any of the
        shapes. If False, include a pixel only if its center is within one of
        the shapes, or if it is selected by Bresenham's line algorithm.
        (from rasterio)

    Returns
    ----------
    tuple

        out_image: cropped numpy array
            A numpy array that is cropped to the geoms object
            extent with shape (bands, rows, columns)
        out_meta:  dict
            A dictionary containing updated metadata for the cropped raster,
            including extent (shape elements) and transform properties.

    Example
    -------
        >>> import geopandas as gpd
        >>> import rasterio as rio
        >>> import earthpy.spatial as es
        >>> from earthpy.io import path_to_example
        >>> # Clip an RGB image to the extent of Rocky Mountain National Park
        >>> rmnp = gpd.read_file(path_to_example("rmnp.shp"))
        >>> with rio.open(path_to_example("rmnp-rgb.tif")) as src_raster:
        ...     cropped_raster, cropped_meta = es.crop_image(src_raster, rmnp)
        >>> src_raster.shape
        (373, 485)
        >>> cropped_raster.shape[1:3]
        (265, 281)
    """
    if isinstance(geoms, gpd.geodataframe.GeoDataFrame):
        clip_extent = [extent_to_json(geoms)]
    else:
        clip_extent = geoms
    out_image, out_transform = mask(
        raster, clip_extent, crop=True, all_touched=all_touched
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
    return out_image, out_meta


def crop_all(
    raster_paths,
    output_dir,
    geoms,
    overwrite=False,
    all_touched=True,
    verbose=True,
):
    """Takes a list of rasters and a boundary, and crops them efficiently.

    Parameters
    ----------
    raster_paths : list of file paths
        List of paths of rasters that will be cropped.
    output_dir : string
        Provide a single directory path if you wish to specify the
        location of the output cropped files only. _crop will be
        appended to the file name for each output cropped image.
    geoms : geopandas geodataframe or list of polygons
        The spatial polygon boundaries in GeoJSON-like dict format
        to be used to crop the image. All data outside of the polygon
        boundaries will be set to nodata and/or removed from the image.
    overwrite : bool (default=False)
        Disallows files to be overwritten if they exist already.
        Can be changed so that files can be overwritten with each
        run of the function. If False, will not overwrite existing
        files. If true, existing files will be overwritten.
    all_touched : bool (default=True)
        Include a pixel in the mask if it touches any of the
        shapes. If False, include a pixel only if its center i
        s within one of the shapes, or if it is selected by
        Bresenham's line algorithm.
        (from rasterio)
    verbose : bool (default=True)
        Returns a list of full file paths created by the function.
         If set to false, returns nothing.

    Returns
    ----------
    return files : list
        List of full file paths created by the function.

    Example
    -------
        >>> import os
        >>> import earthpy.spatial as es
        >>> import geopandas as gpd
        >>> from earthpy.io import path_to_example
        >>> band_fnames = ["red.tif", "green.tif", "blue.tif"]
        >>> paths = [path_to_example(fname) for fname in band_fnames]
        >>> rmnp = gpd.read_file(path_to_example("rmnp.shp"))
        >>> out_dir = os.path.commonpath(paths)
        >>> output_files = es.crop_all(paths, out_dir, rmnp, overwrite=True)
        >>> len(output_files)
        3
        >>> os.path.isfile(output_files[0])
        True
        >>> # Clean up example data
        >>> for bands in output_files:
        ...     os.remove(bands)

    """
    if not os.path.exists(output_dir):
        raise ValueError(
            "The output directory that you provided does not exist"
        )
    return_files = []
    for i, bands in enumerate(raster_paths):
        path_name, extension = bands.rsplit(".", 1)
        name = os.path.basename(os.path.normpath(path_name))
        outpath = os.path.join(output_dir, name + "_crop." + extension)
        return_files.append(outpath)
        if os.path.exists(outpath) and not overwrite:
            raise ValueError(
                "The file {0} already exists. If you wish to overwrite this "
                "file, set the overwrite argument to true.".format(outpath)
            )
        with rio.open(bands) as a_band:
            crop, meta = crop_image(a_band, geoms, all_touched=all_touched)
            with rio.open(outpath, "w", **meta) as dest:
                dest.write(crop)
    if verbose:
        return return_files


def bytescale(data, high=255, low=0, cmin=None, cmax=None):
    """Byte scales an array (image).

    Byte scaling converts the input image to uint8 dtype, and rescales
    the data range to ``(low, high)`` (default 0-255).
    If the input image already has dtype uint8, no scaling is done.
    Source code adapted from scipy.misc.bytescale (deprecated in scipy-1.0.0)

    Parameters
    ----------
    data : numpy array
        image data array.
    high : int (default=255)
        Scale max value to `high`.
    low : int (default=0)
        Scale min value to `low`.
    cmin : int (optional)
        Bias scaling of small values. Default is ``data.min()``.
    cmax : int (optional)
        Bias scaling of large values. Default is ``data.max()``.

    Returns
    -------
    img_array : uint8 numpy array
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
        cmin = float(data.min())

    if (cmax is None) or (cmax > data.max()):
        cmax = float(data.max())

    # Calculate range of values
    crange = cmax - cmin
    if crange < 0:
        raise ValueError("`cmax` should be larger than `cmin`.")
    elif crange == 0:
        raise ValueError(
            "`cmax` and `cmin` should not be the same value. Please specify "
            "`cmax` > `cmin`"
        )

    scale = float(high - low) / crange

    # If cmax is less than the data max, then this scale parameter will create
    # data > 1.0. clip the data to cmax first.
    data[data > cmax] = cmax
    bytedata = (data - cmin) * scale + low
    return (bytedata.clip(low, high) + 0.5).astype("uint8")


def hillshade(arr, azimuth=30, altitude=30):
    """Create hillshade from a numpy array containing elevation data.

    Parameters
    ----------
    arr : numpy array of shape (rows, columns)
        Numpy array with elevation values to be used to created hillshade.
    azimuth : float (default=30)
        The desired azimuth for the hillshade.
    altitude : float (default=30)
        The desired sun angle altitude for the hillshade.

    Returns
    -------
    numpy array
        A numpy array containing hillshade values.

    Example
    -------
    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import rasterio as rio
        >>> import earthpy.spatial as es
        >>> from earthpy.io import path_to_example
        >>> with rio.open(path_to_example('rmnp-dem.tif')) as src:
        ...     dem = src.read()
        >>> print(dem.shape)
        (1, 187, 152)
        >>> squeezed_dem = dem.squeeze() # remove first dimension
        >>> print(squeezed_dem.shape)
        (187, 152)
        >>> shade = es.hillshade(squeezed_dem)
        >>> plt.imshow(shade, cmap="Greys")
        <matplotlib.image.AxesImage object at 0x...>
    """
    try:
        x, y = np.gradient(arr)
    except ValueError:
        raise ValueError("Input array should be two-dimensional")

    if azimuth <= 360.0:
        azimuth = 360.0 - azimuth
        azimuthrad = azimuth * np.pi / 180.0
    else:
        raise ValueError(
            "Azimuth value should be less than or equal to 360 degrees"
        )

    if altitude <= 90.0:
        altituderad = altitude * np.pi / 180.0
    else:
        raise ValueError(
            "Altitude value should be less than or equal to 90 degrees"
        )

    slope = np.pi / 2.0 - np.arctan(np.sqrt(x * x + y * y))
    aspect = np.arctan2(-x, y)

    shaded = np.sin(altituderad) * np.sin(slope) + np.cos(
        altituderad
    ) * np.cos(slope) * np.cos((azimuthrad - np.pi / 2.0) - aspect)

    return 255 * (shaded + 1) / 2


# @deprecate
def stack_raster_tifs(band_paths, out_path, arr_out=True):
    """This function has been deprecated from earthpy.

    Please use the stack() function instead.
    """
    raise Warning("stack_raster_tifs is deprecated. Use stack(). Exiting...")
    sys.exit()
