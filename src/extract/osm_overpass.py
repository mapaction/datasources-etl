import sys
import requests
import json

from utils.yaml_api import parse_yaml

def extract_osm_query():
    osm_query(sys.argv[1], sys.argv[2],

def

def osm_query(osm_yml: dict, iso2_country: str):
    """ Country based query using Overpass Query Language.  Using key value pairs,
        contructs a simple OSM query on relations, ways & nodes.

        Input osm_tags should be a dictionary, where:
        (1) one key is 'osm_types' which is a list of osm data types to return (e.g. way, boundary, nodes)
        (2) the other key is 'tags' with a value another dictionary:
            (a) this other dictionary is has the key of osm tag names, and the values are lists of desired
             values for the tag name.

        For example {osm_types: ['relation','way'], tags: {'highway': ['motorway', 'trunk']}}

        Input iso2_country is the two letter ISO country code for a specific country

        The query will be built built around requesting all matched osm data types where the
        property (key) matches one of the related values.
        """
    # Define output type. Default is XML
    output_format = '[out:json]; \n'
    # Area filter part of query
    area_filter = f'(area["ISO3166-1"="{iso2_country}"]["admin_level"="2"];)->.a; \n'
    # Main part of query is the union of sets returned with key-value tags.
    main_query = '( \n'
    for osm_type in osm_yml['osm_types']:
        for key, value in osm_yml['tags'].items():
            if type(value) == list:
                for tag_value in value:
                    main_query += f'{osm_type}[{key}={tag_value}](area.a); \n'
            elif value == None:
                main_query += f'{osm_type}[{key}](area.a); \n'
            else:
                main_query += f'{osm_type}[{key}={value}](area.a); \n'
    main_query += '); \n'
    # recurse through previous set to bring back all nodes, then return final set
    recurse_out = (
        '(._;>;); \n'
        'out body qt;')
    # Combine all parts of query into full query to send to Overpass
    final_query = (output_format + area_filter
                   + main_query + recurse_out)
    return final_query
