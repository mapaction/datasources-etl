# Recursively process a GADM Country Admin level.

import os
import sys
import fnmatch
import geopandas as gpd
import fiona
from jsonschema import validate
from utils.yaml_api import parse_yaml

##
#
def transform_gadm():
    transform_gadm_all(sys.argv[1], sys.argv[2], sys.argv[3]) 

##
# Get number of all GADM admin levels from a country download.
def get_gadm_adm_levels(gdf):
    cols = gdf.columns.values.tolist()
    gdf_gid = gdf[fnmatch.filter(cols, 'GID_*')].copy()
    gdf_gid.dropna(axis=1, how='all', inplace=True)
    # Last list element, Last character
    last_populated_gid = gdf_gid.columns.values.tolist()[-1][-1]
    print('\tMax Admin Level {0}'.format(last_populated_gid))
    return last_populated_gid

##
#
def transform_gadm_all(input_filename: str, schema_filename: str,
        output_dir: str):

    # Where running as Snakemake ensure it's in from the dir containing file
    #config = parse_yaml('config.yml')
    config = parse_yaml('J:\git\datasources-etl\config.yml')
    GADM_FILENAME = 'gadm36_{ISO3}.gpkg'
    GADM_LAYER = 'gadm36_{ISO3}_{LVL}'
    iso = config['constants']['ISO3']

    # Can also read from a zip file. Saves unzipping the source.
    #gdf_aoi = gpd.read_file(input_filename)
    gdf_aoi = gpd.read_file(f'zip://{input_filename}!{GADM_FILENAME.format(ISO3=iso)}')
    adm_levels = get_gadm_adm_levels(gdf_aoi)

    # Process each levl. +1 as starts at 0.
    for lvl in range(0, int(adm_levels)+1):
        print(lvl)
        gdf_lvl = gpd.read_file(
            f'zip://{input_filename}!{GADM_FILENAME.format(ISO3=iso)}',
            layer=GADM_LAYER.format(ISO3=iso, LVL=lvl))

        # Define schemas for validation - check to see whether the valitation
        # for adm0 works for adm1. ie. Define full schema (level0 has less)
        # and see if level0 passes schema for level1. 
        if lvl == 0:
            schema_mapping = {
                'NAME_0': 'name_en',
                'GID_0': 'pcode'
            }
        else:
            schema_mapping = {
                'NAME_{}'.format(lvl): 'name_en',
                'GID_{}'.format(lvl): 'pcode',
                'GID_{}'.format(lvl-1): 'par_pcode'
            }
        # Change CRS
        gdf_lvl = gdf_lvl.to_crs(config['constants']['crs'])
        # Modify the column names to suit the schema
        gdf_lvl = gdf_lvl.rename(columns=schema_mapping)
        # Make columns needed for validation
        gdf_lvl['geometry_type'] = gdf_lvl['geometry'].apply(lambda x: x.geom_type)
        gdf_lvl['crs'] = gdf_lvl.crs
        # Validate
        validate(instance=gdf_lvl.to_dict('list'), schema=parse_yaml(schema_filename))
        # Write to output
        output_filename = os.path.join(
                output_dir,
                '{0}_admn_ad{1}_py_s0_gadm_pp.shp'.format(iso.lower(), lvl)) 
        gdf_lvl.to_file(output_filename)


##
#
if __name__ == '__main__':
    #source = r'J:/git/datasources-etl/raw_data/MMR_GADM_ADM/gadm36_MMR.gpkg'
    source = r'J:/git/datasources-etl/raw_data/MMR_GADM_ADM.zip'
    schema = r'J:\git\datasources-etl\schemas\gadm_admin_py.yml'
    output_dir = r'J:\git\datasources-etl\processed_data'
    transform_gadm_all(source, schema, output_dir)

