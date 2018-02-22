import os
import rasterio as rio
import numpy as np
from shapely.geometry import Polygon, mapping
from tqdm import tqdm

def fix_paths(path, images_folder='images'):
    """Replace the path that contains the site root with {{ site.url }}.
    """
    img_from_root = path.split(images_folder + os.sep)[-1].split(os.sep)
    new_path = os.path.join('{{ site.url }}', images_folder, *img_from_root)
    return new_path

def bounds_to_box(left, right, bottom, top):
    """Convert bounds to a shapely box.

    This is useful for cropping a raster image.
    """
    box = [(left, bottom), (left, top), (right, top), (right, bottom)]
    box = Polygon(box)
    return box

def crop_image(path, geoms, path_out=None):
    """Crop a single file using geometry objects.

    Parameters
    ----------
    path : str
        The path to the raster file to crop
    geoms : list of polygons
        Polygons are GeoJSON-like dicts specifying the boundaries of features
        in the raster to be kept. All data outside of specified polygons
        will be set to nodata.
    path_out : str | None
        The path to the file to be written to disk. If `None`, the input
        path will be overwritten.
    """
    # Mask the input image and update the metadata
    with rio.open(path) as src:
        out_image, out_transform = rio.mask.mask(src, geoms, crop = True)
        out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})

    # Write to a new raster file
    if path_out is None:
        path_out = path
    with rio.open(path_out, "w", **out_meta) as dest:
        dest.write(out_image)

def stack(band_paths, out_path, return_raster=True):
    """Stack a set of bands into a single file.

    Parameters
    ----------
    bands : list of file paths
        A list with paths to the bands you wish to stack. Bands
        will be stacked in the order given in this list.
    out_path : string
        A path for the output file.
    return_raster : bool
        Whether to return a refernce to the opened output
        raster file.
    """
    # Read in metadata
    first_band = rio.open(band_paths[0], 'r')
    meta = first_band.meta.copy()

    # Replace metadata with new count
    counts = 0
    for ifile in band_paths:
        with rio.open(ifile, 'r') as ff:
            counts += ff.meta['count']
    meta.update(count=counts)

    # create a new file
    with rio.open(out_path, 'w', **meta) as ff:
        for ii, ifile in tqdm(enumerate(band_paths)):
            bands = rio.open(ifile, 'r').read()
            if bands.ndim != 3:
                bands = bands[np.newaxis, ...]
            for band in bands:
                ff.write(band, ii+1)

    if return_raster is True:
        return rio.open(out_path)
