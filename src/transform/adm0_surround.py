#############################################################################
# Process Surrounding Countries for GADM AOI.
#############################################################################

import sys
import os
import datetime
import zipfile
from jsonschema import validate
import fiona
import geopandas as gpd
import pandas as pd

from utils.yaml_api import parse_yaml 
from transform import gadm_gpkg_processing


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
    # Unzip - as reading zipped world geopackage takes too long
    rawdir = config['dirs']['raw_data']
    zipgpkg = config['surrounding']['gadm']['rawzip']
    source_gadm_world = os.path.join(rawdir, zipgpkg)
    print(r'Unzipping {0} to {1}'.format(source_gadm_world, held_gpkg))
    gadmzip = zipfile.ZipFile(source_gadm_world, 'r')
    gadmzip.extractall(rawdir)
    gadmzip.close()
    # Check unzip was ok?
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
    # Remove country of interest from neighbours list if required.
    #if country_aoi in neighbours: neighbours.remove(country_aoi)
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



