import geopandas as gpd

"A module to clip vector data using geopandas"

# Create function to clip point data using geopandas


def clip_points(shp, clip_obj):
    '''
    Docs Here
    '''

    poly = clip_obj.geometry.unary_union
    return(shp[shp.geometry.intersects(poly)])

# Create function to clip line and polygon data using geopandas


def clip_line_poly(shp, clip_obj):
    '''
    docs
    '''

    # Create a single polygon object for clipping
    poly = clip_obj.geometry.unary_union
    spatial_index = shp.sindex

    # Create a box for the initial intersection
    bbox = poly.bounds
    # Get a list of id's for each road line that overlaps the bounding box and subset the data to just those lines
    sidx = list(spatial_index.intersection(bbox))
    #shp_sub = shp[shp.index.isin(sidx)]
    shp_sub = shp.iloc[sidx]

    # Clip the data - with these data
    clipped = shp_sub.copy()
    clipped['geometry'] = shp_sub.intersection(poly)

    # Return the clipped layer with no null geometry values
    return(clipped[clipped.geometry.notnull()])


# Final clip function that handles points, lines and polygons


def clip_shp(shp, clip_obj):
   """A function to clip points, lines, polygon geometries based on an input
   geometry.

   Both layers must be the same CRS.

   Depending on the geometry type, input data will be clipped to the full
   extent of clip_obj using either clip_points or clip_line_poly.

   If there are multiple polygons in object,
   data will be clipped to the total boundary of
   all polygons.

   Parameters
   ----------
   shp : geopandas dataframe
        Vector layer (point, line, polygon) to be clipped to clip_obj.

   clip_obj : dataset to which data is to be clipped.

   Returns
   -------
   Points, lines, polygons clipped to vector boundary."""

    if shp["geometry"].iloc[0].type == "Point":
        return(clip_points(shp, clip_obj))
    else:
        return(clip_line_poly(shp, clip_obj))
