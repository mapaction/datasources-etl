# Admin Line work
# Take lowest level of line and turn all in lines.
# Include boundary / don't include the boundary.
# 
# Create internal boundaries for all admin levels for a supplier
# ie. GADM

import sys
import os
import re
import argparse
import geopandas as gpd
import pandas as pd
import numpy as np
import shapely
from shapely import ops
from jsonschema import validate
from utils.yaml_api import parse_yaml
 
# Input Directory, Schema, Supplier
# Will need to be able to pass parameters at Snakemake for supplier - this
# won't be added to setup or snakefile.
# No idea how this set up enables passing of user defined parameters at the
# commant prompt. Argparse in function.
def adm_to_line_handler():
    adm_to_line(sys.argv[1], sys.argv[2], sys.argv[3])

##
#
def get_files(dirPath, fileExt):
    fList = []
    for file in os.listdir(dirPath):
        if file.endswith(fileExt):
            fList.append(os.path.join(dirPath, file))
    return fList

##
# Create a column called "borders" that contains a dictionay of 
# intersections, where the keys are the names of the intersecting regions,
# and the values are the line geometry of the intersection.
def check_borders(x, df_borders, border_name):
    result = {y[border_name]: x['geometry'].intersection(y['geometry'])
        # checking intersection of first region against all remaining
        for _, y in df_borders.iloc[x.name+1:].iterrows()      
            # Intersects help - tolerance issue.
            # https://geopandas.org/reference.html
            if x['geometry'].intersects(y['geometry'])
        }                
    return result

##
# Create a column called "new_rows" by converting each row of the "borders"
# column to a geodataframe
def make_new_rows(x):
    result = gpd.GeoDataFrame(
        {'name_1_en': x['name_en'], # Assumes 'name_en' in the source data
         'name_2_en': list(x['borders'].keys()),
         'geometry': list(x['borders'].values())
        }
    )
    return result

## 
#
def adm_to_line(inputDir: str, schemaFile: str, supplier: str):
    #config = parse_yaml(r'J:\git\datasources-etl\config.yml')
    config = parse_yaml('config.yml') # relative to the root path, where
                                      # snakemake is.

    # Ensure user knows to pass 'supplier' param
    if supplier is None:
        print('Please provide Supplier param')
        print("snakemake transform_internal_boundaries --config supplier='<supplier> --cores 1'")
        sys.exit(0)
    else:
        print(f'Processing {supplier} admin boundaries for internal dividing lines.')

    print('! NOTE. There are currently known issues with this process.')
    print('! Please check the output manually for consistency.')
    print('! More details are in this wiki page:')
    print('! https://wiki.mapaction.org/display/orgdev/Boundaries')
    print('! See Section: Internal Boundaries')
    print('\n')

    # capture all relevant admin files
    files = get_files(inputDir, '.shp')
    admShps = []
    for fName in files:
        if re.match(
                rf".*{config['constants']['ISO3']}_admn_ad[1-9]_py_s0_{supplier}_pp.shp$",
                fName, re.I):
            admShps.append(fName)

    for inputFile in admShps:
        outputFile = inputFile.replace('_py_s0_','_ln_s0_')
        df_adm = gpd.read_file(inputFile, encoding='utf-8')
        df_borders = df_adm.copy()
        # Note. The following could be within lamdba values. Unpacking into 
        # separate function if further refinement of the changes are necessary.
        df_borders['borders'] = df_borders.apply(
                check_borders,df_borders=df_borders,border_name='name_en',axis=1)
        df_borders['new_rows'] = df_borders.apply(make_new_rows, axis=1)
        # Combine the rows from each new_rows column into a new dataframe
        # Assumes the following simple data schema.
        # 'name_en_1','name_en_2' These reflect the names of the admin areas on
        # either side of the line processed.
        df_new = gpd.GeoDataFrame(columns=['name_1_en', 'name_2_en', 'geometry'])
        for _, row in df_borders.iterrows():
            df_new = df_new.append(row['new_rows'], ignore_index=True)
        
        # Update local names - assumes source schema includes appropriate 
        # colums. name_1_local
        df_new = pd.merge(
                df_new, df_adm[['name_en', 'name_local']], 
                left_on='name_1_en', right_on='name_en', how='inner')
        df_new.rename(columns={'name_local': 'name_1_loc'}, inplace=True)
        df_new.drop(['name_en'], axis=1, inplace=True)
        # name_2_local
        df_new = pd.merge(
                df_new, df_adm[['name_en', 'name_local']],
                left_on='name_2_en', right_on='name_en', how='inner')
        df_new.rename(columns={'name_local': 'name_2_loc'}, inplace=True)
        df_new.drop(['name_en'], axis=1, inplace=True)

        # NOTE. The process below can result in errors. This may be due to the
        # order in which a MultiLineString is defined. Checking for errors
        # (ie. Using ArcGIS Desktop - Check / Repair Geometry)

        # Convert MultiLineString to just LineStrings
        # Issues where MultiLineString is not converted - as is the case with
        # YEM GADM files:
        # https://gis.stackexchange.com/questions/223447/weld-individual-line-segments-into-one-linestring-using-shapely
        df_new['geometry'] = df_new['geometry'].apply(
            lambda x: ops.linemerge(x)
            if x.geom_type == 'MultiLineString' 
            else x)
       
        # Second pass as ops.linemerge(x) can fail
        # https://gis.stackexchange.com/questions/223447/weld-individual-line-segments-into-one-linestring-using-shapely
        # Assumptions are that the line strings are generally correct.
        df_new['geometry'] = df_new['geometry'].apply(
            lambda x: shapely.geometry.LineString(
                [i for sublist in [list(i.coords) for i in x] for i in sublist])
            if x.geom_type == 'MultiLineString' 
            else x)

        # Check the geom_types here. If anything other than MultiLineString
        # then drop.
        geomTypesL = list(df_new['geometry'].geom_type.unique())
        geomTypesL.remove('LineString')
        for nonLS in geomTypesL:
            df_new.drop(df_new[df_new['geometry'].geom_type == nonLS].index, inplace=True)

        # Define projection to be the same as the source - which should be
        # specified in the config.yml file. 
        df_new.crs = df_borders.crs
        # Make additional columns needed for validation
        df_new['geometry_type'] = df_new['geometry'].apply(lambda x: x.geom_type)
        # Validate
        try:
            validate(instance=df_new.to_dict('list'), schema=parse_yaml(schemaFile))
        except Exception as err:
            print(err)
        else:
            # Write to output
            df_new.to_file(outputFile, encoding='utf-8')
    print("Done.")


##
# For test purposes outside Snakemake. Ensure is run from the directory
# containing config.xml and the input/output Files are relevant to local
# sources.
if __name__ == '__main__':
    inputDir = r'J:\git\datasources-etl\processed_data'
    schemaFile = r'J:\git\datasources-etl\schemas\admin_internal_boundaries_ln.yml'
    supplier = r'gadm'
    adm_to_line(inputDir, schemaFile, supplier)
    print('End.')
