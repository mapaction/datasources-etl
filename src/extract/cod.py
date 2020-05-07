import os
import shutil
import sys

from utils.hdx_api import query_api


HDX_YEMEN_ADDRESS = 'yemen-admin-boundaries'
HDX_YEMEN_FILENAME = 'yem_adm_govyem_cso_ochayemen_20191002_GPKG.zip'


# HDX COD Admin 0
def get_adm0_snakemake():
    get_adm0(sys.argv[1], sys.argv[2])


def get_adm0(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_YEMEN_ADDRESS, raw_data_dir,
                             [HDX_YEMEN_FILENAME])[HDX_YEMEN_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)

# HDX COD Admin 1
def get_adm1_snakemake():
    get_adm1(sys.argv[1], sys.argv[2])


def get_adm1(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_YEMEN_ADDRESS, raw_data_dir,
                             [HDX_YEMEN_FILENAME])[HDX_YEMEN_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)

# HDX COD Admin 2
def get_adm2_snakemake():
    get_adm2(sys.argv[1], sys.argv[2])


def get_adm2(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_YEMEN_ADDRESS, raw_data_dir,
                             [HDX_YEMEN_FILENAME])[HDX_YEMEN_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)

# HDX COD Admin 3
def get_adm3_snakemake():
    get_adm3(sys.argv[1], sys.argv[2])


def get_adm3(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_YEMEN_ADDRESS, raw_data_dir,
                             [HDX_YEMEN_FILENAME])[HDX_YEMEN_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)