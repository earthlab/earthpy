"A module to clip vector data using geopandas"

# TODO: Clip poly should use OVERLAY not spatial indexing + intersects


def _clip_points(shp, clip_obj):
    """ A function to clip point geometry using geopandas. Takes an
    input point GeoDataFrame that will be clipped to the clip_obj
    GeoDataFrame.

    Points that intersect with the geometry of clip_obj are extracted
    and returned.

    Parameters
    ----------
    shp : GeoDataFrame
        Composed of point geometry that is clipped to clip_obj

    clip_obj : GeoDataFrame
        Reference polygon for clipping.

    Returns
    -------
    GeoDataFrame
        The returned GeoDataFrame is a subset of shp that intersects
        with clip_obj
    """
    poly = clip_obj.geometry.unary_union
    return shp[shp.geometry.intersects(poly)]


def _clip_line_poly(shp, clip_obj):
    """A function to clip line and polygon data using geopandas.

    Takes an input GeoDataFrame that is used as the clipped data, and a second
    GeoDataFrame that is used as the clipping object or reference area.

    A spatial index is created around the shp input and is then intersected
    with the bounding box of the clip_obj.

    Data within this intersection is extracted from shp and the resulting
    subset is the output of the function.

    Parameters
    ----------
    shp : GeoDataFrame
        Line or polygon geometry that is clipped to clip_obj

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
    """A function to clip points, lines, polygon geometries based on an input
    geometry.

    Both layers must be in the same Coordinate Reference System (CRS).

    Depending on the geometry type, input data will be clipped to the full
    extent of clip_obj using either _clip_points or _clip_line_poly.

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

        >>> import matplotlib.pyplot as plt
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

    Plotting the clipped sections of the points, lines, and polygons.

    .. plot::

        >>> import matplotlib.pyplot as plt
        >>> import geopandas as gpd
        >>> import earthpy.clip as cl
        >>> from earthpy.io import path_to_example
        >>> rmnp = gpd.read_file(path_to_example('rmnp.shp'))
        >>> glaciers = gpd.read_file(path_to_example('colorado-glaciers.geojson'))
        >>> rmnp_glaciers = cl.clip_shp(glaciers, rmnp)
        >>> cdt = gpd.read_file(path_to_example('continental-div-trail.geojson'))
        >>> rmnp_cdt_section = cl.clip_shp(cdt, rmnp)
        >>> counties = gpd.read_file(path_to_example('colorado-counties.geojson'))
        >>> rmnp_counties = cl.clip_shp(counties, rmnp)
        >>> fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(8, 3))
        >>> ax1.set_axis_off()
        >>> ax2.set_axis_off()
        >>> ax3.set_axis_off()
        >>> rmnp_glaciers.plot(ax=ax1) #doctest: +ELLIPSIS
        <matplotlib.axes._subplots.AxesSubplot object at 0x...>
        >>> rmnp.boundary.plot(ax=ax1, color='red') #doctest: +ELLIPSIS
        <matplotlib.axes._subplots.AxesSubplot object at 0x...>
        >>> ax1.set_title('Clipped Points') #doctest: +ELLIPSIS
        Text(...'Clipped Points')
        >>> rmnp_cdt_section.plot(ax=ax2) #doctest: +ELLIPSIS
        <matplotlib.axes._subplots.AxesSubplot object at 0x...>
        >>> rmnp.boundary.plot(ax=ax2, color='red') #doctest: +ELLIPSIS
        <matplotlib.axes._subplots.AxesSubplot object at 0x...>
        >>> ax2.set_title('Clipped Lines') #doctest: +ELLIPSIS
        Text(...'Clipped Lines')
        >>> rmnp_counties.plot(ax=ax3) #doctest: +ELLIPSIS
        <matplotlib.axes._subplots.AxesSubplot object at 0x...>
        >>> rmnp.boundary.plot(ax=ax3, color='red') #doctest: +ELLIPSIS
        <matplotlib.axes._subplots.AxesSubplot object at 0x...>
        >>> ax3.set_title('Clipped Polygon') #doctest: +ELLIPSIS
        Text(...'Clipped Polygon')
        >>> plt.show()
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
