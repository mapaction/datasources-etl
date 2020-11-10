import os
import sys
import numpy as np
import logging
import scipy.ndimage as ndimage
import rasterio


logger = logging.getLogger(__name__)


# Hill shading is determine by a combination of the slope (steepness) and the
# slope direction -> using http://people.csail.mit.edu/bkph/papers/Hill-Shading.pdf


###############################################################################
def calculate_slope_aspect_NE(northing, easting):

    slope = np.arctan(easting / northing)
    # slope direction is simply taken from the angle between the ew and ns slopes
    # but atan only extends to +/- 90 degrees so cardinal direction determined by
    # whether slope faces north or south
    if northing == 0:
        if easting < 0.:
            slope = np.pi /4.
        else:
            slope = 3. * np.pi / 4.
    elif northing > 0.:
        if slope < 0.:
            slope += 2*np.pi
    else:
        slope += np.pi
    return slope


###############################################################################
def calculate_NE_slope_9by9(arr, xy_resolution):
    """
    Calculate a slope of a central point in a 9x9 matrix
    using a weighted average of central difference
    """

    if np.shape(arr) != (9, 9):
        raise ValueError('Input matrix should be 9x9')

    # we = west-east; ns = north-south; kept in this orientation for
    # consistency (note that numpy arranges arrays increasing
    # left to right (west to east)), but bottom to top (south to north)
    # positive we is going _downhill_ towards east (east facing slope)
    # positive sn is going _downhill_ towards north (north facing slope)
    unit_slope_we = (arr[2, 2] + (2*arr[1, 2]) + arr[0, 2]) \
                     - (arr[2, 0] + (2*arr[1, 0]) + arr[0, 0])
    unit_slope_sn = (arr[2, 2] + (2*arr[2, 1]) + arr[2, 0]) \
                     - (arr[0, 2] + (2*arr[0, 1]) + arr[0, 0])

    slope_we = unit_slope_we / (8 * xy_resolution)
    slope_sn = unit_slope_sn / (8 * xy_resolution)

    return slope_we, slope_sn


###############################################################################
def calculate_slope_magnitude_9by9(arr, xy_resolution=1):

    slope_we, slope_sn = calculate_NE_slope_9by9(arr, xy_resolution)
    slope_magnitude = np.sqrt(slope_we**2 + slope_sn**2)
    return slope_magnitude


###############################################################################
def calculate_slope_direction_9by9(arr, xy_resolution=1):

    slope_we, slope_sn = calculate_NE_slope_9by9(arr, xy_resolution)
    slope_direction = calculate_slope_aspect_NE(slope_sn, slope_we)
    return slope_direction


###############################################################################
def calculate_slope_angle(input_dem_uri):
    """
    Uses scipy's generic image filter to apply slope calculation across an image
    efficiently, then calculate slope angle. See
    docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generic_filter.html
    :param input_dem_uri:
    :param output_slope_mag_uri:
    :return:
    """
    with rasterio.open(input_dem_uri, 'r') as raster_in:
        demdata = raster_in.read(1)
        demmeta = raster_in.meta

    slope_mag = demdata.copy()
    slope_mag[:] = demmeta['nodata']

    extra_keywords = {"xy_resolution": abs(demmeta['transform'][0])}
    ndimage.generic_filter(demdata, calculate_slope_magnitude_9by9,
                           size=(3, 3), output=slope_mag, mode='nearest',
                           extra_keywords=extra_keywords)

    slope_angle = np.atan(slope_mag)
    return slope_angle


###############################################################################
def calculate_slope_aspect(input_dem_uri):
    """
    Uses scipy's generic image filter to apply slope direction across an image
    efficiently, then calculae the aspect See
    :param input_dem_uri:
    :param output_slope_dir_uri:
    :return:
    """
    with rasterio.open(input_dem_uri, 'r') as raster_in:
        demdata = raster_in.read(1)
        demmeta = raster_in.meta

    aspect = demdata.copy()
    aspect[:] = demmeta['nodata']

    extra_keywords = {"xy_resolution": abs(demmeta['transform'][0])}
    ndimage.generic_filter(demdata, calculate_slope_direction_9by9,
                           size=(3, 3), output=aspect, mode='nearest',
                           extra_keywords=extra_keywords)
    return aspect


###############################################################################
def calculate_basic_hillshade(aspect_array, slope_array,
                              altitude_deg=45., azimuth_deg=315.):

    # 1) altitude in degrees -> zenith angle in radians
    zenith_rad = (90. - altitude_deg) * np.pi/180.

    # 2) azimuth in radians and check the
    azimuth_rad = (360.0 - azimuth_deg + 90) % 360

    hillshade = 255.0 * ((np.cos(zenith_rad) * np.cos(slope_array)) +
                         (np.sin(zenith_rad) * np.sin(slope_array)
                          * np.cos(azimuth_rad - aspect_array)))
    return hillshade


###############################################################################
def get_basic_hillshade(output_hillshade_uri, input_dem_uri,
                        altitude_deg=45., azimuth_deg=315.,
                        save_temp_files=True,
                        overwrite_temp_files=False):

    # Set up file naming conventions
    input_dem_basename = os.path.basename(input_dem_uri)
    working_dir = os.path.dirname(output_hillshade_uri) + os.sep \
                  + 'hillshade_working'
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    with rasterio.open(input_dem_uri, 'r') as input_r:
        inputmeta = input_r.meta

    temp_aspect_uri = working_dir + os.sep + \
                      '_aspect'.join(os.path.splitext(input_dem_basename))
    temp_slope_uri = working_dir + os.sep + \
                     '_slopeangle'.join(os.path.splitext(input_dem_basename))

    # See if the data has already been saved to default temp sub-folder
    if not os.path.exists(temp_aspect_uri):
        aspect = calculate_slope_aspect(input_dem_uri)
    else:
        with rasterio.open(temp_aspect_uri, 'r') as tempas:
            aspect = tempas.read(1)
    if not os.path.exists(temp_slope_uri):
        slope_angle = calculate_slope_angle(input_dem_uri)
    else:
        with rasterio.open(temp_slope_uri, 'r') as tempsl:
            slope_angle = tempsl.read(1)

    # save data if requested
    if save_temp_files:
        if overwrite_temp_files or not os.path.exists(temp_aspect_uri):
            with rasterio.open(temp_aspect_uri, 'w', **inputmeta) as handle:
                handle.write_band(1, aspect)
        if overwrite_temp_files or not os.path.exists(temp_slope_uri):
            with rasterio.open(temp_slope_uri, 'w', **inputmeta) as handle:
                handle.write_band(1, slope_angle)

    hillshade = calculate_basic_hillshade(aspect, slope_angle,
                                          altitude_deg=altitude_deg,
                                          azimuth_deg=azimuth_deg)

    with rasterio.open(output_hillshade_uri, 'w', **inputmeta) as outraster:
        outraster.write_band(1, hillshade)


###############################################################################





