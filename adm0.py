import os

import geopandas as gpd
from hdx.utilities.path import get_temp_dir

from utils.hdx_api import query_api
from utils.requests_api import download_url


GADM_YEMEN_ADDRESS = 'https://biogeo.ucdavis.edu/data/gadm3.6/gpkg/gadm36_YEM_gpkg.zip'
GADM_YEMEN_FILENAME = 'gadm36_YEM.gpkg'
HDX_YEMEN_ADDRESS = 'yemen-admin-boundaries'
HDX_YEMEN_FILENAME = 'yem_adm_govyem_cso_ochayemen_20191002_GPKG.zip'
CRS = 'EPSG:3395'


def main(debug=False):
    data_dir = get_temp_dir('yemen_adm0')
    # Get HDX data
    if not debug:
        filepath_hdx = query_api(HDX_YEMEN_ADDRESS, data_dir, [HDX_YEMEN_FILENAME])[HDX_YEMEN_FILENAME]
    else:
        filepath_hdx = os.path.join(data_dir, f'{HDX_YEMEN_FILENAME}1.zipped geopackage')
    # Get GADM data
    filepath_gadm = os.path.join(data_dir, 'gadm_adm0.zip')
    if not debug:
        download_url(GADM_YEMEN_ADDRESS, filepath_gadm)
    # Open them and compare
    df_hdx = gpd.read_file(f'zip://{filepath_hdx}')
    df_gadm = gpd.read_file(f'zip://{filepath_gadm}!{GADM_YEMEN_FILENAME}')
    # Change CRS
    df_hdx = df_hdx.to_crs(CRS)
    df_gadm = df_gadm.to_crs(CRS)
