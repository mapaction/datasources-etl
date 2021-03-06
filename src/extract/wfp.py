import logging
import sys
import requests
import geopandas as gpd
import pandas as pd
logger = logging.getLogger(__name__)


###############################################################################
def get_wfp_airport_link():
    """
    Fake look up function to convert a ISO3 code to a ourairportapi.com
    link (in full pipeline, this would rely on some ISO3 based lookup)
    :param iso3: ISO 3 code for country
    :return: url for country airport data from wfp_airports
    """
    base_uri = "https://geonode.wfp.org/geoserver/wfs?srsName=EPSG%3A4326&" \
               + "typename=geonode%3Awld_trs_airports_wfp&outputFormat=json&" \
               + "service=WFS&request=GetFeature"

    return base_uri


###############################################################################
def get_wfp_airports(output_airport_uri, iso3, wfp_airports_url):
    """
    fetched our airports data from standard url
    :param output_airport_uri:
    :param iso3:
    :param wfp_airports_url:
    :return:
    """

    if wfp_airports_url is None:
        wfp_airports_url = get_wfp_airport_link()

    # Pull data from the API as a json lump
    this_request = requests.get(wfp_airports_url)
    logger.info("Status code: %s" % str(this_request.status_code))
    logger.info("URL: %s" % wfp_airports_url)
    json = this_request.json()

    # Loop through flows and append data to dataframe
    airports = json["features"]
    airport_list = []
    for airport in airports:
        airport_list.append(airport["properties"])

    airport_df = pd.DataFrame(airport_list)
    apt_country = airport_df[airport_df['iso3'] == iso3]

    airport_pt = gpd.GeoDataFrame(apt_country,
        geometry=gpd.points_from_xy(apt_country.longitude,
                                    apt_country.latitude))

    # Set CRS
    if airport_pt.crs is None:
        airport_pt.crs = {'init': 'epsg:4326'}

    # Export to file
    # airport_pt.to_file("../../raw_data/wfp_airports.gpkg", driver="GPKG")
    # airport_pt.to_file("../../raw_data/wfp_airports.shp", encoding='utf-8')
    # airport_pt.to_file("../../processed_data/yem_tran_air_pt_s1_wfp_pp.shp", encoding='utf-8')
    # airport_pt.to_csv("../../raw_data/wfp_airports.csv", index=False, encoding='utf-8')
    airport_pt.to_file(output_airport_uri)


###############################################################################
def get_wfp_airports_snakemake():
    """snakemake rule"""
    get_wfp_airports(sys.argv[1], sys.argv[2], sys.argv[3])
