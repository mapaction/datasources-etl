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
import datetime

#from utils.requests_api import download_url

import pdb

##
#
def check_version(held_version, supplier):
    """ Check the source vs held version. Returns True/False if file names
    match """
    print("Checking:\n\t{0}\n\t{1}".format(held_version, supplier))
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
            return False, None
        # Compare
        held_path, held_file = os.path.split(held_version)
        if held_file != dl_file:
            return True, dl_link 
        else:
            return True, None
    else: 
        print('Did not recognise supplier.')
        return False

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
def get_country():
    pass


##
#
def get_surrounding():
    pass


##
#
def main():
    # Assume that the supplier/format/local holding  will be in a config file
    # but for now:
    country_aoi = 'Yemen'
    supplier = r'GADM'
    source_format = r'geopackage'
    ma_holding = r'J:\05_OpenData\GADM\gadm36_gpkg.zip'
    gadm_geopkg = r'J:\05_OpenData\GADM\gadm36_gpkg\gadm36.gpkg'
    aoi_dir = r'J:\05_OpenData\GADM\Yemen'

    # Download new GADM data if the version specified on the site has changed.
    result, url = check_version(ma_holding, supplier)
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
    # Code missing so done manually


    # Get the country from the World Geopackage. 
    print("Reading in World GeoPackage")
    # The below isn't necessary as it doens't look like the world geopackage
    # includes more than one layer, however using fiona looks to be a way to
    # read a geopackage with multiple layers.
    # https://stackoverflow.com/questions/56165069/can-geopandas-get-a-geopackages-or-other-vector-file-all-layers
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
        # Get Yemen
        gdf_aoi_country = gdf.loc[gdf['NAME_0'] == country_aoi] # <<< NAME_0 
        output = os.path.join(aoi_dir, '{0}.gpkg'.format(country_aoi))
        if os.path.exists(output):
            print("\tWarning output file exists: {0}".format(output))
            print("\tDecide what to do... but not overwriting this time")     
        else:
            gdf_aoi_country.to_file(output, driver="GPKG")

        #Test times with Shapely
        #Could read into PostGIS



if __name__ == '__main__':
    main()


