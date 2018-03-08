"""File Input/Output utilities."""

from download import download
import os.path as op
import os
import matplotlib.pyplot as plt

# plt.style.use('ggplot')

DATA_URLS = {
    'week_02': [('https://ndownloader.figshare.com/files/7010681',
                 'boulder-precip.csv'),
                ('https://ndownloader.figshare.com/files/7010681',
                 'temperature_example.csv')],
    'week_02-hw': ('https://ndownloader.figshare.com/files/7426738', 'ZIPFILE'),
    'week_03': ('https://ndownloader.figshare.com/files/7446715', 'ZIPFILE'),
    'week_04': ('https://ndownloader.figshare.com/files/7525363', 'ZIPFILE'),
    'week_05': ('https://ndownloader.figshare.com/files/7525363', 'ZIPFILE'),
    'week_07': [('https://ndownloader.figshare.com/files/7677208', 'ZIPFILE')]
}

#               destfile = "data/boulder-precip.csv"'}
HOME = op.join(op.expanduser('~'))
DATA_NAME = op.join('earth-analytics', 'data')
path = None

#def __init__(self, path=None):
    if path is None:
        path = op.join(HOME, DATA_NAME)
    path = path
    data_keys = list(DATA_URLS.keys())


#def __repr__(self):
    s = 'Available Datasets: {}'.format(data_keys)
    #return s

def get_data(self, key=None, name=None, replace=False, zipfile=True):
    """
    Retrieve the data for a given week and return its path.

    This will retrieve data from the internet if it isn't already
    downloaded, otherwise it will only return a path to that dataset.

    Parameters
    ----------
    key : str
        The dataset to retrieve. Possible options can be found in
        ``self.data_keys``.
    replace : bool
        Whether to replace the data for this key if it is
        already downloaded.
    zipfile : bool
        Whether the dataset is a zip file.

    Returns
    -------
    path_data : str
        The path to the downloaded data.
    """
    # alt+shift+e to run
    key=None
    # ok this checks to ensure hte data selected is one available in the dictionary
    if key is None:
        print('Available datasets: {}'.format(
            list(DATA_URLS.keys())))
    elif key not in DATA_URLS:
        raise ValueError("Don't understand key "
                         "{}\nChoose one of {}".format(
            key, DATA_URLS.keys()))
    # if the key is found... get the data

    key = "week_02-hw"
    else:
        this_data = DATA_URLS[key]
        if not isinstance(this_data, list):
            this_data = [this_data]
        data_paths = []
        for url, name in this_data:
            name = key if name is None else name
            if zipfile is True:
                # could this be if name = "ZIPFILE" ??
                name = key
                this_root = path
                this_path = download(url,
                                     path=os.path.join(this_root, name),
                                     replace=replace, kind='zip',
                                     verbose=False)
            else:
                this_root = op.join(self.path, key)
                this_path = download(url, os.path.join(this_root, name),
                                     replace=replace,
                                     verbose=False)
            # this_path = download(url, os.path.join(this_root, name),
            #                     replace=replace, zipfile=zipfile,
            #                     verbose=False)
            data_paths.append(this_path)
        if len(data_paths) == 1:
            data_paths = data_paths[0]
        return data_paths
