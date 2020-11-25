import sys
import geopandas as gpd
from utils.yaml_api import parse_yaml
from jsonschema import validate


def transform_osm():
    transform('osm', sys.argv[1], sys.argv[2], sys.argv[3])


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm" or "osm"
    """
    config = parse_yaml('config.yml')

    if source == "osm":

        df = gpd.read_file(input_filename)

        schema_mapping = {
            'name:en': 'name_en',
            'name': 'name_loc',
            'waterway': 'fclass'
        }
        # GDAL converts OSM to GPKG, tags are written as hstore key-value in attribute 'other_tags'
        # method to convert hstore string to dictionary from SqlAlchemy
        hstore = HSTORE.result_processor(None, None, 'string')
        df['other_tags'] = df['other_tags'].apply(hstore)

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


    if source == "cod":
        df = gpd.read_file(f'zip://{input_filename}')

    # Change CRS
    df = df[df['geometry'].notna()]
    df = df.to_crs(config['constants']['crs'])
    # Make columns needed for validation
    ### df['geometry_type'] = df['geometry'].apply(lambda x: x.geom_type)
    ### df['crs'] = df.crs
    # Validate
    #### validate(instance=df.to_dict('list'), schema=parse_yaml(schema_filename))

    # Write to output
    df.to_file(output_filename)
