import os
import sys
import numpy as np
import logging
import scipy
import scipy.ndimage as ndimage
import rasterio
import numba
from numba import njit
# from numba import cfunc, carray
# from numba.core.types import intc, CPointer, float64, intp, voidptr
# from scipy import LowLevelCallable

logger = logging.getLogger(__name__)
# Hill shading is determine by a combination of the slope (steepness) and the
# slope direction -> using http://people.csail.mit.edu/bkph/papers/Hill-Shading.pdf


###############################################################################
# def jit_filter_function(filter_function):
#     """
#     Decorator for use with scipy.ndimage.generic_filter.
#     Pinched from https://ilovesymposia.com/2017/03/15/
#         prettier-lowlevelcallables-with-numba-jit-and-decorators/
#     """
#     jitted_function = numba.jit(filter_function, nopython=True)
#
#     @cfunc(intc(CPointer(float64), intp, CPointer(float64), voidptr))
#     def wrapped(values_ptr, len_values, result, data):
#         values = carray(values_ptr, (len_values,), dtype=float64)
#         result[0] = jitted_function(values)
#         return 1
#     return LowLevelCallable(wrapped.ctypes)


###############################################################################
def set_working_directory(path_to_output_file):
    """
    Basically make a subdirectory where the output file is located with the
    working files needed to construct a given hillshade.
    :param path_to_output_file: path to the output file
    :return:
    """
    working_dir = os.path.dirname(path_to_output_file) + os.sep \
                  + 'hillshade_working'
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    return working_dir


###############################################################################
def calculate_slope_aspect_NE(northing, easting):
    """
    DEPRECATED -> unwrapped into calculate_slope_aspect_3by3()
    :param northing:
    :param easting:
    :return:
    """

    slope = np.arctan2(easting / northing)
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
def calculate_NE_slope_3by3(arr, xy_resolution):
    """
    DEPRECATED -> unwrapped into calculate_slope_magnitude_3by3()
        and calculate_slope_aspect_3by3()
    Calculate a slope of a central point in a 3x3 matrix
    using a weighted average of central difference
    """

    if np.shape(arr) != (3, 3):
        err_msg = 'Input matrix should be 3x3'
        logger.error(err_msg)
        raise ValueError(err_msg)

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
@njit()
def calculate_slope_magnitude_3by3(arr, xy_resolution=1):

    unit_slope_we = (arr[2, 2] + (2*arr[1, 2]) + arr[0, 2]) - (arr[2, 0] + (2*arr[1, 0]) + arr[0, 0])
    unit_slope_sn = (arr[2, 2] + (2*arr[2, 1]) + arr[2, 0]) - (arr[0, 2] + (2*arr[0, 1]) + arr[0, 0])

    slope_we = unit_slope_we / (8 * xy_resolution)
    slope_sn = unit_slope_sn / (8 * xy_resolution)

#    slope_we, slope_sn = calculate_NE_slope_3by3(arr, xy_resolution)

    slope_magnitude = np.sqrt(slope_we**2 + slope_sn**2)
    return slope_magnitude


###############################################################################
@njit()
def calculate_slope_aspect_3by3(arr, xy_resolution=1):

    # slope_we, slope_sn = calculate_NE_slope_3by3(arr, xy_resolution)
    # slope_direction = calculate_slope_aspect_NE(slope_sn, slope_we)
    # return slope_direction

    unit_slope_we = (arr[2, 2] + (2*arr[1, 2]) + arr[0, 2]) \
                     - (arr[2, 0] + (2*arr[1, 0]) + arr[0, 0])
    unit_slope_sn = (arr[2, 2] + (2*arr[2, 1]) + arr[2, 0]) \
                     - (arr[0, 2] + (2*arr[0, 1]) + arr[0, 0])

    slope_we = unit_slope_we / (8 * xy_resolution)
    slope_sn = unit_slope_sn / (8 * xy_resolution)

    slope = np.arctan2(slope_we / slope_sn)
    # slope direction is simply taken from the angle between the ew and ns slopes
    # but atan only extends to +/- 90 degrees so cardinal direction determined by
    # whether slope faces north or south
    if slope_sn == 0:
        if slope_we < 0.:
            slope = np.pi /4.
        else:
            slope = 3. * np.pi / 4.
    elif slope_sn > 0.:
        if slope < 0.:
            slope += 2*np.pi
    else:
        slope += np.pi
    return slopesrtm.py


