import os

configfile: "config.yml"

##EXTRACT
##Extract HDX COD
rule extract_adm0_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm0']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_adm0_cod {params} {output}"

rule extract_adm1_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm1']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_adm1_cod {params} {output}"

rule extract_adm2_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm2']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_adm2_cod {params} {output}"

rule extract_adm3_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm3']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_adm3_cod {params} {output}"


rule  extract_rivers_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['rivers']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_rivers_cod {params} {output}"

rule  extract_seaports_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['seaports']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_seaports_cod {params} {output}"

rule  extract_global_seaports_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['seaports_global']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_global_seaports_cod {params} {output}"

# Extract GADM
rule extract_adm0_gadm:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm0']['gadm']['raw'])
    params:
        url=config['adm0']['gadm']['url']
    shell:
        "curl {params} -o {output} -O -J -L"

rule extract_adm1_gadm:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm1']['gadm']['raw'])
    params:
        url=config['adm1']['gadm']['url']
    shell:
        "curl {params} -o {output} -O -J -L"

rule extract_adm2_gadm:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm2']['gadm']['raw'])
    params:
        url=config['adm2']['gadm']['url']
    shell:
        "curl {params} -o {output} -O -J -L"

# Generic rule to extract all GADM admin levels for a particular country.
rule extract_gadm_adm:
    output:
        os.path.join(config['dirs']['raw_data'],
        "{0}_{1}".format(config['constants']['ISO3'], config['gadm']['raw']))
    params:
        url=config["gadm"]["url"].format(ISO3=config["constants"]["ISO3"])
    shell:
        "curl {params} -o {output} -O -J -L"

# Following should negate the need for the above GADM rules since the world 
# file is processed.
rule extract_world_gadm:
    # Note. By removing the output Snakemake will always re-run the process
    # this means we could program a test into the extract process if
    # necessary.
    output:
        os.path.join(
            config['dirs']['raw_data'], config['surrounding']['gadm']['rawzip'])
    shell:
        "extract_world_gadm"

# Extract Geoboundaries
rule extract_geoboundaries:
    output:
      [
        "{0}/{1}".format(config['dirs']['raw_data'],r'geobnd_adm0.zip'),
        "{0}/{1}".format(config['dirs']['raw_data'],r'geobnd_adm1.zip'),
        "{0}/{1}".format(config['dirs']['raw_data'],r'geobnd_adm2.zip')
      ]
    shell:
        "extract_geoboundaries"

## OSM Extract ##

rule extract_osm_rivers:
    input:
        os.path.join(
            config['dirs']['schemas'], config['osm']['rivers']['osm_tags'])
    params:
        url=config['osm']['url'],
        country=config['constants']['ISO2']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['osm']['rivers']['raw_osm']),
        os.path.join(
            config['dirs']['raw_data'], config['osm']['rivers']['raw_shp'])
    shell:
        "extract_osm \"{params.url}\" \"{params.country}\" {input} {output}"

rule extract_osm_lakes:
    input:
        os.path.join(
            config['dirs']['schemas'], config['osm']['lakes']['osm_tags'])
    params:
        url=config['osm']['url'],
        country=config['constants']['ISO2']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['osm']['lakes']['raw_osm']),
        os.path.join(
            config['dirs']['raw_data'], config['osm']['lakes']['raw_shp'])
    shell:
        "extract_osm \"{params.url}\" \"{params.country}\" {input} {output}"

rule extract_osm_rail:
    input:
        os.path.join(
            config['dirs']['schemas'], config['osm']['rail']['osm_tags'])
    params:
        url=config['osm']['url'],
        country=config['constants']['ISO2']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['osm']['rail']['raw_osm']),
        os.path.join(
            config['dirs']['raw_data'], config['osm']['rail']['raw_shp'])
    shell:
        "extract_osm \"{params.url}\" \"{params.country}\" {input} {output}"

rule extract_osm_airports:
    input:
        os.path.join(
            config['dirs']['schemas'], config['osm']['airports']['osm_tags'])
    params:
        url=config['osm']['url'],
        country=config['constants']['ISO2']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['osm']['airports']['raw_osm']),
        os.path.join(
            config['dirs']['raw_data'], config['osm']['airports']['raw_shp'])
    shell:
        "extract_osm \"{params.url}\" \"{params.country}\" {input} {output}"

