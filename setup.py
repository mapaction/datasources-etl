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
            'extract_rivers_cod=extract.cod:get_rivers_snakemake',
            'extract_seaports_cod=extract.cod:get_seaports_snakemake',
            'extract_global_seaports_cod=extract.cod:get_global_seaports_snakemake',
            'extract_srtm30=extract.srtm:get_srtm30_snakemake',
            'extract_srtm90=extract.srtm:get_srtm90_snakemake',
            'extract_world_gadm=extract.gadm:get_world',
            'extract_geoboundaries=extract.geoboundaries:get_geoboundaries_adm',
            'extract_geoboundaries_adm0_all=extract.geoboundaries:get_all_adm0',
            'extract_ourairports=extract.ourairports:get_our_airports',
            'transform_adm0_cod=transform.adm0:transform_cod',
            'transform_adm1_cod=transform.adm1:transform_cod',
            'transform_adm2_cod=transform.adm2:transform_cod',
            'transform_adm3_cod=transform.adm3:transform_cod',
            'transform_rivers_cod=transform.rivers:transform_cod',
            'transform_seaports_cod=transform.seaports:transform_cod',
            'transform_adm0_gadm=transform.adm0:transform_gadm',
            'transform_adm1_gadm=transform.adm1:transform_gadm',
            'transform_adm2_gadm=transform.adm2:transform_gadm',
            'transform_gadm_adm=transform.adm_gadm:transform_gadm',
            'transform_surrounding_gadm=transform.adm0_surround:transform',
            'transform_adm0_geoboundaries=transform.adm0:transform_geoboundaries',
            'transform_adm1_geoboundaries=transform.adm1:transform_geoboundaries',
            'transform_adm2_geoboundaries=transform.adm2:transform_geoboundaries',
            'transform_surrounding_geoboundaries=transform.adm0_surround:transform_geoboundaries',
            'transform_internal_boundaries=transform.adm_lines:adm_to_line_handler',
            'extract_osm=extract.osm_overpass:extract_osm_query',
            # Roads
            'extract_roads_cod=extract.cod:get_roads_snakemake',
            'transform_roads_cod=transform.roads:transform_cod',
        ]
    }
)
