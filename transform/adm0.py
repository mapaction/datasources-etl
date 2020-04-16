import os
import geopandas as gpd

from utils.yaml_api import parse_config


CRS = 'EPSG:2090'
GADM_YEMEN_FILENAME = 'gadm36_YEM.gpkg'


def transform_adm0(source: str):
    """
    :param source: "cod" or "gadm"
    """
    config = parse_config()
    input_filename = os.path.join(config["dirs"]["raw_data"], config["adm0"][source]["raw"])
    if source == "cod":
        df_adm0 = gpd.read_file(f'zip://{input_filename}')
    elif source == "gadm":
        df_adm0 = gpd.read_file(f'zip://{input_filename}!{GADM_YEMEN_FILENAME}', layer='gadm36_YEM_0')
    # Change CRS
    df_adm0 = df_adm0.to_crs(CRS)
    # For GADM, modify the column names to suit the schema
    if source == "gadm":
        gadm_schema_mapping = {
            'NAME_0': 'admin0Name'
        }
        df_adm0 = df_adm0.rename(columns=gadm_schema_mapping)
    # Write to output
    output_filename = os.path.join(config["dirs"]["processed_data"], config["adm0"][source]["processed"])
    df_adm0.to_file(output_filename)
