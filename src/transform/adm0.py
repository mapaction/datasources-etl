import sys

import geopandas as gpd
from jsonschema import validate

from utils.yaml_api import parse_yaml
from utils.geoprocessing import poly_to_line


GADM_FILENAME = 'gadm36_{ISO3}.gpkg'
GADM_LAYER = 'gadm36_{ISO3}_0'


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


def transform_gadm():
    transform('gadm', sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str, boundaries_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    config = parse_yaml('config.yml')
    if source == "cod":
        df_adm0 = gpd.read_file(f'zip://{input_filename}')
        schema_mapping = {
            'admin0Name_en': 'name_en'
        }
    elif source == "gadm":
        df_adm0 = gpd.read_file(f'zip://{input_filename}!{GADM_FILENAME.format(ISO3=config["constants"]["ISO3"])}',
                                layer=GADM_LAYER.format(ISO3=config['constants']['ISO3']))
        schema_mapping = {
            'NAME_0': 'name_en'
        }
    # Change CRS
    df_adm0 = df_adm0.to_crs(config['constants']['crs'])
    # Modify the column names to suit the schema
    df_adm0 = df_adm0.rename(columns=schema_mapping)
    # Make columns needed for validation
    df_adm0['geometry_type'] = df_adm0['geometry'].apply(lambda x: x.geom_type)
    df_adm0['crs'] = df_adm0.crs
    # Validate
    validate(instance=df_adm0.to_dict('list'), schema=parse_yaml(schema_filename))
    # Write to outputs
    df_adm0.to_file(output_filename)
    # Boundaries - boundaries file should match schema of original file with geometry converted to line
    # added to transform function as these outputs should be synchronised wherever possible.
    df_adm0_boundaries = poly_to_line(df_adm0)
    # Make geometry column needed for validation
    df_adm0_boundaries['geometry_type'] = df_adm0_boundaries['geometry'].apply(lambda x: x.geom_type)
    # Write to outputs
    df_adm0_boundaries.to_file(boundaries_filename)
