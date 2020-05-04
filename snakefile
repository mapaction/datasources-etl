import os

configfile: "config.yml"


rule extract_adm0_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm0']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_adm0_cod {params} {output}"


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
            config['dirs']['raw_data'], config['surrounding']['gadm']['raw'])
    params:
        url=config['surrounding']['gadm']['url']
    shell:
        "extract_world_gadm {input} {output}"


rule transform_adm0_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm0']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm0']['cod']['processed'])
    shell:
        "transform_adm0_cod {input} {output}"


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
            config['dirs']['raw_data'], config['surrounding']['gadm']['raw']),
        os.path.join(
            config['dirs']['schemas'], config['surrounding']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['surrounding']['gadm']['processed'])
    shell:
        "transform_surrounding_gadm {input} {output}"

