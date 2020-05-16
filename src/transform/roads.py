import sys

import geopandas as gpd
import fiona
from jsonschema import validate

from utils.yaml_api import parse_yaml

GADM_FILENAME = 'gadm36_{ISO3}.gpkg'
GADM_LAYER = 'gadm36_{ISO3}_0'


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3])


def transform_gadm():
    transform('gadm', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    config = parse_yaml('config.yml')

    if source == "cod":
        df_roads = gpd.read_file(f'zip://{input_filename}')

#TODO Fix schema check, CRS, column names and validation
#        schema_mapping = {
#            'admin0Name_en': 'name_en'
#        }

    # Change CRS
#   df_roads = df_roads.to_crs(config['constants']['crs'])
    # Modify the column names to suit the schema
#    df_roads = df_roads.rename(columns=schema_mapping)
    # Make columns needed for validation
#   df_roads['geometry_type'] = df_roads['geometry'].apply(lambda x: x.geom_type)
#   df_roads['crs'] = df_roads.crs
    # Validate
#   validate(instance=df_roads.to_dict('list'), schema=parse_yaml(schema_filename))
    # Write to output
    df_roads.to_file(output_filename)
