import sys

import geopandas as gpd
from jsonschema import validate

from utils.yaml_api import parse_yaml

GADM_FILENAME = 'gadm36_{ISO3}.gpkg'
GADM_LAYER = 'gadm36_{ISO3}_2'


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3])


def transform_gadm():
    transform('gadm', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    config = parse_yaml('config.yml')

##TODO: extract only admin 2
    if source == "cod":
        df_adm2 = gpd.read_file(f'zip://{input_filename}')
        schema_mapping = {
            'admin2Name_en': 'name_en'
        }
    elif source == "gadm":
        df_adm2 = gpd.read_file(f'zip://{input_filename}!{GADM_FILENAME.format(ISO3=config["constants"]["ISO3"])}',
                                layer=GADM_LAYER.format(ISO3=config['constants']['ISO3']))
        schema_mapping = {
            'NAME_2': 'name_en'
        }
    # Change CRS
    df_adm2 = df_adm2.to_crs(config['constants']['crs'])
    # Modify the column names to suit the schema
    df_adm2 = df_adm2.rename(columns=schema_mapping)
    # Make columns needed for validation
    df_adm2['geometry_type'] = df_adm2['geometry'].apply(lambda x: x.geom_type)
    df_adm2['crs'] = df_adm2.crs
    # Validate
    validate(instance=df_adm2.to_dict('list'), schema=parse_yaml(schema_filename))
    # Write to output
    df_adm2.to_file(output_filename)
