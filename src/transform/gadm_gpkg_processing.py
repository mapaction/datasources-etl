#############################################################################
# Various functions for checking and processing GADM data in a Geopackage
#############################################################################

import os
import fnmatch
import datetime
import re
import fiona
import geopandas as gpd


##
#
def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

##
# Aggregate lower admin levels for specified country
def get_country_admin_levels(gdf_world, country_aoi):
    print('Checking {0} Admin Levels.'.format(country_aoi))
    return_dict = {}
    #gdf = gdf_world.loc[gdf_world['GID_0'] == country_aoi].copy()
    gdf = gdf_world.loc[gdf_world['GID_0'] == country_aoi].copy()
    # Determine level of admin - check GID_* cols for None values.
    cols = gdf.columns.values.tolist()
    gdf_gid = gdf[fnmatch.filter(cols, 'GID_*')].copy()
    gdf_gid.dropna(axis=1, how='all', inplace=True)
    # Last list element, Last character
    last_populated_gid = gdf_gid.columns.values.tolist()[-1][-1]
    print('\tMax Admin Level {0}'.format(last_populated_gid))
    # Drop all cols after first empty GID_* column.
    drop_cols = []
    for col in cols:
        if is_int(col[-1]) is True and int(col[-1]) > int(last_populated_gid):
            drop_cols.append(col)
    gdf.drop(drop_cols, axis=1, inplace=True)
    # and take out ID_* fields
    gdf.drop(gdf[fnmatch.filter(gdf.columns.values.tolist(), 'ID_*')], 
             axis=1, inplace=True)
    # and take out REMARKS_*
#    gdf.drop(gdf[fnmatch.filter(gdf.columns.values.tolist(), 'REMARKS_*')], 
#             axis=1, inplace=True)
    # and take out VALID*
#    gdf.drop(gdf[fnmatch.filter(gdf.columns.values.tolist(), 'VALID*')], 
#             axis=1, inplace=True)
    # and the UID
    gdf.drop(columns=['UID'], axis=1, inplace=True)
    # anything else is associated with the last avialable admin level if
    # populated.
    gdf.dropna(axis=1, how='all', inplace=True)
    #
    level = 0
    while level < int(last_populated_gid):
        print('\tProcessing Level {0}'.format(level))
        cols_agg = []
        cols_required = []
        for col in gdf.columns.values.tolist():
            if is_int(col[-1]) is True and int(col[-1]) <= level:
                cols_agg.append(col)
        # Include the geometry column 
        cols_required = list(cols_agg)
        cols_required.append('geometry')
        # Dissolve using GID_* only - assume all other fields to use First
        # value. Was dropping features where looking to be specific and
        # groupby more fields (that should all be the same)
        cols_agg = [x for x in cols_agg if 'GID_' in x]
        gdf_dslv = gdf[cols_required].dissolve(by=cols_agg)
        gdf_dslv.reset_index(inplace=True)
        gdf_dslv = gdf_dslv[cols_required]
        print('\tAggregated to {0} features.'.format(len(gdf_dslv)))
        return_dict["a{0}".format(level)] = gdf_dslv 
        # 
        level += 1
    # Include the highest level
    return_dict["a{0}".format(last_populated_gid)] = gdf
    return return_dict
        
    
##
# If gdf is passed only no way to know what the AOI country is.
def get_neighbour_countries(gdf_source, gdf_A0=None, NAME_0=None, GID_0=None):
    print('Extending bounding box.')
    # https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude#19412565
    bbox = gdf_A0.bounds
    minx = bbox.minx[0]
    maxx = bbox.maxx[0]
    miny = bbox.miny[0]
    maxy = bbox.maxy[0]
    # Ropey way to scale the WGS84 bounding box by a factor... 
    # Should probably map these to see what the distortion ends up as.
    factor = 0.1    # does this mean 10% ???
    pcLon = abs(minx-maxx) / 360    # Total degrees X axis
    lonDistScaled = 360 * ((pcLon * factor) + pcLon) 
    pcLat = abs(miny-maxy) / 180    # Total degrees Y axis
    latDistScaled = 180 * ((pcLat * factor) + pcLat)
    # Use the centroid to extend out to scaled bbox
#    centroid = gdf_A0.centroid # Not sure if the centroid is the centre when
                               # compared to the bounding box
#    centX = centroid.x[0]
#    centY = centroid.y[0]
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
    return gdf_n_check['GID_0'].unique().tolist()


##
# Assumes a dictionary {adminLevel: geopandas_dataframe} is passed along with
# output dir etc. 
def write_to_gpkg(gdf_aoi_levels, version, aoi_dir, country_aoi, neigh=None):
    for level, gdf_level in gdf_aoi_levels.items():
        gpkg = '{0}.gpkg'.format(os.path.join(aoi_dir, country_aoi))
        # Will need to make the folder if it's not present so will need write.
        if not os.path.exists(aoi_dir): os.makedirs(aoi_dir)
        if neigh: 
            layer = 'gadm{0}_{1}_{2}'.format(version, neigh, level)
        else:
            layer = 'gadm{0}_{1}_{2}'.format(version, country_aoi, level)
        gdf_level.to_file(gpkg, layer=layer, driver="GPKG")
        print('Writing {0} to {1}'.format(layer, gpkg))
