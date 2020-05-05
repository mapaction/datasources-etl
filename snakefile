import os

configfile: "config.yml"

##COD
##Extract COD
##TODO extract only admin 0 layers
rule extract_adm0_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm0']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_adm0_cod {params} {output}"

##TODO extract only admin 1 layers
rule extract_adm1_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm1']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_adm1_cod {params} {output}"

##TODO extract only admin 2 layers
rule extract_adm2_cod:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm2']['cod']['raw'])
    params:
        raw_dir=config['dirs']['raw_data']
    shell:
        "extract_adm2_cod {params} {output}"

##Extract GADM
rule extract_adm0_gadm:
    output:
        os.path.join(config['dirs']['raw_data'], config['adm0']['gadm']['raw'])
    params:
        url=config['adm0']['gadm']['url']
    shell:
        "curl {params} -o {output} -O -J -L"

##Transform COD
rule transform_adm0_cod:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm0']['cod']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm0']['cod']['processed'])
    shell:
        "transform_adm0_cod {input} {output}"

##GADM
##Transform GADM
rule transform_adm0_gadm:
    input:
        os.path.join(config['dirs']['raw_data'], config['adm0']['gadm']['raw']),
        os.path.join(config['dirs']['schemas'], config['adm0']['schema'])
    output:
        os.path.join(config['dirs']['processed_data'], config['adm0']['gadm']['processed'])
    shell:
        "transform_adm0_gadm {input} {output}"
