import os
import json
import datetime

import pandas as pd

from utils.yaml_api import parse_yaml
from utils.requests_api import get_json 
from utils.requests_api import download_url 
from transform.adm0 import transform

##
# Process a specific country dataset.
# Get a specific Admin level of get all levels (default) 
# https://www.geoboundaries.org/#dataTable
def get_geoboundaries_adm(admLevel=None):
    config = parse_yaml('config.yml')
    rooturl = config['geoboundaries']['url']
    iso = config['constants']['ISO3']
    typ = config['geoboundaries']['typ']
    # Get Levels
    url = "{0}?ISO={1}&{2}".format(rooturl, iso, typ)
    knownlevels = len(get_json(url))
    # Process Data
    if admLevel is not None: url = r"{0}&ADM={1}".format(url, admLevel)
    # We want all available admin boundaries so skip specifying which AMD to
    # process. Otherwise include a specific ADM level to process.
    geob_api_response = get_json(url)
    # Check whether there may be additional admin levels available 
    if len(geob_api_response) > knownlevels and admLevel is None:
        print('Note. Additional Admin levels may have been added.')
        # Can check the JSON for all admin level on the fly.
        print('\tConfirm with {0}'.format(url))
        print('\tCheck output dir {0}'.format(config['dirs']['raw_data']))
    # Get the download urls from the api response
    for level in geob_api_response:
        adm = level[config['geoboundaries']['boundaryType_api_key']].lower()
        rawdir = config['dirs']['raw_data']
        raw = r'{0}{1}.zip'.format(config['geoboundaries']['raw'], adm)
        dl = level[config['geoboundaries']['downloadURL_api_key']]
        outpath = os.path.join(rawdir, raw)
        print(r'Downloading {0} to {1}'.format(dl, outpath))
        download_url(dl, outpath) 


##
# Compare with previous json - mainly to keep an eye on the updates
# End up passing the parameters via the SnakeMake config.
def get_all_adm0(previous=None):
    config = parse_yaml('config.yml')
    url = "{0}?{1}".format(config['geoboundaries']['url'],
                           config['geoboundaries']['all'])
    rawdir = os.path.join(config['dirs']['raw_data'],
                          config['geoboundaries']['subfolder'])
    geodb_api_response = get_json(url)
    df = pd.DataFrame(geodb_api_response)
    if previous:
        # Load the previous scan/download 
        # Check the date - if previous is available
        pass  
    else:
        # Use latest CSV with format 'gbd_YYYYMMDD.csv' 
        # Process the DataFrame to remove all dates that are up to date.
        # If no latest CSV found download the whole lot
        for index, row in df.iterrows():
            # Download the zip (to a GeoBoundaries ADM0 folder)
            # Unzip is part of the transform process. 
            # Use transform/adm0.py ? 
            dl = row['downloadURL']
            extra, fName = os.path.split(row['downloadURL'])
            outpath = os.path.join(rawdir, fName)
            print(r'Downloading {0} to {1}'.format(dl, outpath))
            download_url(dl, outpath)
        # Log the output details
        now = datetime.datetime.now().strftime("%Y%m%d")
        df.to_csv(os.path.join(rawdir, "gbd_{0}.csv".format(now)),
                  index=False)


##
#
#if __name__ == '__main__':
#    import pdb
#    pdb.set_trace()
#    get_geoboundaries_adm(admLevel="ADM0")
#    get_all_adm0()
#    pass