###############################################################################
@njit()
def calculate_curvature_3by3(arr, xy_resolution=1):
    """
    This works as a bilinear interpolation of the second-order terms of
    a 9x9 surface described by a fourth-order polynomial surface
    (see http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//00q90000000t000000)
    akin to an osculating circle
    :param arr: 9x9 array of either slope steepness or aspect (in radians)
    :param xy_resolution: resolution of the raster in metres.
    :return:
    """
    horizontal = ((arr[1,2] + arr[1,0])/2 - arr[1,1]) / (xy_resolution**2)
    vertical = ((arr[2,1] + arr[0,1])/2 - arr[1,1]) / (xy_resolution**2)

    curvature = -2*(horizontal + vertical) * 100

    return curvature


###############################################################################
def calculate_slope_angle(dem_raster, xy_resolution=1):
    """
    Uses scipy's generic image filter to apply slope calculation across an image
    efficiently, then calculate slope angle. See
    docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.generic_filter.html
    :param dem_raster:
    :param xy_resolution:
    :return:
    """
    slope_mag = dem_raster.copy()
    slope_mag[:] = 0.

    extra_keywords = {"xy_resolution": xy_resolution}
    ndimage.generic_filter(dem_raster, calculate_slope_magnitude_3by3,
                           size=(3, 3), output=slope_mag, mode='nearest',
                           extra_keywords=extra_keywords)

    slope_angle = np.arctan(slope_mag)
    return slope_angle


###############################################################################
def calculate_slope_aspect(dem_raster, xy_resolution=1):
    """
    Uses scipy's generic image filter to apply slope direction across an image
    efficiently, then calculae the aspect See
    :param dem_raster:
    :param xy_resolution:
    :return:
    """
    aspect = dem_raster.copy()
    aspect[:] = 0.

    extra_keywords = {"xy_resolution": xy_resolution}
    ndimage.generic_filter(dem_raster, calculate_slope_aspect_3by3,
                           size=(3, 3), output=aspect, mode='nearest',
                           extra_keywords=extra_keywords)
    return aspect


###############################################################################
def calculate_basic_hillshade(aspect_array, slope_array,
                              altitude_deg=45., azimuth_deg=315.):
    """
    Calculates a basic hillshade based on
    :param aspect_array:
    :param slope_array:
    :param altitude_deg:
    :param azimuth_deg:
    :return:
    """

    # 1) altitude in degrees -> zenith angle in radians
    zenith_rad = (90. - altitude_deg) * np.pi/180.

    # 2) azimuth in radians and check the
    azimuth_rad = (360.0 - azimuth_deg + 90) % 360

    hillshade = 255.0 * ((np.cos(zenith_rad) * np.cos(slope_array)) +
                         (np.sin(zenith_rad) * np.sin(slope_array)
                          * np.cos(azimuth_rad - aspect_array)))
    return hillshade


###############################################################################
def get_slope_angle(input_dem_uri, working_dir, save_temp_files=True,
                    overwrite_temp_files=False):

    # Set up file naming conventions
    input_dem_basename = os.path.basename(input_dem_uri)
    temp_slope_uri = working_dir + os.sep + \
                     '_slopeangle'.join(os.path.splitext(input_dem_basename))

    # See if the data has already been saved to default temp sub-folder
    if not os.path.exists(temp_slope_uri):
        logger.info("Creating slope raster")
        with rasterio.open(input_dem_uri, 'r') as raster_in:
            inputdata = raster_in.read(1)
            inputmeta = raster_in.meta
        xy_resolution = abs(inputmeta['transform'][0])
        slope_angle = \
            calculate_slope_angle(inputdata, xy_resolution=xy_resolution)
    else:
        with rasterio.open(temp_slope_uri, 'r') as tempsl:
            slope_angle = tempsl.read(1)
            inputmeta = tempsl.meta

    # save data if requested
    if overwrite_temp_files or save_temp_files:
        if overwrite_temp_files or not os.path.exists(temp_slope_uri):
            logger.info("Saving slope raster: %s" % temp_slope_uri)
            with rasterio.open(temp_slope_uri, 'w', **inputmeta) as handle:
                handle.write_band(1, slope_angle)

    return slope_angle


