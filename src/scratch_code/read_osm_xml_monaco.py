"""
Rough script of python code that reads in an XML of Monaco boundary data
received from OSM and parses it into points, then lines, then finally
polygon boundaries. Should be useful for extracting points/lines/other polygons
from OSM data.
Note: geodataframes are not written to file in this script.
"""

import logging; logger = logging.getLogger()
import os
import re
import json
import pandas as pd
import shapely
import geopandas as gpd

# using https://wiki.openstreetmap.org/wiki/Elements as a guide
xml_uri = "monaco_boundaries_osm.xml"

with open(xml_uri, 'r') as xx:
    raw_xml = xx.read()

# noticed an errant  UTF-8 BOM character prefixing your file
# (python requests module does that sometimes)
if len(re.findall("\\ufeff", raw_xml)) > 0:
    raw_xml = raw_xml.replace("\ufeff", "")

xml_data = json.loads(raw_xml)

ways = []
nodes = []
relations = []

for el in xml_data['elements']:
    if el['type'] == 'way':
        ways.append(el)
    elif el['type'] == 'node':
        nodes.append(el)
    elif el['type'] == 'relation':
        relations.append(el)

# first things first, lets make all the nodes into points
node_df = pd.DataFrame(nodes)
node_pt = gpd.GeoDataFrame(node_df, 
    geometry=gpd.points_from_xy(node_df.lon, node_df.lat))

# now assemble them into ways
assembled_way = []
for way in ways:
    way_from_node = []
    for node in way['nodes']:
        way_from_node.append(node_pt[node_pt['id'] == node].geometry.item())
    line_from_node = shapely.geometry.LineString(way_from_node)
    this_way = {'geometry': line_from_node}
    # not bothering with retaining "type"
    # "nodes" are basically from line_from_node above so no need to repeat
    for wkey in way.keys():
        if wkey == 'id':
            this_way[wkey] = way[wkey]
        elif wkey == 'tags':
            for tag in way['tags'].keys():
                this_way[tag] = way['tags'][tag]
    assembled_way.append(this_way)
way_ln = gpd.GeoDataFrame(pd.DataFrame(assembled_way))

# relations seem to have centroids and polygons
# excluding translated names for polygons for geopackage output
# (centroids/polygons will contain full info for geojson output)
tagtokeep = []
tagall = []
for relation in relations:
    for tag in relation['tags'].keys():
        if tag not in tagall:
            tagall.append(tag)
            if tag.startswith("name:"):
                if tag == "name:en":
                    tagtokeep.append(tag)
            elif tag.startswith("official_name:"):
                if tag == "official_name:en":
                    tagtokeep.append(tag)
            else:
                tagtokeep.append(tag)

# now let's piece together relation polygons and centroids
relation_pt_list = []
relation_py_list = []

for relation in relations:
    this_rel_pt = {}
    this_rel_py = {}
    for rkey in relation.keys():
        # useful geoinformation buried in "members" entry
        if rkey == 'members':
            temp_df = pd.DataFrame(relation[rkey])
            admin_centroid_df = temp_df[temp_df['role'] == "admin_centre"]
            outer_df = temp_df[temp_df['role'] == "outer"]
            inner_df = temp_df[temp_df['role'] == "inner"] # enclaves?
            other_df = temp_df[~temp_df['role'].isin(
                ["inner", "outer", "admin_centre"])]
            # deal with admin centres first
            admin_centroid_list = []
            for acidx in admin_centroid_df.index:
                this_ad_centre = admin_centroid_df.loc[acidx].to_dict()
                select_node = node_pt["id"] == admin_centroid_df.loc[0, "ref"]
                this_ad_centre['geometry'] = node_pt[select_node]['geometry']
                admin_centroid_list.append(this_ad_centre)
            # now with outline geometries
            outer_rel = []
            for idx in outer_df.index:
                select_way = way_ln["id"] == outer_df.loc[idx, 'ref']
                outer_way = way_ln[select_way]
                for geom in outer_way['geometry']:
                    if not any(ln.equals(geom) for ln in outer_rel):
                        outer_rel.append(geom)
            outer_line = shapely.ops.linemerge(
                shapely.geometry.MultiLineString(outer_rel))
            if isinstance(outer_line, shapely.geometry.MultiLineString):
                outer_poly = [{'geometry': shapely.geometry.Polygon(o)} 
                              for o in outer_line]
            else:
                outer_poly = [{'geometry': 
                              shapely.geometry.Polygon(outer_line)}]
            # TODO: enclaves exist, but I've not bothered with them here
            if len(inner_df) > 0:
                logger.warning("Not incorporated enclaves in processing")
            # TODO: do something with other information? e.g., land_area, label
            if len(other_df) > 0:
                for oidx in other_df.index:
                    logger.warning("Not using %s" % other_df.loc[oidx, "role"])
        elif rkey == 'tags': # deal with tags
            for rkk in relation[rkey].keys():
                this_rel_pt[rkk] = relation[rkey][rkk]
                if rkk in tagtokeep:
                    this_rel_py[rkk] = relation[rkey][rkk]
        else:
            this_rel_pt[rkey] = relation[rkey]
            this_rel_py[rkey] = relation[rkey]
    relation_py_list += [{**opy, **this_rel_py} for opy in outer_poly]
    relation_pt_list += [{**adc, **this_rel_pt} for adc in admin_centroid_list]

relation_py_df = gpd.GeoDataFrame(pd.DataFrame(relation_py_list))
relation_pt_df = gpd.GeoDataFrame(pd.DataFrame(relation_pt_list))











