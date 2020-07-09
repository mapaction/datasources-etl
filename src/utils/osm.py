import os
import subprocess

import geopandas as gpd

def convert_osm_to_gpkg(input_filename: str, tmp_filename: str, layer_name: str):
    tmp_filename = os.path.join('/', 'tmp', tmp_filename)
    command = "ogr2ogr -f gpkg {output} --config OSM_USE_CUSTOM_INDEXING NO {input}"
    subprocess.run(command.format(input=input_filename, output=tmp_filename), shell=True)
    return gpd.read_file(tmp_filename, layer='lines')

