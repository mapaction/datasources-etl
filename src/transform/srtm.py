import os
import sys
import logging
import rasterio

logger = logging.getLogger(__name__)


###############################################################################
def calculate_slope(input_dem_uri, output_slope_uri):


    with rasterio.open(input_dem_uri, 'r') as raster_in:
        demdata = raster_in.read(1)
        demmeta = raster_in.meta

    # slope calculation is simply a steepness measure of the
