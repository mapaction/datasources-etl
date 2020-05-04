#############################################################################
# Process Surrounding Countries for GADM AOI.
#############################################################################

import sys
import os
import fiona
import geopandas as gpd
import logging
import datetime
import pandas as pd
from jsonschema import validate

from utils.yaml_api import parse_yaml 
from utils import gadm_gpkg_processing

import pdb

##
#
def transform():
    config = parse_yaml('config.yml')
    held_gpkg = os.path.join(
            config['dirs']['raw_data'], config['surrounding']['gadm']['raw'])
    country_aoi = config['constants']['ISO3']
    schema_filename = os.path.join(
            config['dirs']['schemas'], config['surrounding']['schema'])
    output_filename = os.path.join(
            config['dirs']['processed_data'], 
            config['surrounding']['gadm']['processed'])
    print(f'Reading {held_gpkg}')
    for layername in fiona.listlayers(held_gpkg):
        print(f'Reading {layername} into Geopandas. Takes about 2 mins...')
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        gdf = gpd.read_file(held_gpkg, layer=layername)
        print(r'Done reading.')
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # Process the country of interest 
    gdf_aoi_levels = gadm_gpkg_processing.get_country_admin_levels(
            gdf, country_aoi)
    # Get neighbours
    neighbours = gadm_gpkg_processing.get_neighbour_countries(
            gdf, gdf_A0=gdf_aoi_levels['a0'])
    # Remove country of interest from neighbours list
    if country_aoi in neighbours: neighbours.remove(country_aoi)
    print(r'Found {0}'.format(','.join(neighbours)))
    # Process all neighbour countries
    A0_list = []
    for neighbour in neighbours:
        gdf_aoi_levels = gadm_gpkg_processing.get_country_admin_levels(
                gdf, neighbour)
        A0_list.append(gdf_aoi_levels['a0'])
    # Concatenate neighbours A0 gemetries into single GeoDataFrame
    gdf_A0_all = gpd.GeoDataFrame(pd.concat(A0_list, ignore_index=True))
    # Redefine definition
    gdf_A0_all.crs = {'init': 'epsg:4326'}
    # Reproject
    gdf_A0_all = gdf_A0_all.to_crs(config['constants']['crs'])
    # Apply schema 
    gdf_A0_all = gdf_A0_all.rename(columns={'NAME_0':'name_en'}) 
    # Make columns needed for validation
    gdf_A0_all['geometry_type'] = gdf_A0_all['geometry'].apply(lambda x: x.geom_type)
    gdf_A0_all['crs'] = gdf_A0_all.crs
    # Validate
    validate(instance=gdf_A0_all.to_dict('list'), schema=parse_yaml(schema_filename))
    # Write to output
    gdf_A0_all.to_file(output_filename)