###############################################################################
def get_slope_aspect(input_dem_uri, working_dir, save_temp_files=True,
                     overwrite_temp_files=False):

    # Set up file naming conventions
    input_dem_basename = os.path.basename(input_dem_uri)
    temp_aspect_uri = working_dir + os.sep + \
                      '_aspect'.join(os.path.splitext(input_dem_basename))

    # See if the data has already been saved to default temp sub-folder
    if not os.path.exists(temp_aspect_uri):
        logger.info("Creating aspect raster")
        with rasterio.open(input_dem_uri, 'r') as raster_in:
            inputdata = raster_in.read(1)
            inputmeta = raster_in.meta
        xy_resolution = abs(inputmeta['transform'][0])
        aspect = \
            calculate_slope_aspect(inputdata, xy_resolution=xy_resolution)
    else:
        with rasterio.open(temp_aspect_uri, 'r') as tempas:
            aspect = tempas.read(1)
            inputmeta = tempas.meta

    if overwrite_temp_files or save_temp_files:
        if overwrite_temp_files or not os.path.exists(temp_aspect_uri):
            logger.info("Saving aspect raster: %s" % temp_aspect_uri)
            with rasterio.open(temp_aspect_uri, 'w', **inputmeta) as handle:
                handle.write_band(1, aspect)

    return aspect


###############################################################################
def get_basic_hillshade(output_hillshade_uri, input_dem_uri,
                        altitude_deg=45., azimuth_deg=315.,
                        save_temp_files=True,
                        overwrite_temp_files=False):

    # Set up file naming conventions
    working_dir = set_working_directory(output_hillshade_uri)

    # Get slope angle and aspect
    aspect = get_slope_aspect(input_dem_uri, working_dir,
                              save_temp_files=save_temp_files,
                              overwrite_temp_files=overwrite_temp_files)
    slope_angle = get_slope_angle(input_dem_uri, working_dir,
                                  save_temp_files=save_temp_files,
                                  overwrite_temp_files=overwrite_temp_files)

    # Calculate hillshade
    logger.info("Creating basic hillshade raster")
    hillshade = calculate_basic_hillshade(aspect, slope_angle,
                                          altitude_deg=altitude_deg,
                                          azimuth_deg=azimuth_deg)

    with rasterio.open(input_dem_uri, 'r') as input_r:
        inputmeta = input_r.meta

    logger.info("Saving basic hillshade raster: %s" % output_hillshade_uri)
    with rasterio.open(output_hillshade_uri, 'w', **inputmeta) as outraster:
        outraster.write_band(1, hillshade)


###############################################################################
def calculate_profile_curvature(slope_angle, xy_resolution=1):
    """
    Nice explanation of curvature here:
    https://www.esri.com/arcgis-blog/products/product/imagery/understanding-curvature-rasters/
    This function calculates the profile curvature of slopes. i.e., the rate
    of change of slope magnitude.
    :param slope_angle: the steepness of the slope in radians
    :param xy_resolution: the length of one dimension of a given raster cell
    :return:
    """
    profile_curvature = slope_angle.copy()
    profile_curvature[:] = 0.
    extra_keywords = {"xy_resolution": xy_resolution}

    ndimage.generic_filter(slope_angle, calculate_curvature_3by3, size=(3, 3),
                           output=profile_curvature, mode='nearest',
                           extra_keywords=extra_keywords)

    return profile_curvature


###############################################################################
def calculate_planform_curvature(slope_aspect, xy_resolution=1):
    """
    Nice explanation of curvature here:
    https://www.esri.com/arcgis-blog/products/product/imagery/understanding-curvature-rasters/
    This function calculates the planform curvature of slopes. i.e., the rate
    of change of slope aspect.
    :param slope_aspect:
    :param xy_resolution: the length of one dimension of a given raster cell
    :return:
    """
    planform_curvature = slope_aspect.copy()
    planform_curvature[:] = 0.
    extra_keywords = {"xy_resolution": xy_resolution}

    ndimage.generic_filter(slope_aspect, calculate_curvature_3by3, size=(3, 3),
                           output=planform_curvature, mode='nearest',
                           extra_keywords=extra_keywords)

    return planform_curvature


