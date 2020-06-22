import setuptools

setuptools.setup(
    name='datasources-etl',
    url="mapaction/datasources-etl",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    setup_requires=[],
    tests_require=[],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'extract_adm0_cod=extract.cod:get_adm0_snakemake',
            'extract_adm1_cod=extract.cod:get_adm1_snakemake',
            'extract_adm2_cod=extract.cod:get_adm2_snakemake',
            'extract_adm3_cod=extract.cod:get_adm3_snakemake',
            'extract_world_gadm=extract.gadm:get_world',
            'extract_geoboundaries=extract.geoboundaries:get_geoboundaries_adm',

            'transform_adm0_cod=transform.adm0:transform_cod',
            'transform_adm1_cod=transform.adm1:transform_cod',
            'transform_adm2_cod=transform.adm2:transform_cod',
            'transform_adm3_cod=transform.adm3:transform_cod',
            'transform_adm0_gadm=transform.adm0:transform_gadm',
            'transform_adm1_gadm=transform.adm1:transform_gadm',
            'transform_adm2_gadm=transform.adm2:transform_gadm',
            'transform_surrounding_gadm=transform.adm0_surround:transform',
            'transform_adm0_geoboundaries=transform.adm0:transform_geoboundaries',
            'transform_adm1_geoboundaries=transform.adm1:transform_geoboundaries',
            'transform_adm2_geoboundaries=transform.adm2:transform_geoboundaries'
        ]
    }
)
