import sys
import geopandas as gpd
from utils.yaml_api import parse_yaml
from jsonschema import validate
from sqlalchemy.dialects.postgresql import HSTORE

def hstore2dict(str):
    """ Return a python dictionary from a HSTORE data type.
    This data is used by GDAL to store the key-value pairs
    from the OSM XML into a single string attribute"""
    hstore = HSTORE.result_processor(None,None,'string')
    return hstore(str)


def transform_osm():
    transform('osm', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    config = parse_yaml('config.yml')

    if source == "osm":
        df_airports = gpd.read_file(input_filename)


        # Example schema mapping
        """
        schema_mapping = {
            'NAME_1': 'name_en',
            'GID_1': 'pcode',
            'GID_0': 'par_pcode'
        }
        """

        # Example rename columns
        # df_adm1 = df_adm1.rename(columns=schema_mapping)

    # Change CRS
    df_airports = df_airports[df_airports['geometry'].notna()]
    df_airports = df_airports.to_crs(config['constants']['crs'])
    # Make columns needed for validation
    df_airports['geometry_type'] = df_airports['geometry'].apply(lambda x: x.geom_type)
    df_airports['crs'] = df_airports.crs

    # Validate
    validate(instance=df_airports.to_dict('list'), schema=parse_yaml(schema_filename))

    # Write to output
    df_seaports.to_file(output_filename)
