import os

from utils.yaml_api import parse_config
from utils.requests_api import download_url


GADM_YEMEN_ADDRESS = 'https://biogeo.ucdavis.edu/data/gadm3.6/gpkg/gadm36_YEM_gpkg.zip'


def get_adm0():
    config = parse_config()
    filepath_gadm = os.path.join(config['dirs']['raw_data'], config['adm0']['gadm']['raw'])
    download_url(GADM_YEMEN_ADDRESS, filepath_gadm)