rule extract_osm_seaports:
    input:
        os.path.join(
            config['dirs']['schemas'], config['osm']['seaports']['osm_tags'])
    params:
        url=config['osm']['url'],
        country=config['constants']['ISO2']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['osm']['seaports']['raw_osm']),
        os.path.join(
            config['dirs']['raw_data'], config['osm']['seaports']['raw_shp'])
    shell:
        "extract_osm \"{params.url}\" \"{params.country}\" {input} {output}"


rule extract_osm_admin:
    input:
        os.path.join(
            config['dirs']['schemas'], config['osm']['admin']['osm_tags'])
    params:
        url=config['osm']['url'],
        country=config['constants']['ISO2']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['osm']['admin']['raw_osm']),
        os.path.join(
            config['dirs']['raw_data'], config['osm']['admin']['raw_shp'])
    shell:
        "extract_osm \"{params.url}\" \"{params.country}\" {input} {output}"

rule extract_osm_roads:
    input:
        os.path.join(
            config['dirs']['schemas'], config['osm']['roads']['osm_tags'])
    params:
        url=config['osm']['url'],
        country=config['constants']['ISO2']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['osm']['roads']['raw_osm']),
        os.path.join(
            config['dirs']['raw_data'], config['osm']['roads']['raw_shp'])
    shell:
        "extract_osm \"{params.url}\" \"{params.country}\" {input} {output}"

####

rule extract_geoboundaries_adm0_all:
    shell:
        "extract_geoboundaries_adm0_all"

# Extract SRTM
# TODO Note: SRTM Snakemake rule does not currently work - functionality has been parked for SDS PoC
rule extract_srtm30:
    # not sure how to employ (optional) keyword arguments into snakemake
    params:
        download_folder=os.path.join(config['dirs']['raw_data'], config['srtm']['srtm30']['dl_subdir']),
        config=config['constants']['crs']
    output:
        os.path.join(config['dirs']['processed_data'], config['srtm']['srtm30']['processed'])
    shell:
        "extract_srtm30 {output} {params}"

rule extract_srtm90:
    # not sure how to employ (optional) keyword arguments into snakemake
    params:
        download_folder=os.path.join(config['dirs']['raw_data'], config['srtm']['srtm90']['dl_subdir']),
        config=config['constants']['crs']
    output:
        os.path.join(config['dirs']['processed_data'], config['srtm']['srtm90']['processed'])
    shell:
        "extract_srtm90 {output} {params}"

rule extract_ourairports:
    params:
        config['constants']['ISO3'],
        config['ourairports']['url']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['ourairports']['raw'])
    shell:
        "extract_ourairports {output} {params}"

rule extract_wfp_airports:
    params:
        iso3=config['constants']['ISO3'],
        url=config['wfp_airports']['url']
    output:
        os.path.join(
            config['dirs']['raw_data'], config['wfp_airports']['raw'])
    shell:
        "extract_wfp_airports {output} \"{params.iso3}\" \"{params.url}\" "

##TRANSFORM
##Transform HDX COD

rule transform_adm0_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm0']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm0']['cod']['processed'])
    shell:
        "transform_adm0_cod {input} {output}"

rule transform_adm1_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm1']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm1']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm1']['cod']['processed'])
    shell:
        "transform_adm1_cod {input} {output}"

rule transform_adm2_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm2']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm2']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm2']['cod']['processed'])
    shell:
        "transform_adm2_cod {input} {output}"

rule transform_adm3_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm3']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm3']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm3']['cod']['processed'])
    shell:
        "transform_adm3_cod {input} {output}"

rule transform_rivers_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['rivers']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['rivers']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['rivers']['cod']['processed'])
    shell:
        "transform_rivers_cod {input} {output}"

rule transform_seaports_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['seaports']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['seaports']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['seaports']['cod']['processed'])
    shell:
        "transform_seaports_cod {input} {output}"

##Transform GADM
rule transform_adm0_gadm:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm0']['gadm']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm0']['gadm']['processed'])
    shell:
        "transform_adm0_gadm {input} {output}"

rule transform_adm1_gadm:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm1']['gadm']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm1']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm1']['gadm']['processed'])
    shell:
        "transform_adm1_gadm {input} {output}"

rule transform_adm2_gadm:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm2']['gadm']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm2']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm2']['gadm']['processed'])
    shell:
        "transform_adm2_gadm {input} {output}"
rule transform_surrounding_gadm:
    output:
        os.path.join(config['dirs']['processed_data'], config['surrounding']['gadm']['processed'])
    shell:
        "transform_surrounding_gadm"

