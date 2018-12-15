Earthpy example datasets
========================

The earthpy package contains some small datasets that are used in examples.
This README file describes these example datasets at a high level, including
their sources and any relevant licensing information.


# Rocky Mountain National Park boundary

A simplified polygon of the Rocky Mountain National Park boundary.

### Filename

`rmnp.shp`

### Source

The RMNP boundary was extracted from the National Park Service boundary
dataset from the A-16 Federally Derived Data Open Data Catalog:
https://public-nps.opendata.arcgis.com/datasets/0b69abf463aa4a44b0ba45988fbba8af_0

### License

The National Park Service shall not be held liable for improper or incorrect
use of the data described and / or contained herein. These data and related
graphics (i.e. GIF or JPG format files) are not legal documents and are not
intended to be used as such. The information contained in these data is dynamic
and may change over time. The data are not better than the original sources
from which they were derived. It is the responsibility of the data user to use
the data appropriately and consistent within the limitations of geospatial data
in general and these data in particular. The related graphics are intended to
aid the data user in acquiring relevant data it is not appropriate to use the
related graphics as data. The National Park Service gives no warranty,
expressed or implied, as to the accuracy, reliability, or completeness of these
data. It is strongly recommended that these data are directly acquired from an
NPS server and not indirectly through other sources which may have changed the
data in some way. Although these data have been processed successfully on
computer systems at the National Park Service, no warranty expressed or implied
is made regarding the utility of the data on other systems for general or
scientific purposes, nor shall the act of distribution constitute any such
warranty. This disclaimer applies both to individual use of the data and
aggregate use with other data.



# Rocky Mountain National Park digital elevation model

A digital elevation model for Rocky Mountain National Park.

### Filename

`rmnp-dem.tif`

### Source

Created from terrain tiles on Amazon Web Services:
https://aws.amazon.com/public-datasets/terrain/

### License

License information can be found here: https://mapzen.com/terms/



# Colorado glacier locations

Point locations of glaciers in the state of Colorado.

### Filename

`colorado-glaciers.geojson`

### Source

This dataset is a subset of the GLIMS Glacier Database that includes
point locations of glaciers in the state of Colorado, USA, with the original
source data available here:
http://www.glims.org/download/glims_db_20171027.zip

### License

License information and other documentation can be found at
http://www.glims.org/download/00README_GLIMS.txt



# RGB imagery for Rocky Mountain National Park

Low resolution RGB satellite imagery over RMNP, as a three channel GeoTIFF, and
separate one channel GeoTIFF files.

### Filename

`rmnp-rgb.tif`, `red.tif`, `green.tif`, `blue.tif`

### Source

This Landsat imagery was originally showcased on NASA's Visible Earth website:
https://visibleearth.nasa.gov/view.php?id=88405.
The data provided in Earthpy have been spatially coarsened and reprojected to
reduce the file size, and we have also provided additional single band GeoTIFF
files (`red.tif`, `green.tif`, and `blue.tif`), to use in examples that stack
raster layers.

### License

There are no restrictions on the use of data received from the U.S. Geological
Survey's Earth Resources Observation and Science (EROS) Center or NASA's Land
Processes Distributed Active Archive Center (LP DAAC), unless expressly
identified prior to or at the time of receipt. More information on licensing
and Landsat data citation is available from USGS.



# Colorado counties polygons

Simplified polygons for every county in Colorado.

### Filename

`colorado-counties.geojson`

### Source

U.S. Census Bureau: https://www.census.gov/geo/maps-data/data/cbf/cbf_counties.html

### License

Public Domain



# EPSG code to proj4string dictionary

A dictionary that maps numeric EPSG codes to their proj4string representations.

### Filename

`epsg.json`

### Source

TODO: name source

### License

TODO: include license info



# Continental Divide Trail path

A simplified path of the Continental Divide Trail

### Filename

`continental-div-trail.geojson`

### Source

Continental Divide Trail Coalition data clearinghouse:
https://continentaldividetrail.org/cdt-data/

### License

All data is provided without warranty and for use at your own risk, please read
the data disclaimer below.

Improved gravel or surfaced roads are not official sections of the CDNST travel
route.  Information contained online, in map books or other publications, is
dynamic and may change over time. Landownership is not depicted and access
through non-Federal areas is only allowed at the discretion or by agreement
with the landowner. CDTC and the U.S. Forest Service shall not be responsible
for errors or omissions in the data and shall not be obligated to provide
updates, additions, or corrections to the data in the future. CDTC and the U.S.
Forest Service give no warranty, expressed or implied, as to the accuracy,
reliability, or completeness of the information. CDTC and the U.S. Forest
Service shall not be held liable for improper or incorrect use of the data
described and/or contained herein.
