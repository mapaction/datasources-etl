import os
import shutil
import sys

from utils.hdx_api import query_api


HDX_YEMEN_ADDRESS = 'yemen-admin-boundaries'
HDX_YEMEN_FILENAME = 'yem_adm_govyem_cso_ochayemen_20191002_GPKG.zip'


def get_adm0_snakemake():
    get_adm0(sys.argv[1], sys.argv[2])


def get_adm0(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_YEMEN_ADDRESS, raw_data_dir,
                             [HDX_YEMEN_FILENAME])[HDX_YEMEN_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)
