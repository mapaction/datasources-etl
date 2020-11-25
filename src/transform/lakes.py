import sys

import geopandas as gpd
from jsonschema import validate

from sqlalchemy.dialects.postgresql import HSTORE

from utils.yaml_api import parse_yaml


def transform_osm():
    transform('osm', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "osm" or ..
    """
    print(source, input_filename, schema_filename, output_filename)
    config = parse_yaml('config.yml')

    if source == "osm":

        df = gpd.read_file(input_filename)

        schema_mapping = {
            'name:en': 'name_en',
            'name': 'name_loc',
            'highway': 'fclass'
            }
        # GDAL converts OSM to GPKG, tags are written as hstore key-value in attribute 'other_tags'
        # method to convert hstore string to dictionary from SqlAlchemy
        hstore = HSTORE.result_processor(None, None, 'string')
        df['other_tags']=df['other_tags'].apply(hstore)

        for key, value in schema_mapping.items():
            # temp dictionary for pandas rename method. Don't use original dict as want to see whether
            # each input attribute is present.
            temp_schema_dict = {key: value}
            try:
                # rename column if exists.
                df = df.rename(columns=temp_schema_dict, errors="raise")
            except:
                # as error raised, input attribute is not present.
                # now make sure output attribute is NOT present.  If not pull from 'other_tags'
                if value not in df.columns:
                    df[value] = df['other_tags'].apply(lambda x: x.get(key) if type(x) == dict else x)

        # now remove columns which aren't in schema:
        schema_to_keep = list(schema_mapping.values())
        # add geometry to schema
        schema_to_keep.append('geometry')
        df = df.filter(schema_to_keep)

    # Change CRS
    df = df.to_crs(config['constants']['crs'])
    # Make columns needed for validation
    ### df_roads['geometry_type'] = df_roads['geometry'].apply(lambda x: x.geom_type)
    ### df_roads['crs'] = df_roads.crs
    # Validate
    ### validate(instance=df_roads.to_dict('list'), schema=parse_yaml(schema_filename))
    # Write to output
    df.to_file(output_filename)
