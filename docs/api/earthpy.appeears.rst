earthpy.appeears
================

.. automodule:: earthpy.api.appeears
   :members:
   :undoc-members:
   :show-inheritance:

Examples
--------

The AppEEARS client can be configured with Earthdata credentials using the
standard environment variables expected by the authentication helper:

>>> import os
>>> os.environ["EARTHDATA_USERNAME"] = "user@example.com"
>>> os.environ["EARTHDATA_PASSWORD"] = "secret-password"
>>> from earthpy.api.auth import Authenticator
>>> creds = Authenticator("urs.earthdata.nasa.gov", env_prefix="EARTHDATA")
>>> creds.get_env_credentials()
('user@example.com', 'secret-password')

A downloader instance is created with the product, layer, date range, and a
GeoDataFrame boundary. In doctests, it is useful to inspect the object
configuration rather than perform a live API call:

>>> import geopandas as gpd
>>> from shapely.geometry import Polygon
>>> polygon = gpd.GeoDataFrame(
...     geometry=[
...         Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
...     ]
... )
>>> from earthpy.api.appeears import AppeearsDownloader
>>> downloader = AppeearsDownloader(
...     product="MOD13Q1.061",
...     layer="_250m_16_days_NDVI",
...     start_date="01-01-2021",
...     end_date="01-20-2021",
...     polygon=polygon,
...     download_key="example-job",
...     interactive=False,
... )
>>> downloader.download_key
'example-job'
>>> downloader._product
'MOD13Q1.061'
