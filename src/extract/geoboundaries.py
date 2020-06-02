import os
import json

from utils.yaml_api import parse_yaml
from utils.requests_api import get_json 
from utils.requests_api import download_url 


##
# https://www.geoboundaries.org/#dataTable
def get_geoboundaries_adm(admLevel=None):
    config = parse_yaml('config.yml')
    rooturl = config['geoboundaries']['url']
    iso = config['constants']['ISO3']
    url = r"{0}?ISO={1}".format(rooturl, iso)
    knownlevels = config['geoboundaries']['knownlevels']
    if admLevel: url = r"{0}&ADM={1}".format(url, admLevel)
    # We want all available admin boundaries so skip specifying which AMD to
    # process. Otherwise include a specific ADM level to process.
    geob_api_response = get_json(url)
    # Check whether there may be additional admin levels available 
    if len(geob_api_response) > knownlevels and admLevel is None:
        print('Note. Additional Admin levels may have been added.')
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


if __name__ == '__main__':
    get_geoboundaries_adm()
