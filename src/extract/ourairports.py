import logging
import requests
import geopandas as gpd
import pandas as pd
logger = logging.getLogger(__name__)


###############################################################################
def get_ourairport_link(iso3):
    """
    Fake look up function to convert a ISO3 code to a ourairportapi.com
    link (in full pipeline, this would rely on some ISO3 based lookup)
    :param iso3: ISO 3 code for country
    :return: url for country airport data from ourairports
    """
    base_uri = "https://ourairportapi.com/airports-in/"
    if iso3 == 'YEM':
        link_uri = base_uri + "Yemen"
    else:
        raise IOError("No country found with ISO3 code: %s" % iso3)

    return link_uri


###############################################################################
def get_our_airports(output_airport_uri, iso3, raw_data_uri):

    next_link = get_ourairport_link(iso3)

    # Loop through pages and pull data from the API
    session = requests.Session()

    logger.info(next_link)
    request = session.get(url=next_link)
    json = request.json()

    # Loop through flows and append data to dataframe
    airports = json["results"]

    airport_df = pd.DataFrame(airports)
    logger.info(airport_df)

    if 'keywords' in airport_df.columns:
        old_kw = airport_df.keywords.copy()
        for kidx in old_kw.index:
            if old_kw.loc[kidx] is None:
                old_kw.loc[kidx] = ''
            else:
                old_kw.loc[kidx] = '; '.join(old_kw.loc[kidx])
        airport_df['keywords'] = old_kw

    airport_pt = gpd.GeoDataFrame(airport_df,
        geometry=gpd.points_from_xy(airport_df.lon, airport_df.lat))

    # Set CRS (known for ourairport to be WGS 1984)
    if airport_pt.crs is None:
        airport_pt.crs = {'init': 'epsg:4326'}

    # Export to file
    # airport_pt.to_csv("../../raw_data/ourairports_airports.csv", index=False)
    # airport_pt.to_file("../../raw_data/wfp_airports.gpkg", driver="GPKG")
    # airport_pt.to_file("../../raw_data/ourairports_airports.shp")
    # airport_pt.to_file("../../processed_data/yem_tran_air_pt_s1_ourairports_pp.shp")
    airport_pt.to_file(output_airport_uri)
