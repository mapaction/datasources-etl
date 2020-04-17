import os
import shutil

from utils.yaml_api import parse_config
from utils.hdx_api import query_api


HDX_YEMEN_ADDRESS = 'yemen-admin-boundaries'
HDX_YEMEN_FILENAME = 'yem_adm_govyem_cso_ochayemen_20191002_GPKG.zip'
CRS = 'EPSG:2090'


def get_adm0():
    config = parse_config()
    filepath_hdx = query_api(HDX_YEMEN_ADDRESS, config['dirs']['raw_data'],
                             [HDX_YEMEN_FILENAME])[HDX_YEMEN_FILENAME]
    shutil.move(os.path.join(config['dirs']['raw_data'], filepath_hdx),
                os.path.join(config['dirs']['raw_data'], config['adm0']['cod']['raw']))
