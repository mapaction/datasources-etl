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
            'transform_adm0_cod=transform.adm0:transform_cod',
            'transform_adm0_gadm=transform.adm0:transform_gadm',
        ]
    }
)