###############################################################################
def get_profile_curvature(input_dem_uri, working_dir, save_temp_files=True,
                          overwrite_temp_files=False):

    # Set up file naming conventions
    input_dem_basename = os.path.basename(input_dem_uri)
    temp_profcurve_uri = working_dir + os.sep + \
        '_profilecurvature'.join(os.path.splitext(input_dem_basename))

    with rasterio.open(input_dem_uri, 'r') as input_r:
        inputmeta = input_r.meta
    xy_resolution = abs(inputmeta['transform'][0])

    # See if the data has already been saved to default temp sub-folder
    if not os.path.exists(temp_profcurve_uri):
        logger.info("Creating profile curvature raster")
        slope_angle = get_slope_angle(input_dem_uri, working_dir,
                                      save_temp_files=save_temp_files,
                                      overwrite_temp_files=overwrite_temp_files)
        profile_curvature = \
            calculate_profile_curvature(slope_angle, xy_resolution=xy_resolution)
    else:
        with rasterio.open(temp_profcurve_uri, 'r') as tempas:
            profile_curvature = tempas.read(1)

    if overwrite_temp_files or save_temp_files:
        if overwrite_temp_files or not os.path.exists(temp_profcurve_uri):
            logger.info("Saving profile curvature raster: %s" % temp_profcurve_uri)
            with rasterio.open(temp_profcurve_uri, 'w', **inputmeta) as handle:
                handle.write_band(1, profile_curvature)

    return profile_curvature


###############################################################################
def get_planform_curvature(input_dem_uri, working_dir, save_temp_files=True,
                           overwrite_temp_files=False):

    # Set up file naming conventions
    input_dem_basename = os.path.basename(input_dem_uri)
    temp_plancurve_uri = working_dir + os.sep + \
        '_planformcurvature'.join(os.path.splitext(input_dem_basename))

    with rasterio.open(input_dem_uri, 'r') as input_r:
        inputmeta = input_r.meta
    xy_resolution = abs(inputmeta['transform'][0])

    # See if the data has already been saved to default temp sub-folder
    if not os.path.exists(temp_plancurve_uri):
        logger.info("Creating planform curvature raster")
        slope_aspect = get_slope_angle(input_dem_uri, working_dir,
                                       save_temp_files=save_temp_files,
                                       overwrite_temp_files=overwrite_temp_files)
        planform_curvature = \
            calculate_planform_curvature(slope_aspect, xy_resolution=xy_resolution)
    else:
        with rasterio.open(temp_plancurve_uri, 'r') as tempas:
            planform_curvature = tempas.read(1)

    if overwrite_temp_files or save_temp_files:
        if overwrite_temp_files or not os.path.exists(temp_plancurve_uri):
            logger.info("Saving planform curvature raster: %s" % temp_plancurve_uri)
            with rasterio.open(temp_plancurve_uri, 'w', **inputmeta) as handle:
                handle.write_band(1, planform_curvature)

    return planform_curvature


###############################################################################
def get_curvature_hillshade(output_curveshade_uri, input_dem_uri,
                            altitude_deg=45., azimuth_deg=315.,
                            save_temp_files=True,
                            overwrite_temp_files=False):

    # Set up file naming conventions
    working_dir = set_working_directory(output_curveshade_uri)

    # Get slope angle and aspect
    aspect = get_slope_aspect(input_dem_uri, working_dir,
                              save_temp_files=save_temp_files,
                              overwrite_temp_files=overwrite_temp_files)
    slope_angle = get_slope_angle(input_dem_uri, working_dir,
                                  save_temp_files=save_temp_files,
                                  overwrite_temp_files=overwrite_temp_files)

    # Calculate hillshade
    hillshade = calculate_basic_hillshade(aspect, slope_angle,
                                          altitude_deg=altitude_deg,
                                          azimuth_deg=azimuth_deg)
    # Calculate curvature
    planform_curv = get_planform_curvature(input_dem_uri, working_dir,
                                           save_temp_files=save_temp_files,
                                           overwrite_temp_files=overwrite_temp_files)
    profile_curv = get_planform_curvature(input_dem_uri, working_dir,
                                          save_temp_files=save_temp_files,
                                          overwrite_temp_files=overwrite_temp_files)

    # rescale curvature to 0 - 255
    renorm_planform = 255. * abs(planform_curv) / max(abs(planform_curv))
    renorm_profile = 255. * abs(profile_curv) / max(abs(profile_curv))

    hillshade_curv = 0.2*(renorm_planform + renorm_profile) + 0.6*hillshade

    with rasterio.open(input_dem_uri, 'r') as input_r:
        inputmeta = input_r.meta
    with rasterio.open(output_curveshade_uri, 'w', **inputmeta) as outraster:
        outraster.write_band(1, hillshade_curv)


