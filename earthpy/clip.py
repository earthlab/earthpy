"""
earthpy.clip
============

A module to clip vector data using GeoPandas.

"""

import pandas as pd
import geopandas as gpd

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


def _clip_multi_poly_line(shp, clip_obj):
    """Clip multi lines and polygons to the clip_obj GeoDataFrame extent.

    Clip an input multi line or polygon to the polygon extent of the clip_obj
    parameter. Lines or Polygons that intersect the clip_obj geometry are
    extracted with associated attributes and returned.

    Parameters
    ----------
    shp : GeoDataFrame
        multiLine or multipolygon geometry that is clipped to clip_obj.

    clip_obj : GeoDataFrame
        Reference polygon for clipping.

    Returns
    -------
    GeoDataFrame
        The returned GeoDataFrame is a clipped subset of shp
        that intersects with clip_obj.
    """

    # This feels super hacky
    lines_exist = False
    polys_exist = False
    # Clip multi polygons
    clipped = _clip_line_poly(shp.explode().reset_index(level=[1]), clip_obj)

    # If there are lines, handle line dissolves
    if any(clipped.geometry.type == "MultiLineString") or any(
        clipped.geometry.type == "LineString"
    ):
        lines_exist = True
        lines = clipped[
            (clipped.geometry.type == "MultiLineString")
            | (clipped.geometry.type == "LineString")
        ]
        line_diss = lines.dissolve(by=[lines.index]).drop(columns="level_1")

    # If there are poly's handle polys
    if any(clipped.geometry.type == "MultiPolygon") or any(
        clipped.geometry.type == "Polygon"
    ):
        polys_exist = True
        # Just get the polygons
        polys = clipped[clipped.geometry.type == "Polygon"]
        poly_diss = polys.dissolve(by=[polys.index]).drop(columns="level_1")

        # TODO if this is a poly input, can you merge lines and polys (unary_union)??
        # TODO handle -- All polys, 2) polys and lines and then 3 just lines (do we want to do this?)
        # Dissolve the polys and lines back together
        # If both lines and polys exist combine and return
        # note that this isn't ideal as we probably want to think this through
        # this is pretty sloppy
    if lines_exist and polys_exist:
        return gpd.GeoDataFrame(
            pd.concat([poly_diss, line_diss], ignore_index=True)
        )
    elif lines_exist:
        return line_diss
    else:
        return poly_diss


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
            "Please make sure that your input and clip GeoDataFrames have a"
            " valid geometry column"
        )

    # if clip_obj["geometry"].iloc[0].type != "Polygon":
    # raise AttributeError("Trying to clip an object with something other then a polygon.")

    if not any(shp.intersects(clip_obj.unary_union)):
        raise ValueError("Shape and crop extent do not overlap.")

    # if any(clipped.geometry.type == "MultiPolygon"):
    #     _clip_multi_poly(shp, clip_obj)

    # Multipolys / point / line clip differently then non-multi features.
    # TODO turn into a multi point clip function
    if any(shp.geometry.type == "MultiPoint"):
        # if "Multi" in str(shp.geom_type):
        if (
            shp["geometry"].iloc[0].type == "Point"
            or shp["geometry"].iloc[0].type == "MultiPoint"
        ):
            # This line works
            clipped = _clip_points(
                shp.explode().reset_index(level=[1]), clip_obj
            )
            return clipped.dissolve(by=[clipped.index]).drop(
                columns="level_1"
            )[shp.columns.tolist()]
        # else:
        # If there are multi lines or polygons handle the complex geoms
    if any(shp.geometry.type == "MultiPolygon") or any(
        shp.geometry.type == "MultiLineString"
    ):
        return _clip_multi_poly_line(shp, clip_obj)
        # # Clip multi polygons
        # clipped = _clip_line_poly(shp.explode().reset_index(level=[1]), clip_obj)
        # # If there are lines and poly's you can't just dissolve
        # if any(clipped.geometry.type == "MultiLineString"):
        #     # Just get the polygons
        #     polys = clipped[clipped.geometry.type == "Polygon"]
        #     lines = clipped[clipped.geometry.type == "MultiLineString"]
        #     # Dissolve the polys and lines back together
        #     poly_diss = polys.dissolve(by=[polys.index]).drop(columns='level_1')
        #     line_diss = lines.dissolve(by=[polys.index]).drop(columns='level_1')
        #
        # return gpd.GeoDataFrame(pd.concat([poly_diss, line_diss], ignore_index=True))
        # return clipped.dissolve(by=[clipped.index]).drop(columns='level_1')[shp.columns.tolist()]
    # elif shp["geometry"].iloc[0].type == "Point":
    #     return _clip_points(shp, clip_obj)
    # else:
    if shp["geometry"].iloc[0].type == "Point":
        return _clip_points(shp, clip_obj)
    else:
        return _clip_line_poly(shp, clip_obj)


# try:
#     clipped.geometry.type == "MultiLineString"
