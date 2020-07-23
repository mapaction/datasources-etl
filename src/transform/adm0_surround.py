#############################################################################
# Process Surrounding Countries from AOI boundary dataset, where possible.
#############################################################################
import sys
import os
import datetime
import zipfile
import shutil
from jsonschema import validate
import fiona
import geopandas as gpd
import pandas as pd

from utils.yaml_api import parse_yaml 
from transform import gadm_gpkg_processing


##
#
def get_neighbours_generic(gdf_source, gdf_aoi, uid):
    bbox = gdf_aoi.bounds
    minx = bbox.minx.iloc[0]
    maxx = bbox.maxx.iloc[0]
    miny = bbox.miny.iloc[0]
    maxy = bbox.maxy.iloc[0]
    # Ropey way to scale the WGS84 bounding box by a factor... 
    # Should probably map these to see what the distortion ends up as.
    factor = 0.1    # does this mean 10% ???
    pcLon = abs(minx-maxx) / 360    # Total degrees X axis
    lonDistScaled = 360 * ((pcLon * factor) + pcLon) 
    pcLat = abs(miny-maxy) / 180    # Total degrees Y axis
    latDistScaled = 180 * ((pcLat * factor) + pcLat)
    # Use the centroid to extend out to scaled bbox
    centX = minx + abs(minx-maxx)/2
    centY = miny + abs(miny-maxy)/2
    minxScale = centX - (lonDistScaled / 2)
    maxxScale = centX + (lonDistScaled / 2)
    minyScale = centY - (latDistScaled / 2)
    maxyScale = centY + (latDistScaled / 2)
    # Use CX method to query by scaled bounding box coords
    print('Checking neighbour countries.')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    gdf_n_check = gdf_source.cx[minxScale:maxxScale, minyScale:maxyScale] 
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # Note the country list will also include the original country of
    # interest.
    return gdf_n_check[uid].unique().tolist()



##
#
# Include the Transform functions for GeoBoundaries Surround here.
# Principles will be the same. Get a World Dataset, pass an ISO code, 
# query for surrounding intersects. Process all intersects.
def transform_geoboundaries():
    config = parse_yaml('config.yml')
    rawdir = os.path.join(config['dirs']['raw_data'],
                          config['geoboundaries']['subfolder'])
    iso = config['constants']['ISO3']
    isofield = config['geoboundaries']['isofield']
    schema_filename =  os.path.join(
            config['dirs']['schemas'], config['surrounding']['schema'])
    output_filename = os.path.join(
            config['dirs']['processed_data'], 
            config['surrounding']['geoboundaries']['processed'])
    dfs = []
    for root, dirs, files in os.walk(rawdir):
        for fileName in files:
            if fileName.endswith(".zip"):
                # Unzip
                forUnzip, ext = os.path.splitext(fileName)
                source = os.path.join(root, fileName)
                print(f'Processing {source}')
                try:
                    geobndzip = zipfile.ZipFile(source, 'r')
                except Exception as err:
                    print(err)
                    continue
                unzipped = os.path.join(root, forUnzip)
                geobndzip.extractall(unzipped)
                # Capture GeoJson
                for fName in os.listdir(unzipped):
                    if fName.endswith(".geojson"):
                        df = gpd.read_file(os.path.join(unzipped,fName))
                        dfs.append(df)
                # Delete dir
                shutil.rmtree(unzipped)    
    # Merge into single total GeoBoundaries ADM0 dataset
    gdf_source = gpd.GeoDataFrame(pd.concat(dfs, ignore_index=True))
    # get AOI from this dataset
    gdf_aoi = gdf_source.loc[gdf_source[isofield] == iso]
    # Check + concat + process neighbours
    neighbours = get_neighbours_generic(gdf_source, gdf_aoi, isofield)
    dfs_ngb = []
    for ngb in neighbours:
        dfs_ngb.append(gdf_source.loc[gdf_source[isofield] == ngb])
    gdf_ngb = gpd.GeoDataFrame(pd.concat(dfs_ngb, ignore_index=True))
    # Redefine definition
    gdf_ngb.crs = {'init': 'epsg:4326'}
    # Reproject
    gdf_ngb = gdf_ngb.to_crs(config['constants']['crs'])
    # Apply schema 
    gdf_ngb = gdf_ngb.rename(columns={'shapeName':'name_en'}) 
    # Make columns needed for validation
    gdf_ngb['geometry_type'] = gdf_ngb['geometry'].apply(lambda x: x.geom_type)
    gdf_ngb['crs'] = gdf_ngb.crs
    validate(
        instance=gdf_ngb.to_dict('list'),schema=parse_yaml(schema_filename))
    gdf_ngb.to_file(output_filename)


##
# Transform GADM.
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


if __name__ == '__main__':
    #transform_geoboundaries()
    pass