###############################################################################
def blur_raster(input_raster, pixel_radius=10):
    """
    Takes the mean of a circular aperture of some pixel radius
    of all pixels -> effectively blurring the whole raster.
    :param input_raster: a numpy array
    :param pixel_radius: radius to blur
    :return: blurred raster
    """

    dim_size = 1 + 2*pixel_radius
    footprint = np.zeros(dim_size, dim_size)
    distance = footprint.copy()
    for x in range(distance.shape[0]):
        dx = pixel_radius - x
        for y in range(distance.shape[1]):
            dy = pixel_radius - y
            distance[x,y] = np.sqrt(dx**2 + dy**2)
    footprint = np.where(distance <= pixel_radius, 1., 0.)

    output_raster = input_raster.copy()
    output_raster[:] = 0.

    ndimage.generic_filter(input_raster, scipy.stats.mean, footprint=footprint,
                           output=output_raster, mode='nearest')
    return output_raster


###############################################################################
def calculate_multiscale_hillshade(output_mshillshade_uri, input_dem_uri,
                                   altitude_deg=45., azimuth_deg=315.):
    """
    Saw this youtube: https://youtu.be/pFDLFldNj9c on how to hack ambient
    occlusion on hillshades and it looks boss. However, I'm sticking to
    grayscale so let's have a party and see if this works.
    The recipe seems to be:
        1) sandwich blurred DEMs to accentuate large scale features
        2) use blurred slopes as a fake directionless curvature indication
        3) use hillshade on blurred slopes to
    :param output_mshillshade_uri:
    :param input_dem_uri:
    :param altitude_deg:
    :param azimuth_deg:
    :return:
    """
    pathtomaindir = r'~/Documents/MapAction/SoftwareDevelopment/Ganymede'
    maindir = os.path.expanduser(pathtomaindir)
    output_mshillshade_uri = \
        os.path.join(maindir, 'data', 'YEM_SRTM30_EPSG2090_multishade.tif')
    input_dem_uri = os.path.join(maindir, 'data', 'YEM_SRTM30_SRTM2090.tif')
    output_mshillshade_uri = \
        os.path.join(maindir, 'data', 'YEM_SRTM90_multishade.tif')
    input_dem_uri = os.path.join(maindir, 'data', 'YEM_SRTM90.tif')
    altitude_deg = 45.
    azimuth_deg = 315.

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    pixel_blur = [10, 20, 50]
    # Set up file naming conventions
    working_dir = set_working_directory(output_mshillshade_uri)

    base_dem = []
    slope = []
    hillshade = []

    with rasterio.open(input_dem_uri, 'r') as indem:
        orig_dem = indem.read(1)
        base_dem.append(indem.read(1))
        base_meta = indem.meta

    #test
    # out_test = orig_dem.copy()
    # out_test[:] = 0
    # ndimage.generic_filter(orig_dem, np.mean, size=(3, 3), output=out_test, mode='nearest')

    xy_size = abs(base_meta['transform'][0])
    logger.info("Calculating aspect")
    aspect = calculate_slope_aspect(base_dem[0], xy_resolution=xy_size)
    logger.info("Calculating slope")
    slope_angle = calculate_slope_angle(base_dem[0], xy_resolution=xy_size)
    slope.append(slope_angle)
    logger.info("Calculating hillshade")
    hillshade.append(calculate_basic_hillshade(aspect, slope_angle,
                                               altitude_deg=altitude_deg,
                                               azimuth_deg=azimuth_deg))
    # Calculate hillshades for blurred DEMs
    for pxbl in pixel_blur:
        logger.info("Applying %d pixel radius blur to DEM" % pxbl)
        base_dem.append(blur_raster(base_dem[0], pixel_radius=pxbl))
        logger.info("\tCalculating aspect with %d pixel radius blur" % pxbl)
        aspect = calculate_slope_aspect(base_dem[-1], xy_resolution=xy_size)
        logger.info("\tCalculating slope with %d pixel radius blur" % pxbl)
        slope_angle = calculate_slope_angle(base_dem[-1], xy_resolution=xy_size)
        slope.append(slope_angle)
        logger.info("\tCalculating hillshade with %d pixel radius blur" % pxbl)
        hillshade.append(calculate_basic_hillshade(aspect, slope_angle,
                                                   altitude_deg=altitude_deg,
                                                   azimuth_deg=azimuth_deg))

    # add the hillshades up and then brighten them...

    # take hi res hillshade and use the bright end to brighten up/ white out
    # highlighted areas


    # with the slopes, need to invert values (want steepest areas to be darkest)
    # then average them together - the directionless gives a fake ambient
    # occlusion effect


    # now take hillshade of the slope at all resolutions.
    # We only really want the high end and low end to accent our final hillshade


    # finally, with original DEM, take the lower 50% of elevated areas and
    # proportionally darken





