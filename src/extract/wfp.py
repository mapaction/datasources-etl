import requests
import geopandas as gpd
import pandas as pd

r = requests.get("https://geonode.wfp.org/geoserver/wfs?srsName=EPSG%3A4326&typename=geonode%3Awld_trs_airports_wfp&outputFormat=json&service=WFS&request=GetFeature")
r.raise_for_status()

data = r.json()

df = pd.json_normalize(data['features'])
print(df)
df = df.drop(columns=[
    'geometry',
    'geometry.type',
    'geometry.coordinates',
    'properties.nameshort',
    'properties.namelong',
    'properties.namealt',
    'properties.city',
    'properties.icao',
    'properties.iata',
    'properties.apttype',
    'properties.aptclass',
    'properties.authority',
    'properties.status',
    'properties.dmg',
    'properties.rwpaved',
    'properties.rwlengthm',
    'properties.rwlengthf',
    'properties.elevm',
    'properties.elevf',
    'properties.humuse',
    'properties.humoperatedby',
    'properties.locprecision',
    'properties.iso3',
    'properties.iso3_op',
    'properties.country',
    'properties.lastcheckdate',
    'properties.remarks',
    'properties.url_lca',
    'properties.source',
    'properties.createdate',
    'properties.updatedate',
    'properties.geonameid'])

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df["properties.longitude"], df["properties.latitude"]))

gdf = gdf.drop(columns=[
    'properties.longitude',
    'properties.latitude'])

for col in gdf.columns:
    print(col)

gdf.to_file("../../raw_data/wfp_airports.shp")