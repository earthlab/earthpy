"A module to clip vector data using geopandas"

# TODO: Clip poly should use OVERLAY not spatial indexing + intersects


def _clip_points(shp, clip_obj):
    """Clip point geometry to the clip_obj GeoDataFrame extent.

    Clip an input point GeoDataFrame to the polygon extent of the clip_obj
    parameter. Points that intersect the clip_obj geometry are extracted with
    associated attributes and returned.

    Parameters
    ----------
    shp : GeoDataFrame
        Composed of point geometry that is clipped to clip_obj.

    clip_obj : GeoDataFrame
        Reference polygon for clipping.

    Returns
    -------
    GeoDataFrame
        The returned GeoDataFrame is a subset of shp that intersects
        with clip_obj.
    """
    poly = clip_obj.geometry.unary_union
    return shp[shp.geometry.intersects(poly)]


def _clip_line_poly(shp, clip_obj):
    """Clip line and polygon geometry to the clip_obj GeoDataFrame extent.

    Clip an input line or polygon to the polygon extent of the clip_obj
    parameter. Lines or Polygons that intersect the clip_obj geometry are
    extracted with associated attributes and returned.

    Parameters
    ----------
    shp : GeoDataFrame
        Line or polygon geometry that is clipped to clip_obj.

    clip_obj : GeoDataFrame
        Reference polygon for clipping.

    Returns
    -------
    GeoDataFrame
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
    """Clip points, lines, or polygon geometries to the clip_obj extent.

    Both layers must be in the same Coordinate Reference System (CRS) and will
    be clipped to the full extent of the clip object.

    If there are multiple polygons in clip_obj,
    data from shp will be clipped to the total boundary of
    all polygons in clip_obj.

    Parameters
    ----------
    shp : GeoDataFrame
          Vector layer (point, line, polygon) to be clipped to clip_obj.
    clip_obj : GeoDataFrame
          Polygon vector layer used to clip shp.
          The clip_obj's geometry is dissolved into one geometric feature
          and intersected with shp.

    Returns
    -------
    GeoDataFrame
         Vector data (points, lines, polygons) from shp clipped to
         polygon boundary from clip_obj.

    Examples
    --------
    Clipping points (glacier locations in the state of Colorado) with
    a polygon (the boundary of Rocky Mountain National Park):

        >>> import geopandas as gpd
        >>> import earthpy.clip as cl
        >>> from earthpy.io import path_to_example
        >>> rmnp = gpd.read_file(path_to_example('rmnp.shp'))
        >>> glaciers = gpd.read_file(path_to_example('colorado-glaciers.geojson'))
        >>> glaciers.shape
        (134, 2)
        >>> rmnp_glaciers = cl.clip_shp(glaciers, rmnp)
        >>> rmnp_glaciers.shape
        (36, 2)

    Clipping a line (the Continental Divide Trail) with a
    polygon (the boundary of Rocky Mountain National Park):

        >>> cdt = gpd.read_file(path_to_example('continental-div-trail.geojson'))
        >>> rmnp_cdt_section = cl.clip_shp(cdt, rmnp)
        >>> cdt['geometry'].length > rmnp_cdt_section['geometry'].length
        0    True
        dtype: bool

    Clipping a polygon (Colorado counties) with another polygon
    (the boundary of Rocky Mountain National Park):

        >>> counties = gpd.read_file(path_to_example('colorado-counties.geojson'))
        >>> counties.shape
        (64, 13)
        >>> rmnp_counties = cl.clip_shp(counties, rmnp)
        >>> rmnp_counties.shape
        (4, 13)
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
        return _clip_points(shp, clip_obj)
    else:
        return _clip_line_poly(shp, clip_obj)
