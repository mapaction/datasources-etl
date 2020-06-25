import sys
import geopandas as gpd
from utils.yaml_api import parse_yaml


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    config = parse_yaml('config.yml')

    if source == "cod":
        df_rivers = gpd.read_file(f'zip://{input_filename}')

    # Change CRS
    df_rivers = df_rivers[df_rivers['geometry'].notna()]
    df_rivers = df_rivers.to_crs(config['constants']['crs'])
    # Make columns needed for validation
    df_rivers['geometry_type'] = df_rivers['geometry'].apply(lambda x: x.geom_type)
    df_rivers['crs'] = df_rivers.crs

    # TODO fix validation
    # Validate
    # validate(instance=df_rivers.to_dict('list'), schema=parse_yaml(schema_filename))

    # Write to output
    df_rivers.to_file(output_filename)
