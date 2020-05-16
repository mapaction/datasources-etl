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

rule extract_roads_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['roads']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_roads_cod {params} {output}"

##Extract GADM
rule extract_adm0_gadm:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm0']['gadm']['raw'])
    params:
        url=config['adm0']['gadm']['url']
    shell:
        "curl {params} -o {output} -O -J -L"

rule extract_world_gadm:
    output:
        os.path.join(
            config['dirs']['raw_data'], config['surrounding']['gadm']['rawzip'])
    params:
        url=config['surrounding']['gadm']['url']
    shell:
        "extract_world_gadm {input} {output}"

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

rule transform_roads_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['roads']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['roads']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['roads']['cod']['processed'])
    shell:
        "transform_roads_cod {input} {output}"

##Transform GADM
rule transform_adm0_gadm:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm0']['gadm']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm0']['gadm']['processed'])
    shell:
        "transform_adm0_gadm {input} {output}"


rule transform_surrounding_gadm:
    input:
        os.path.join(
            config['dirs']['raw_data'], config['surrounding']['gadm']['rawzip']),
        os.path.join(
            config['dirs']['schemas'], config['surrounding']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['surrounding']['gadm']['processed'])
    shell:
        "transform_surrounding_gadm {input} {output}"

