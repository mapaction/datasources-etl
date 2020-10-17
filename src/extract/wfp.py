import requests
import geopandas as gpd
import pandas as pd

next_link = "https://geonode.wfp.org/geoserver/wfs?srsName=EPSG%3A4326&typename=geonode%3Awld_trs_airports_wfp&outputFormat=json&service=WFS&request=GetFeature"
iso3 = 'YEM'

# Loop through pages and pull data from the API
session = requests.Session()

print(next_link)
request = session.get(url=next_link)
json = request.json()

# Loop through flows and append data to dataframe
# print(json)
airports = json["features"]
# print(airports)
airport_list = []
for airport in airports:
    airport_list.append(airport["properties"])

airport_df = pd.DataFrame(airport_list)

apt_yem = airport_df[airport_df['iso3'] == iso3]

airport_pt = gpd.GeoDataFrame(apt_yem,
    geometry=gpd.points_from_xy(apt_yem.longitude, apt_yem.latitude))

# Set CRS
airport_pt.crs = {'init': 'epsg:4326'}

# Export to file
# airport_pt.to_file("../../raw_data/wfp_airports.gpkg", driver="GPKG")
airport_pt.to_file("../../raw_data/wfp_airports.shp", encoding='utf-8')
airport_pt.to_file("../../processed_data/yem_tran_air_pt_s1_wfp_pp.shp", encoding='utf-8')
airport_pt.to_csv("../../raw_data/wfp_airports.csv", index=False, encoding='utf-8')
