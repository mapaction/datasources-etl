import sys

import geopandas as gpd
from jsonschema import validate

from utils.yaml_api import parse_yaml

CRS = 'EPSG:2090'
GADM_YEMEN_FILENAME = 'gadm36_YEM.gpkg'
GADM_LAYER = 'gadm36_YEM_0'


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3])


def transform_gadm():
    transform('gadm', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    if source == "cod":
        df_adm0 = gpd.read_file(f'zip://{input_filename}')
        schema_mapping = {
            'admin10Name': 'name_en'
        }
    elif source == "gadm":
        df_adm0 = gpd.read_file(f'zip://{input_filename}!{GADM_YEMEN_FILENAME}', layer=GADM_LAYER)
        schema_mapping = {
            'NAME_0': 'name_en'
        }
    # Change CRS
    df_adm0 = df_adm0.to_crs(CRS)
    # Modify the column names to suit the schema
    df_adm0 = df_adm0.rename(columns=schema_mapping)
    # Make columns needed for validation
    df_adm0['geometry_type'] = df_adm0['geometry'].apply(lambda x: x.geom_type)
    df_adm0['crs'] = df_adm0.crs
    # Validate
    validate(instance=df_adm0.to_dict('list'), schema=parse_yaml(schema_filename))
    # Write to output
    df_adm0.to_file(output_filename)
