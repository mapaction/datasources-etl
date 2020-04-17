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


rule transform_adm0_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm0']['cod']['raw'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm0']['cod']['processed'])
    shell:
        "transform_adm0_cod {input} {output}"


rule transform_adm0_gadm:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm0']['gadm']['raw'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm0']['gadm']['processed'])
    shell:
        "transform_adm0_gadm {input} {output}"
