import os
import numpy as np
import rasterio as rio
from shapely.geometry import Polygon, mapping
from tqdm import tqdm

# This should be moved to the new package that handles data download
# and the website build potentially
def fix_paths(path, images_folder="images"):
    """
    Replace the path that contains the site root with {{ site.url }}, in
    order to make the path usable outside of the local context.

    Parameters
    ----------
    path : str
        The path that needs to be modified
    images_folder : str
        Name of the desired folder to recieve images. Defaults to 
        the users 'images' folder.

    Returns
    -------
    new_path : str
        The fixed path that contains the new site root.
    """
    img_from_root = path.split(images_folder + os.sep)[-1].split(os.sep)
    new_path = os.path.join("{{ site.url }}", images_folder, *img_from_root)
    return new_path
