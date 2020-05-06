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
