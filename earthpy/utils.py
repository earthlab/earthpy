import os
import rasterio as rio
import numpy as np
from shapely.geometry import Polygon, mapping
from tqdm import tqdm

# This should be moved to the new package that handles data download
# and the website build potentially 
def fix_paths(path, images_folder='images'):
    """
    Replace the path that contains the site root with {{ site.url }}.
    """
    img_from_root = path.split(images_folder + os.sep)[-1].split(os.sep)
    new_path = os.path.join('{{ site.url }}', images_folder, *img_from_root)
    return new_path
