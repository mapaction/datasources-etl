import sys

import geopandas as gpd


CRS = 'EPSG:2090'
GADM_YEMEN_FILENAME = 'gadm36_YEM.gpkg'
GADM_LAYER = 'gadm36_YEM_0'


def transform_cod():
    transform('cod', sys.argv[1], sys.argv[2])


def transform_gadm():
    transform('gadm', sys.argv[1], sys.argv[2])


def transform(source: str, input_filename: str, output_filename: str):
    """
    :param source: "cod" or "gadm"
    """
    if source == "cod":
        df_adm0 = gpd.read_file(f'zip://{input_filename}')
    elif source == "gadm":
        df_adm0 = gpd.read_file(f'zip://{input_filename}!{GADM_YEMEN_FILENAME}', layer=GADM_LAYER)
    # Change CRS
    df_adm0 = df_adm0.to_crs(CRS)
    # For GADM, modify the column names to suit the schema
    if source == "gadm":
        gadm_schema_mapping = {
            'NAME_0': 'admin0Name'
        }
        df_adm0 = df_adm0.rename(columns=gadm_schema_mapping)
    # Write to output
    df_adm0.to_file(output_filename)
