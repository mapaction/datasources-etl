import os
import shutil
import sys

from utils.hdx_api import query_api


HDX_YEMEN_ADDRESS = 'yemen-admin-boundaries'
HDX_YEMEN_FILENAME = 'yem_adm_govyem_cso_ochayemen_20191002_GPKG.zip'

HDX_YEMEN_ROAD_ADDRESS = 'yemen-roads'
HDX_YEMEN_ROAD_FILENAME = 'ymn-roads.zip'

HDX_YEMEN_RIVER_ADDRESS = 'yemen-water-bodies'
HDX_YEMEN_RIVER_FILENAME = 'wadies.zip'

HDX_YEMEN_SEAPORT_ADDRESS = 'yemen-ports'
HDX_YEMEN_SEAPORT_FILENAME = 'ymn-seaport.zip'

HDX_GLOBAL_SEAPORT_ADDRESS = 'world-port-index'
HDX_GLOBAL_SEAPORT_FILENAME = 'world_port_index.zip'

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


# HDX COD Roads
def get_roads_snakemake():
    get_roads(sys.argv[1], sys.argv[2])


def get_roads(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_YEMEN_ROAD_ADDRESS, raw_data_dir,
                             [HDX_YEMEN_ROAD_FILENAME])[HDX_YEMEN_ROAD_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)


# HDX COD Rivers
def get_rivers_snakemake():
    get_rivers(sys.argv[1], sys.argv[2])


def get_rivers(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_YEMEN_RIVER_ADDRESS, raw_data_dir,
                             [HDX_YEMEN_RIVER_FILENAME])[HDX_YEMEN_RIVER_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)


# HDX COD Seaports
def get_seaports_snakemake():
    get_seaports(sys.argv[1], sys.argv[2])


def get_seaports(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_YEMEN_SEAPORT_ADDRESS, raw_data_dir,
                             [HDX_YEMEN_SEAPORT_FILENAME])[HDX_YEMEN_SEAPORT_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)

# HDX COD Global Seaports
def get_global_seaports_snakemake():
    get_global_seaports(sys.argv[1], sys.argv[2])


def get_global_seaports(raw_data_dir: str, output_filename: str):
    filepath_hdx = query_api(HDX_GLOBAL_SEAPORT_ADDRESS, raw_data_dir,
                             [HDX_GLOBAL_SEAPORT_FILENAME])[HDX_GLOBAL_SEAPORT_FILENAME]
    shutil.move(os.path.join(raw_data_dir, filepath_hdx),
                output_filename)