# Generic transform all GADM admin levels included within the download.
rule transform_gadm_adm:
    input:
        os.path.join(config['dirs']['raw_data'],
        "{0}_{1}".format(config['constants']['ISO3'], config['gadm']['raw'])), 
        os.path.join(config['dirs']['schemas'],config['gadm']['schema']),
        config['dirs']['processed_data']
    shell:
        "transform_gadm_adm {input}"

# Transform Geoboundaries
rule transform_adm0_geoboundaries:
    input:
        os.path.join(config['dirs']['raw_data'],
            config['geoboundaries']['adm0']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join( config['dirs']['processed_data'], 
            config['geoboundaries']['adm0']['processed']),
    shell:
        "transform_adm0_geoboundaries {input} {output}"

rule transform_adm1_geoboundaries:
    input:
        os.path.join(config['dirs']['raw_data'],
            config['geoboundaries']['adm1']['raw']),
        os.path.join( config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], 
            config['geoboundaries']['adm1']['processed'])
    shell:
        "transform_adm1_geoboundaries {input} {output}"
 
rule transform_adm2_geoboundaries:
    input:
        os.path.join( config['dirs']['raw_data'],
            config['geoboundaries']['adm2']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], 
            config['geoboundaries']['adm2']['processed'])
    shell:
        "transform_adm2_geoboundaries {input} {output}"

rule transform_surrounding_geoboundaries:
    shell:
        "transform_surrounding_geoboundaries"

# Extract roads

rule extract_roads_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['roads']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_roads_cod {params} {output}"

# Transform roads

rule transform_roads_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['roads']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['roads']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['roads']['cod']['processed'])
    shell:
        "transform_roads_cod {input} {output}"

rule transform_roads_osm:
    input:
        os.path.join(config['dirs']['raw_data'], config['roads']['osm']['raw']),
        os.path.join(config['dirs']['schemas'], config['roads']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['roads']['osm']['processed'])
    shell:
        "transform_roads_osm {input} {output}"


# Obtain internal boundary lines from Admin polygons (Transform)
rule transform_internal_boundaries:
    input:
        os.path.join(config['dirs']['processed_data']),
        os.path.join(config['dirs']['schemas'], config['internalBnd']['schema']),
    params:
        config['constants']['ISO3'],
        config['supplier']
    shell:
        "transform_internal_boundaries {input} {output}"

# Transform SRTM -> make hillshade
# still not sure how to employ (optional) keyword arguments into snakemake
rule transform_srtm30_hsh_basic:
    input:
        os.path.join(config['dirs']['processed_data'], config['srtm']['srtm30']['processed'])
    params:
        config['constants']['altitude_light_deg'],
        config['constants']['azimuth_light_deg']
    output:
        input_dem_uri = os.path.join(config['dirs']['processed_data'], config['srtm']['srtm30']['basichillshade'])
    shell:
        "transform_srtm30_hsh_basic \"{output}\" \"{input}\"  {params}"

rule transform_srtm30_hsh_pretty:
    input:
        os.path.join(config['dirs']['processed_data'], config['srtm']['srtm30']['processed'])
    params:
        config['constants']['altitude_light_deg'],
        config['constants']['azimuth_light_deg']
    output:
        input_dem_uri = os.path.join(config['dirs']['processed_data'], config['srtm']['srtm30']['prettyhillshade'])
    shell:
        "transform_srtm30_hsh_pretty \"{output}\" \"{input}\"  {params}"

rule transform_srtm90_hsh_basic:
    input:
        os.path.join(config['dirs']['processed_data'], config['srtm']['srtm90']['processed'])
    params:
        config['constants']['altitude_light_deg'],
        config['constants']['azimuth_light_deg']
    output:
        input_dem_uri = os.path.join(config['dirs']['processed_data'], config['srtm']['srtm90']['basichillshade'])
    shell:
        "transform_srtm90_hsh_basic \"{output}\" \"{input}\"  {params}"

rule transform_srtm90_hsh_pretty:
    input:
        os.path.join(config['dirs']['processed_data'], config['srtm']['srtm90']['processed'])
    params:
        config['constants']['altitude_light_deg'],
        config['constants']['azimuth_light_deg']
    output:
        input_dem_uri = os.path.join(config['dirs']['processed_data'], config['srtm']['srtm90']['prettyhillshade'])
    shell:
        "transform_srtm90_hsh_pretty \"{output}\" \"{input}\" {params}"

