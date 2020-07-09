import sys
import geopandas as gpd
from utils.yaml_api import parse_yaml
from jsonschema import validate


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    config = parse_yaml('config.yml')

    if source == "cod":
        df_seaports = gpd.read_file(f'zip://{input_filename}')

    # Change CRS
    df_seaports = df_seaports[df_seaports['geometry'].notna()]
    df_seaports = df_seaports.to_crs(config['constants']['crs'])
    # Make columns needed for validation
    df_seaports['geometry_type'] = df_seaports['geometry'].apply(lambda x: x.geom_type)
    df_seaports['crs'] = df_seaports.crs

    # Validate
    validate(instance=df_seaports.to_dict('list'), schema=parse_yaml(schema_filename))

    # Write to output
    df_seaports.to_file(output_filename)
