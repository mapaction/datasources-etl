import os
import zipfile

from utils.yaml_api import parse_yaml
from utils.requests_api import download_url

import pdb


def get_world():
    config = parse_yaml('config.yml')
    rawdir = config['dirs']['raw_data']
    outputZip = config['surrounding']['gadm']['rawzip']
    sourceURL = config['surrounding']['gadm']['url']
    source_gadm_world = os.path.join(rawdir, outputZip)
    print(r'Downloading {0}'.format(sourceURL))
    download_url(sourceURL, source_gadm_world)
    # Unzip - as reading zipped world geopackage takes too long
    print(r'Unzipping {0}'.format(config['surrounding']['gadm']['url']))
    gadmzip = zipfile.ZipFile(source_gadm_world, 'r')
    gadmzip.extractall(rawdir)
    gadmzip.close()


