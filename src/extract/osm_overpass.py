import sys
import requests
import json

from utils.yaml_api import parse_yaml

def extract_osm_query():
    osm_url = sys.argv[1] #"http://overpass-api.de/api/interpreter?"
    country = sys.argv[2] #'YE'
    osm_schema = parse_yaml(sys.argv[3]) #parse_yaml('schemas/osm_tags_lakes.yml')
    output_file = sys.argv[4] #'raw_data/osm_rivers_pol.xml'
    get_osm_xml(osm_url, osm_query(osm_schema, country), output_file)

def osm_query(osm_yml: dict, iso2_country: str):
    """ Country based query using Overpass Query Language.  Using key value pairs,
        contructs a simple OSM query on relations, ways & nodes.

        Input osm_tags should be a dictionary, where:
        (1) it has exactly two elements, which are:
            (a) osm_types - a list of geometry OSM data types (relation, way, node)
            (b) tags - a list of one or more dictionaries where the key values are those tag-name & tag-values requested

        For example {osm_types: [values], tags: {['highway': ['motorway', 'trunk']}]}

        Input iso2_country is the two letter ISO country code for a specific country

        The query will be built around requesting all matched osm data types where the
        property (key) matches one of the related values.
        """

    # Define output type. Default is XML
    # Area filter part of query
    area_filter = f'(area["ISO3166-1"="{iso2_country}"]["admin_level"="2"];)->.a; \n'
    # Main part of query is the union of sets returned with key-value tags.
    # this is perhaps overcomplicated but tries to accept different tag values in yaml file,
    # will work whether yaml tag value is list, string or dict.
    main_query = '( \n'
    for osm_type in osm_yml['osm_types']:
        if type(osm_yml['tags']) == list:
            for tags in osm_yml['tags']:
                for tag, value in tags.items():
                    if type(value) == list:
                        for tag_value in value:
                            main_query += f'{osm_type}[{tag}={tag_value}](area.a); \n'
                    elif type(value) == str:
                        main_query += f'{osm_type}[{tag}={value}](area.a); \n'
                    elif value == None:
                        main_query += f'{osm_type}[{tag}](area.a); \n'
        elif type(osm_yml['tags']) == dict:
            for tag, value in osm_yml['tags'].items():
                if type(value) == list:
                    for tag_value in value:
                        main_query += f'{osm_type}[{tag}={tag_value}](area.a); \n'
                elif type(value) == str:
                    main_query += f'{osm_type}[{tag}={value}](area.a); \n'
                elif value == None:
                    main_query += f'{osm_type}[{tag}](area.a); \n'
    main_query += '); \n'
    # recurse through previous set to bring back all nodes, then return final set
    recurse_out = (
        '(._;>;); \n'
        'out body qt;')
    # Combine all parts of query into full query to send to Overpass
    final_query = (area_filter
                   + main_query + recurse_out)
    return final_query


def get_osm_xml(api_url, osm_query, output_file):
    response  = requests.get(api_url,
                                params={'data': osm_query})
    data = response.text
    if response.status_code == 200:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(response.text)
    else:
        pass