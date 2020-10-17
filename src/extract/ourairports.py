import requests
import geopandas as gpd
import pandas as pd

next_link = "https://ourairportapi.com/airports-in/Yemen"
iso3 = 'YEM'

# Loop through pages and pull data from the API
session = requests.Session()

print(next_link)
request = session.get(url=next_link)
json = request.json()

# Loop through flows and append data to dataframe
airports = json["results"]
print(airports)
airport_list = []
for airport in airports:
    airport_list.append(airport)

airport_df = pd.DataFrame(airport_list)
print(airport_df)
airport_df = airport_df.drop(columns=['keywords'])

airport_pt = gpd.GeoDataFrame(airport_df,
    geometry=gpd.points_from_xy(airport_df.lon, airport_df.lat))

# Set CRS
airport_pt.crs = {'init': 'epsg:4326'}

# Export to file
airport_pt.to_csv("../../raw_data/ourairports_airports.csv", index=False)
# airport_pt.to_file("../../raw_data/wfp_airports.gpkg", driver="GPKG")
airport_pt.to_file("../../raw_data/ourairports_airports.shp")
airport_pt.to_file("../../processed_data/yem_tran_air_pt_s1_ourairports_pp.shp")
