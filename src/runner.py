# Change to correct directory in case we aren't already there
import os
os.chdir('/Users/tomharrison/Documents/Projects/UV_exposure')


# import relevant packages
import constants # a file where API keys are stored
import math
import pandas as pd
import pytz
import time
import warnings

from datetime import datetime, timedelta, timezone
from geopy.geocoders import Nominatim
from src import parse_args
from utils.UV_exposure import *
from utils.UV_exposure import get_times


def runner(args):
    # Find local time and the corresponding UTC time
    args.time, utc_time = get_times(
        lat = args.latitude,
        long = args.longitude,
        time = args.time
    )
    
    time_ = args.time
    
    if time.daylight:
        args.time = args.time - timedelta(hours = 1)

    # Find the current UTC datetime. We will use it for extracting ozone data, calculating the Earth-Sun distance, and more
    day_of_year = utc_time.timetuple().tm_yday
    
    # NASA website takes ~2 days to update. Therefore we find the ozone data for 2 days prior to the current date
    if args.current:
        ozone.get_ozone_data(utc_time - timedelta(days=2))
        df_ozone = ozone.clean_ozone_data(utc_time - timedelta(days=2))
    elif args.time:
        utc = pytz.UTC
        if utc.localize(args.time - timedelta(days=2)) > datetime.now(timezone.utc):
            warnings.warn("It is not possible to use future ozone forecasts so the most recent ozone data is being used.")
            utc_time = datetime.now(timezone.utc) - timedelta(days=3)
        
        ozone.get_ozone_data(utc_time)
        df_ozone = ozone.clean_ozone_data(utc_time)
    
    # Find the thickness of the ozone layer at the location of interest
    ozone_thickness = ozone.get_ozone_thickness(
        df_ozone = df_ozone, 
        lat = args.latitude, 
        long = args.longitude
    )
    
    # Find the solar zenith angle at the location and time given
    zenith = incident_UV.zenith_angle(
        lat = args.latitude, 
        long = args.longitude, 
        local_time = args.time, 
        utc_time = utc_time
    )

    # Find the cleay-sky UV index at the specified location and time
    clear_sky_UVI = incident_UV.clear_sky_UVI(
        utc_day = day_of_year, 
        zenith = zenith, 
        tot_ozone = ozone_thickness
    )

    print('\nIn {} on {} at {}: \nClear-sky UV index = {}\n'.format(args.location, time_.strftime("%d/%m/%Y"), time_.strftime("%H:%M"), round(clear_sky_UVI, 2)))
    
    if args.current:
        # Find the cloud modification factor based on weather
        cmf = cloud_cover.get_cloud_mod_factor(
            lat = args.latitude, 
            long = args.longitude,
            api_key = constants.weatherstack_api_key
        )
    
        real_UVI = cmf * clear_sky_UVI
        print('Real UV Index = {}\n'.format(round(real_UVI, 2)))
    elif args.time:
        warnings.warn("There is currently no support for historical weather data, so the real UV index cannot be calculated.")
    
    return 0



if __name__ == "__main__":

    args = parse_args()
    
    # Find the coordinates of the specified location using geolocator
    geolocator = Nominatim(timeout=10, user_agent="PDS")
    location_full = geolocator.geocode(args.location)
    
    # Store latitude and longitude in the argparser
    args.latitude, args.longitude = location_full.latitude, location_full.longitude
        
    # If the user wants the current time, set time = None
    # If the user wants a particular time, then convert the supplied string to a datetime object
    if args.current:
        args.time = None
    elif args.time:
        args.time = datetime.strptime(args.time, '%d/%m/%y %H:%M')
    
    # Convert start and end times to datetime objects
    if args.start_time or args.end_time:
        try:
            args.start_time = datetime.strptime(args.start_time, '%d/%m/%y %H:%M')
            args.end_time = datetime.strptime(args.end_time, '%d/%m/%y %H:%M')
        except TypeError as exc:
            raise Exception('Both the start time and end time have to be specified together.') from exc
                    
    # Call the runner
    runner(args)
