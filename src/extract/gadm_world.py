#############################################################################
# Check and download the GADM world geopackage and extract a country.
# Does not use a config file, though the expectation is that there would be
# one available. Hard-coded vales are set at the start of main()
# Incomplete in the sense that surrounding countries (based on the country of
# interest are not automatically downloaded - this is on a todo list)
# Also need to write an unzipper - assuming there will be a specific location
# to save the data.
#############################################################################

import os
import requests
from requests.compat import urljoin
from bs4 import BeautifulSoup
import re
import fiona
import geopandas as gpd
import fnmatch
import datetime

#from utils.requests_api import download_url

import pdb

##
#
def check_version(held_version, supplier):
    """ Check the source vs held version. Returns True/False if file names
    match """
    print("Checking supplier holding:\n\t{0}\n\t{1}".format(supplier,
        held_version))
    # In the case of GADM need to parse the following data 'home-page' for a
    # version.
    # Assume that this function knows how to check each supplier source to
    # obtain a comparable version. In that sense this function will behave
    # differently depending on what supplier is being checked.
    # In this case also assumes that the format to be checked is a geopackage
    if supplier == 'GADM':
        gdal_home = r''
        # Check data home-page for latest version and download link:
        download_page_html = r'https://gadm.org/download_world.html' 
        page = requests.get(download_page_html)
        soup = BeautifulSoup(page.text, 'html.parser')
        h4_list = soup.find_all("h4")
        if len(h4_list) > 1:
            # At the time of processing there was only one h4 tag in the html
            print('Page format may have changed.')
        version = h4_list[0].text.strip()
        if 'Current version' not in version:
            print('Warning. Could not verify h4 expected to contain version details')
            print("Found: '{0}'".format(version))
        # Search for expected download link
        version = re.sub(r'[^\d]+', '', version)
        expected_df = "gadm{0}_gpkg.zip".format(version)
        a_list = soup.find_all("a")
        dl_link = None
        for a in a_list:
            path, dl_file = os.path.split(a.attrs['href'])
            if dl_file == expected_df:
                dl_link = urljoin("{0}/".format(path), dl_file)
                print("Found download link:\n\t{0}".format(dl_link))
                break
        if not dl_link: 
            print("Did not find expected download link")
            return False, None, version
        # Compare
        held_path, held_file = os.path.split(held_version)
        if held_file != dl_file:
            return True, dl_link, version 
        else:
            return True, None, version
    else:
        print('Did not recognise supplier.')
        return False, None, None

##
#
def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
    #logger.info(f'Downloaded "{url}" to "{save_path}"')
    print('Downloaded {0} to {1}'.format(url, save_path))


##
#
def unzip_geopkg(source_zip):
    pass


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
    gdf = gdf_world.loc[gdf_world['NAME_0'] == country_aoi].copy()
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
    print('Checking neighbour countries.')
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
    print('Looking for neighbours')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    gdf_n_check = gdf_source.cx[minxScale:maxxScale, minyScale:maxyScale] 
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # 
#    gdf_n_check.remove(<country_aoi>)
    return gdf_n_check['NAME_0'].unique().tolist()


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

##
#
def main():
    # Assume that the supplier/format/local holding  will be in a config file
    # but for now:
#    country_aoi = 'Yemen'
    country_aoi = 'Oman'
    supplier = r'GADM'
    source_format = r'geopackage'
    ma_holding = r'J:\05_OpenData\GADM\gadm36_gpkg.zip'
    gadm_geopkg = r'J:\05_OpenData\GADM\gadm36_gpkg\gadm36.gpkg'
    aoi_dir = r'J:\05_OpenData\GADM\{0}'.format(country_aoi)

    # Download new GADM data if the version specified on the site has changed.
    result, url, version = check_version(ma_holding, supplier)
    if result is True and url:
        msg = 'Completed checks. Source version found not the same as ' \
'source version held.'
        print(msg)
        print(url)
        # Downloading found link
        # Create new download path - config file?
        print('Preparing new download path for source...')
        dl_path, dl_file = os.path.split(ma_holding)
        source_path, source_file = os.path.split(url)
        new_holding = os.path.join(dl_path, source_file)
        print("\t{0}".format(new_holding))
        if os.path.exists(new_holding):
            msg = "Found existing holding which appears to be the same as " \
"source version due to be downloaded. Is the config file up to date?"
            print(msg)
        download_url(url, new_holding) 
    elif result is True and not url:
        print('Current held version is the same as current source version.')
    elif result is False:
        print('Unable to complete check.')

    # Do the unzip here
    # Code not done yet so done manually

    # Get the country from the World Geopackage. 
    print("Reading in World GeoPackage")
    for layername in fiona.listlayers(gadm_geopkg):
        #with fiona.open(gadm_geopkg, layer=layername) as src:
        #    print(layername, len(src))
        #    for feature in src:
        #        print(feature['geometry'])
        print('Reading into geopandas') # Takes about 3-5 min?
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        gdf = gpd.read_file(gadm_geopkg, layer=layername) 
        print('Done reading')
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # Get Country - the GADM files include lowest level admin only
        gdf_aoi_levels = get_country_admin_levels(gdf, country_aoi)
        # Add gdf as layers to the same geopackage.
        # gdf_aoi_levels, version, aoi_dir, country_aoi
        write_to_gpkg(gdf_aoi_levels, version, aoi_dir, country_aoi)
        # Extract Surrounding countries 
        neighbours = get_neighbour_countries(gdf, gdf_A0=gdf_aoi_levels['a0'])
        if country_aoi in neighbours: neighbours.remove(country_aoi)
        print('Found neighbours {0}'.format(','.join(neighbours)))
        # Process each surrounding country
        for neighbour in neighbours:
            gdf_aoi_levels = get_country_admin_levels(gdf, neighbour)
            # Write to different geopackage
#            write_to_gpkg(gdf_aoi_levels, version, aoi_dir, neighbour)
            # Can add to the same geopackage
            write_to_gpkg(gdf_aoi_levels, version, aoi_dir,
                    country_aoi, neigh=neighbour)

    print('Done.')


if __name__ == '__main__':
    main()


