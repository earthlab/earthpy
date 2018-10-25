import geopandas as gpd

"A module to clip vector data using geopandas"

# Create function to clip point data using geopandas


def clip_points(shp, clip_obj):
    '''
    A function to clip point geomerty using geopandas. Takes an input point shapefile that will be clipped to the clip_obj.
    Points will be extracted that intersect with the clipping object.

         shp: A shapefile composed of point geometry that is to be clipped to clip_obj

    clip_obj: A shapefile composed of polygon geometry that is used as the reference area for clipping
              the point data. The clip_obj's geometry is dissolved into a single geometric feature, Points
              that intersect with the resulting geometry are then extracted from the reference area.
    '''

    poly = clip_obj.geometry.unary_union
    return(shp[shp.geometry.intersects(poly)])

# Create function to clip line and polygon data using geopandas


def clip_line_poly(shp, clip_obj):
    '''
    A function to clip line and polygon data using geopandas. Takes an input shapefile that is used as the clipped
    data, and a second shapefile that is used as the clipping object or reference areaself. A spatial index is created
    around the 'shp' input and is then intersected with the bounding box of the clip_obj. Data within this intersection
    is extracted from the 'shp' attribute table and the resulting subset is the output of the function.

         shp: A shapefile composed of line or polygon geometry that is clipped down to the reference area provided by then
              clip_obj

    clip_obj: A shapefile composed of polygon geometry that provides the reference area for clipping the 'shp' inputself.
              The clip_obj's geometry is dissolved into a single geometric feature and intersected with the spatial sindex
              of the 'shp' input.


    '''

    # Create a single polygon object for clipping
    poly = clip_obj.geometry.unary_union
    spatial_index = shp.sindex

    # Create a box for the initial intersection
    bbox = poly.bounds
    # Get a list of id's for each road line that overlaps the bounding box and subset the data to just those lines
    sidx = list(spatial_index.intersection(bbox))
    shp_sub = shp.iloc[sidx]

    # Clip the data - with these data
    clipped = shp_sub.copy()
    clipped['geometry'] = shp_sub.intersection(poly)

    # Return the clipped layer with no null geometry values
    return(clipped[clipped.geometry.notnull()])


# Final clip function that handles points, lines and polygons


def clip_shp(shp, clip_obj):
    '''
    '''
    if shp["geometry"].iloc[0].type == "Point":
        return(clip_points(shp, clip_obj))
    else:
        return(clip_line_poly(shp, clip_obj))
