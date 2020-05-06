import os
import re
import requests
from requests.compat import urljoin
from bs4 import BeautifulSoup

from utils.yaml_api import parse_yaml
from utils.requests_api import download_url

##
# While this works it hasn't yet been implemented with snakemake.
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
def get_world():
    config = parse_yaml('config.yml')
    rawdir = config['dirs']['raw_data']
    outputZip = config['surrounding']['gadm']['rawzip']
    sourceURL = config['surrounding']['gadm']['url']
    source_gadm_world = os.path.join(rawdir, outputZip)
    print(r'Downloading {0} to {1}'.format(sourceURL, source_gadm_world))
    download_url(sourceURL, source_gadm_world)
    

