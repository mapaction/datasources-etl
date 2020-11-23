import logging
import sys
import requests
import geopandas as gpd
import pandas as pd
logger = logging.getLogger(__name__)


###############################################################################
def get_wfp_airport_link(iso3, base_uri=None):
    """
    Fake look up function to convert a ISO3 code to a ourairportapi.com
    link (in full pipeline, this would rely on some ISO3 based lookup)
    :param iso3: ISO 3 code for country
    :return: url for country airport data from wfp_airports
    """
    if base_uri is None:
        base_uri = "https://geonode.wfp.org/geoserver/wfs?srsName=EPSG%3A4326&typename=geonode%3Awld_trs_airports_wfp&outputFormat=json&service=WFS&request=GetFeature"

    if iso3 == 'YEM':
        link_uri = base_uri + "Yemen"
    else:
        raise IOError("No country found with ISO3 code: %s" % iso3)

    return link_uri


###############################################################################
def get_wfp_airports(output_airport_uri, iso3, wfp_airports_url):
    """
    fetched our airports data from standard url
    :param output_airport_uri:
    :param iso3:
    :param raw_data_uri:
    :return:
    """

    # next_link = "https://geonode.wfp.org/geoserver/wfs?srsName=EPSG%3A4326&typename=geonode%3Awld_trs_airports_wfp&outputFormat=json&service=WFS&request=GetFeature"
    next_link = get_wfp_airport_link(iso3, base_uri=wfp_airports_url)
    iso3 = 'YEM'

    # Loop through pages and pull data from the API
    session = requests.Session()

    # print(next_link)
    request = session.get(url=next_link)
    json = request.json()

    # Loop through flows and append data to dataframe
    airports = json["features"]
    airport_list = []
    for airport in airports:
        airport_list.append(airport["properties"])

    airport_df = pd.DataFrame(airport_list)

    apt_yem = airport_df[airport_df['iso3'] == iso3]

    airport_pt = gpd.GeoDataFrame(apt_yem,
        geometry=gpd.points_from_xy(apt_yem.longitude, apt_yem.latitude))

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
