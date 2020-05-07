import geopandas as gpd


def poly_to_line(geodataframe):
    """takes a geopandas geodataframe with polygon geometry and replaces the geometry with lines"""

    # read in data from input file
    boundary_data = geodataframe

    # create new geometry column, replace original geometry column
    boundary_data.rename_geometry('geom_old',True)
    boundary_data['geometry'] = boundary_data.geometry.boundary
    boundary_data = boundary_data.set_geometry('geometry')
    boundary_data = boundary_data.drop('geom_old', 1)

    return boundary_data