# Admin Line work
# Take lowest level of line and turn all in lines.
# Include boundary / don't include the boundary.

import sys
import os
import geopandas as gpd
import numpy as np
from shapely import ops
from jsonschema import validate
from utils.yaml_api import parse_yaml

 
# Note the sys.argv[] values are passed by snakemake?
# Source, Output, Schema
def adm_to_line_handler():
    #print(sys.argv[0])
    #print(sys.argv[1])
    #print(sys.argv[2])
    #print(sys.argv[3])
    adm_to_line(sys.argv[1], sys.argv[3], sys.argv[2])


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
def adm_to_line(inputFile: str, outputFile: str, schemaFile: str):
    #config = parse_yaml(r'J:\git\datasources-etl\config.yml')
    config = parse_yaml('config.yml') # relative to the root path, where
                                      # snakemake is.
    df_adm = gpd.read_file(inputFile)
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
    # Add local names to the defined schema
    df_new['name_1_local'] = np.nan
    df_new['name_2_local'] = np.nan
    # Obtain local admin names (if available)
    # Assume these are in the source data and named as per the schema
    # ie. name_1_local, name_2_local
    if 'name_local' not in df_borders.columns:
        print('Local names not present in source schema.')
    else:
        # Update name_1_local and name_2_local by looking up the name_1_local
        # value against df_borders 
        # Todo
        print('Updating local names.')
        # Todo
    # Convert MultiLineString to just LineStrings
    df_new['geometry'] = df_new['geometry'].apply(
        lambda x: ops.linemerge(x)
        if x.geom_type == 'MultiLineString'
        else x)
    # Define projection to be the same as the source 
    df_new.crs = df_borders.crs
    # Make additional columns needed for validation
    df_new['geometry_type'] = df_new['geometry'].apply(lambda x: x.geom_type)
    # Validate
    validate(instance=df_new.to_dict('list'), schema=parse_yaml(schemaFile))
    # Write to output
    df_new.to_file(outputFile)
    print("Done.")


##
# For test purposes outside Snakemake. Ensure is run from the directory
# containing config.xml and the input/output Files are relevant to local
# sources.
if __name__ == '__main__':
    inputFile =  r'J:\git\datasources-etl\processed_data\older\yem_admn_ad1_py_s0_geobnd_pp.shp'
    outputFile = r'J:\git\datasources-etl\processed_data\older\yem_admn_ad1_ln_s0_geobnd_pp.shp'
    schemaFile = r'J:\git\datasources-etl\schemas\admin1_internal_boundaries_ln.yml'
    adm_to_line(inputFile, outputFile, schemaFile)
    print('End.')
