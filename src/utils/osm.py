import os
import subprocess

import geopandas as gpd

def convert_osm_to_gpkg(input_filename: str, tmp_filename: str, layer_name: str):
    tmp_filename = os.path.join('/', 'tmp', tmp_filename)
    command = "ogr2ogr -f gpkg {output} --config OSM_USE_CUSTOM_INDEXING NO {input}"
    subprocess.run(command.format(input=input_filename, output=tmp_filename), shell=True)
    return gpd.read_file(tmp_filename, layer='lines')

def convert_osm2shape(in_file, out_file, geom_type='multipolygons'):

    """
    Translate an OSM .pbf or .xml file to a shape file
    Note this will need you to select the geometry type from the OSM file:
    points, lines, multilinestrings, multipolygons
    """
    # Dict of possible geometry types in OSM XML, same names of layers in temp geopackage
    geom_types = ['points', 'lines', 'multilinestrings', 'multipolygons', 'other_relations']
    if geom_type not in geom_types:
        raise ValueError("Invalid geom type. Expected one of: %s" % geom_types)

    # Set output geometry type for shapefile
    out_driver = ogr.GetDriverByName('ESRI Shapefile')
    gdal.SetConfigOption('OSM_USE_CUSTOM_INDEXING', 'NO')
    # Delete if previously exists
    if os.path.exists(out_file):
        out_driver.DeleteDataSource(out_file)
    # Create file and layer
    out_ds = out_driver.CreateDataSource(out_file)
    in_ds = ogr.Open(in_file)
    in_lyr = in_ds.GetLayerByName(geom_type)
    out_lyr = out_ds.CopyLayer(in_lyr, geom_type, options=['OVERWRITE=YES', 'ENCODING=UTF-8'])
    out_lyr.SyncToDisk()