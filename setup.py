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
            'extract_adm0_cod=extract.cod:get_adm0',
            'extract_adm0_gadm=extract.gadm:get_adm0',
        ]
    }
)