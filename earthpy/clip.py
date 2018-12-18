"A module to clip vector data using geopandas"

# TODO: Clip poly should use OVERLAY not spatial indexing + intersects


def clip_points(shp, clip_obj):
    """ A function to clip point geometry using geopandas. Takes an
    input point GeoDataFrame that will be clipped to the clip_obj
    GeoDataFrame.

    Points that intersect with the geometry of clip_obj are extracted
    and returned.


    Parameters
    ------------------
    shp: GeoDataFrame
        Composed of point geometry that is clipped to clip_obj

    clip_obj: GeoDataFrame
        Reference polygon for clipping points.
        The clip_obj's geometry is dissolved into one geometric feature
        and intersected with the points of shp.


    Returns
    -------------------
    GeoDataFrame:

        The returned GeoDataFrame is a subset of shp that intersects
        with clip_obj
    """
    poly = clip_obj.geometry.unary_union
    return shp[shp.geometry.intersects(poly)]


def clip_line_poly(shp, clip_obj):
    """A function to clip line and polygon data using geopandas.

    Takes an input GeoDataFrame that is used as the clipped data, and a second
    GeoDataFrame that is used as the clipping object or reference area.

    A spatial index is created around the shp input and is then intersected
    with the bounding box of the clip_obj.

    Data within this intersection is extracted from shp and the resulting
    subset is the output of the function.

    Parameters
    ---------------------
     shp: GeoDataFrame
        Line or polygon geometry that is clipped to the reference
        area provided by the clip_obj

     clip_obj: GeoDataFrame
        Polygon geometry that provides the reference area for clipping
        the input. The clip_obj's geometry is dissolved into one geometric
        feature and intersected with the spatial index of the shp input.

     Returns
     -----------------------
     GeoDataFrame:

        The returned GeoDataFrame is a clipped subset of shp
        that intersects with clip_obj.
    """
    # Create a single polygon object for clipping
    poly = clip_obj.geometry.unary_union
    spatial_index = shp.sindex

    # Create a box for the initial intersection
    bbox = poly.bounds
    # Get a list of id's for each object that overlaps the bounding box and
    # subset the data to just those lines
    sidx = list(spatial_index.intersection(bbox))
    shp_sub = shp.iloc[sidx]

    # Clip the data - with these data
    clipped = shp_sub.copy()
    clipped["geometry"] = shp_sub.intersection(poly)

    # Return the clipped layer with no null geometry values
    return clipped[clipped.geometry.notnull()]


def clip_shp(shp, clip_obj):
    """A function to clip points, lines, polygon geometries based on an input
    geometry.

    Both layers must be in the same Coordinate Reference System (CRS).

    Depending on the geometry type, input data will be clipped to the full
    extent of clip_obj using either clip_points or clip_line_poly.

    If there are multiple polygons in clip_obj,
    data from shp will be clipped to the total boundary of
    all polygons in clip_obj.

    Parameters
    ----------
    shp : GeoDataFrame
          Vector layer (point, line, polygon) to be clipped to clip_obj.

    clip_obj : GeoDataFrame
          Polygon vector layer used to clip shp.

    Returns
    -------
    GeoDataFrame:
         Vector data (points, lines, polygons) from shp clipped to
         polygon boundary from clip_obj.
    """
    try:
        shp.geometry
        clip_obj.geometry
    except AttributeError:
        raise AttributeError(
            """Please make sure that your input and clip
                             GeoDataFrames have a valid
                             geometry column"""
        )

    if not any(shp.intersects(clip_obj.unary_union)):
        raise ValueError("Shape and crop extent do not overlap.")

    # Multipolys / point / line don't clip properly
    if "Multi" in str(clip_obj.geom_type) or "Multi" in str(shp.geom_type):
        raise ValueError(
            """Clip doesn't currently support multipart
        geometries. Consider using .explode to create
        unique features in your GeoDataFrame"""
        )

    if shp["geometry"].iloc[0].type == "Point":
        return clip_points(shp, clip_obj)
    else:
        return clip_line_poly(shp, clip_obj)
