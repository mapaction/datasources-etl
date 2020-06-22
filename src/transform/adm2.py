import sys
<<<<<<< HEAD

import geopandas as gpd
=======
import os
import zipfile
import geopandas as gpd
import fiona
>>>>>>> master
from jsonschema import validate

from utils.yaml_api import parse_yaml

GADM_FILENAME = 'gadm36_{ISO3}.gpkg'
GADM_LAYER = 'gadm36_{ISO3}_2'


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2], sys.argv[3])


def transform_gadm():
    transform('gadm', sys.argv[1], sys.argv[2], sys.argv[3])


<<<<<<< HEAD
def transform(source: str, input_filename: str, schema_filename: str, output_filename: str):
=======
def transform_geoboundaries():
    transform('geoboundaries', sys.argv[1], sys.argv[2], sys.argv[3])


def transform(source: str, input_filename: str, schema_filename: str,
        output_filename: str):
>>>>>>> master
    """
    :param source: "cod" or "gadm"
    """
    config = parse_yaml('config.yml')
<<<<<<< HEAD
    if source == "cod":
        df_adm0 = gpd.read_file(f'zip://{input_filename}')
=======

    if source == "cod":
        layerlist = fiona.listlayers(f'zip://{input_filename}')
        search = 'adm2'
        for sublist in layerlist:
            if search in sublist:
                with fiona.open(f'zip://{input_filename}', layer=sublist) as layer:
                    for feature in layer:
                        if feature['geometry']['type'] == 'MultiPolygon':
                            # print(feature['geometry']['type'],sublist)
                            adm2 = sublist
        # print(adm2)

        index = layerlist.index(adm2)
        adm2_name = layerlist[index]

        df_adm2 = gpd.read_file(f'zip://{input_filename}', layer=adm2_name)
>>>>>>> master
        schema_mapping = {
            'admin2Name_en': 'name_en'
        }
    elif source == "gadm":
<<<<<<< HEAD
        df_adm0 = gpd.read_file(f'zip://{input_filename}!{GADM_FILENAME.format(ISO3=config["constants"]["ISO3"])}',
=======
        df_adm2 = gpd.read_file(f'zip://{input_filename}!{GADM_FILENAME.format(ISO3=config["constants"]["ISO3"])}',
>>>>>>> master
                                layer=GADM_LAYER.format(ISO3=config['constants']['ISO3']))
        schema_mapping = {
            'NAME_2': 'name_en'
        }
<<<<<<< HEAD
    # Change CRS
    df_adm0 = df_adm0.to_crs(config['constants']['crs'])
    # Modify the column names to suit the schema
    df_adm0 = df_adm0.rename(columns=schema_mapping)
    # Make columns needed for validation
    df_adm0['geometry_type'] = df_adm0['geometry'].apply(lambda x: x.geom_type)
    df_adm0['crs'] = df_adm0.crs
    # Validate
    validate(instance=df_adm0.to_dict('list'), schema=parse_yaml(schema_filename))
    # Write to output
    df_adm0.to_file(output_filename)
=======
    elif source == "geoboundaries":
        rawdir = config['dirs']['raw_data']
        source_geob = os.path.join(rawdir, config['geoboundaries']['adm2']['raw'])
        unzipped, ext = os.path.splitext(source_geob)
        # Unzip
        geobndzip = zipfile.ZipFile(source_geob, 'r')
        geobndzip.extractall(unzipped)
        geobndzip.close()
        # Find geojson
        geojson = []
        for root, dirs, files in os.walk(unzipped):
            for filename in files:
                if filename.endswith(".geojson"):
                    geojson.append(os.path.join(root, filename))
        if len(geojson) > 1:
            print('Found more than one geojson file in {0}'.format(zippedshpdir))
        elif len(geojson) == 0:
            print('Found no geojson files in {0}'.format(zippedshpdir))
        else:
            df_adm2 = gpd.read_file(geojson[0])
        schema_mapping = {'shapeName': 'name_en'}    
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
>>>>>>> master
