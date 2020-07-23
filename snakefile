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
            config['dirs']['raw_data'], config['osm']['rivers']['raw'])
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
            config['dirs']['raw_data'], config['osm']['lakes']['raw'])
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
            config['dirs']['raw_data'], config['osm']['admin']['raw'])
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
            config['dirs']['raw_data'], config['osm']['roads']['raw'])
    shell:
        "extract_osm \"{params.url}\" \"{params.country}\" {input} {output}"

####

rule extract_geoboundaries_adm0_all:
    shell:
        "extract_geoboundaries_adm0_all"

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

rule extract_roads_osm:
    output:
        os.path.join(config['dirs']['raw_data'], config['roads']['osm']['raw'])
    params:
        url=config['roads']['osm']['url']
    shell:
        "wget \"{params}\" -O {output}"

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
