import sys

import geopandas as gpd

from utils.yaml_api import parse_yaml
from utils.osm import convert_osm_to_gpkg
from jsonschema import validate


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3])


def transform_osm():
    transform('osm', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    config = parse_yaml('config.yml')

    if source == "cod":
        df_roads = gpd.read_file(f'zip://{input_filename}')
        # COD data has some NAs
        df_roads = df_roads[df_roads['geometry'].notna()]
        schema_mapping = {'TYPE': 'fclass'}
    elif source == "osm":
        df_roads = convert_osm_to_gpkg(input_filename, 'osm_roads.gpkg', 'lines')
        schema_mapping = {'highway': 'fclass'}
    # Change CRS
    df_roads = df_roads.to_crs(config['constants']['crs'])
    # Rename columns
    df_roads = df_roads.rename(columns=schema_mapping)
    # Make columns needed for validation
    df_roads['geometry_type'] = df_roads['geometry'].apply(lambda x: x.geom_type)
    df_roads['crs'] = df_roads.crs
    # Validate
    validate(instance=df_roads.to_dict('list'), schema=parse_yaml(schema_filename))
    # Write to output
    df_roads.to_file(output_filename)
