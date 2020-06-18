import os
import logging
import numpy as np
import geopandas as gpd

logger = logging.getLogger(__name__)


###############################################################################
def get_srtm30_root_url():
    """
    The root url to download SRTM 30m zip files from
    :return:
    """
    srtm30_url = 'http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/'
    return srtm30_url


###############################################################################
def get_srtm90_root_url():
    """
    The root url to download SRTM 90m zip files from
    :return:
    """
    srtm90_url = 'http://srtm.csi.cgiar.org/' + \
                 'wp-content/uploads/files/srtm_5x5/TIFF/'
    return srtm90_url


###############################################################################
def longitude_to_srtm90_grid_long(longitude):
    """
    Determine longitudes within SRTM 5-degree grid
    SRTM longitude is 72 divisions
    Grid starts from 01 at 180E (Pacific Date Line)
    """
    return int(1 + (180 + longitude - (longitude % 5.)) / 5)


###############################################################################
def latitude_to_srtm90_grid_lat(latitude):
    """
    Determine latitudes within SRTM 5-degree grid
    SRTM latitude is 24 divisions starting at 01 from 55N to 60S
    (using 60N as zero index)
    """
    return int((60 - (latitude - (latitude % 5.)))/5)


###############################################################################
def longitude_to_srtm30_text_long(longitude):
    """
    Determine longitudes within SRTM 1-degree grid
    EW Meridian is E000 and tiles indexed by western-most coordinate
    """

    flong = np.floor(longitude)
    if flong < 0.:
        tlong = "W%03d" % (abs(flong))
    else:
        tlong = "E%03d" % (abs(flong))

    return tlong


###############################################################################
def latitude_to_srtm30_text_lat(latitude):
    """
    Determine latitudes within SRTM 1-degree grid
    NS Equator is N00 and tiles indexed by southern-most coordinate
    """

    flat = np.floor(latitude)
    if flat < 0.:
        tlat = "S%02d" % (abs(flat))
    else:
        tlat = "N%02d" % (abs(flat))

    return tlat


###############################################################################
def get_country_bounds(country_gpkg=None):
    """
    :param country_gpkg: geopackage of country border
    :return: bounds of country outline
    N.B. adding this as separate module to allow insertion of tests
    """

    if country_gpkg is None:
        # TODO: have some error behaviour when no file supplied
        logger.info("Defaulting to Yemen")
        country_bnd = np.array([41.81458282, 12.10819435,
                                54.53541565, 18.99999809])
    else:
        country = gpd.read_file(country_gpkg)
        assert country.crs == {'init': 'epsg:4326'}, \
            "Country outline is not in EPSG 4326 (WGS84)"
        country_bnd = country.total_bounds

    return country_bnd


###############################################################################
def determine_srtm_90_zip(country_gpkg=None):
    """
    SRTM is stored in 5x5 degree grids, this script determines which zip
    files to download to cover the country
    """
    country_bnd = get_country_bounds(country_gpkg=country_gpkg)

    # TODO: Not dealt with countries that cross 180E/W longitude
    tru_long = [country_bnd[0], country_bnd[2]]
    tru_lat = [country_bnd[1], country_bnd[3]]

    # determine max / min lats longs 5 degree grid origins
    grid_long = list(range(longitude_to_srtm90_grid_long(min(tru_long)),
                           longitude_to_srtm90_grid_long(max(tru_long)) + 1))
    # NOTE: grid latitude increases with more southerly latitude
    grid_lat = list(range(latitude_to_srtm90_grid_lat(max(tru_lat)),
                          latitude_to_srtm90_grid_lat(min(tru_lat)) + 1))

    # TODO: check tile coincides with country outline
    for glon in grid_long:
        for glat in grid_lat:
            gcoord = '%02d_%02d' % (glon, glat)
            yield 'srtm_' + gcoord + '.zip'


###############################################################################
def determine_srtm_30_zip(country_gpkg=None):
    """
    Determine longitudes within SRTM 1-degree grid
    More straightforward than SRTM 90!
    """
    country_bnd = get_country_bounds(country_gpkg=country_gpkg)

    # TODO: Not dealt with countries that cross 180E/W longitude
    tru_long = [country_bnd[0], country_bnd[2]]
    tru_lat = [country_bnd[1], country_bnd[3]]

    # TODO: check tile coincides with country outline
    for glon in list(range(min(tru_long), max(tru_long))):
        for glat in list(range(min(tru_lat), max(tru_lat))):
            gcoord = latitude_to_srtm30_text_lat(glat) + \
                     longitude_to_srtm30_text_long(glon)
            yield '.'.join([gcoord, 'SRTMGL1', 'hgt', 'zip'])