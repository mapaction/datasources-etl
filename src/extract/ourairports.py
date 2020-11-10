import requests
import geopandas as gpd
import pandas as pd

from utils.yaml_api import parse_yaml
from utils.requests_api import download_url

next_link = "https://ourairportapi.com/airports-in/Yemen"
iso3 = 'YEM'

# Loop through pages and pull data from the API
session = requests.Session()

print(next_link)
request = session.get(url=next_link)
json = request.json()

# Loop through flows and append data to dataframe
airports = json["results"]
airport_list = []
for airport in airports:
    airport_list.append(airport)

airport_df = pd.DataFrame(airport_list)
airport_df = airport_df.drop(columns=['keywords'])

airport_pt = gpd.GeoDataFrame(airport_df,
    geometry=gpd.points_from_xy(airport_df.lon, airport_df.lat))

# Set CRS
airport_pt.crs = {'init': 'epsg:4326'}

# Export to file
airport_pt.to_csv("../../raw_data/ourairports_airports.csv", index=False)
# airport_pt.to_file("../../raw_data/ourairports_airports.gpkg", driver="GPKG")
airport_pt.to_file("../../raw_data/ourairports_airports.shp")
airport_pt.to_file("../../processed_data/yem_tran_air_pt_s1_ourairports_pp.shp")


def get_airports():
    config = parse_yaml('config.yml')
    rawdir = config['dirs']['raw_data']
    outputZip = config['surrounding']['gadm']['rawzip']
    sourceURL = config['surrounding']['gadm']['url']
    source_gadm_world = os.path.join(rawdir, outputZip)
    print(r'Downloading {0} to {1}'.format(sourceURL, source_gadm_world))
    download_url(sourceURL, source_gadm_world)