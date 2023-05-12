# Change to correct directory in case we aren't already there
import os
os.chdir('/Users/tomharrison/Documents/Projects/UV_exposure')


# import relevant packages
import constants # a file where API keys are stored
import datetime
import math
import pandas as pd
import pytz
import time
import warnings

# from datetime import datetime, time, timedelta, timezone
from geopy.geocoders import Nominatim
from src import parse_args

from utils.UV_exposure import *
from utils.UV_exposure import get_times


def runner(args):
    
    if args.time or args.current:
    
        # Find local time and the corresponding UTC time
        args.time, utc_time = get_times(
            lat = args.latitude,
            long = args.longitude,
            time = args.time
        )

        # If daylight saving time is currently in force, we subtract 1 hour from the user-specified time for use in calculations
        # We also store the user-supplied time so that we can print it later 
        time_ = args.time
        if time.daylight:
            args.time = args.time - datetime.timedelta(hours = 1)

        # Find the current UTC datetime. We will use it for extracting ozone data, calculating the Earth-Sun distance, and more
        day_of_year = utc_time.timetuple().tm_yday

        # NASA website takes ~2 days to update. Therefore we find the ozone data for 2 days prior to the current date 
        if args.current:
            ozone.get_ozone_data(utc_time - datetime.timedelta(days=2))
            df_ozone = ozone.clean_ozone_data(utc_time - datetime.timedelta(days=2))
        elif args.time:
            utc = pytz.UTC
            if utc.localize(args.time) > datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2):
                warnings.warn("NASA takes 2 days to release ozone data so the most recent ozone data is being used.")
                utc_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)

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

        # Find the clear-sky UV index at the specified location and time
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
            ## TODO: print what the assumed weather condition is
            print('Real UV Index = {}\n'.format(round(real_UVI, 2)))
        elif args.time:
            warnings.warn("There is currently no support for historical weather data, so the real UV index cannot be calculated.")
            
    elif args.start_time:
        # Find the utc time which corresponds to the supplied start_time
        args.time, utc_time = get_times(
            lat = args.latitude,
            long = args.longitude,
            time = args.start_time
        )
        
        # If daylight saving time is currently in force, we subtract 1 hour from the user-specified time for use in calculations
        # We also store the user-supplied time so that we can print it later 
        start_time_ = args.start_time
        end_time_ = args.end_time
        if time.daylight:
            args.start_time = args.start_time - datetime.timedelta(hours = 1)
            args.end_time = args.end_time - datetime.timedelta(hours = 1)
        
        time_inc = max((args.end_time - args.start_time) / 100, datetime.timedelta(minutes = 1))
        times = [args.start_time + ii * time_inc for ii in range(int((args.end_time - args.start_time) / time_inc) + 1)]
        utc_times = [utc_time + ii * time_inc for ii in range(int((args.end_time - args.start_time) / time_inc))]

        day_of_year = utc_times[0].timetuple().tm_yday
        
        # Find the solar zenith angles for each of the times in `times`
        zenith_angles = [
            incident_UV.zenith_angle(
                lat = args.latitude, 
                long = args.longitude, 
                local_time = time, 
                utc_time = utc_time
            )
            for time, utc_time in zip(times, utc_times)
        ]
        
        # NASA takes a few days to release ozone data so we take the most recent day if user specifies a recent/future date. Otherwise we take the ozone data for the start date.
        utc = pytz.UTC
        if utc.localize(args.start_time) > datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2):
            warnings.warn("NASA takes 2 days to release ozone data so the most recent ozone data is being used.")
            utc_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)
        else:
            utc_time = utc_times[0]

        ozone.get_ozone_data(utc_time)
        df_ozone = ozone.clean_ozone_data(utc_time)

        # Find the thickness of the ozone layer at the location of interest
        ozone_thickness = ozone.get_ozone_thickness(
            df_ozone = df_ozone, 
            lat = args.latitude, 
            long = args.longitude
        )
        
        # Find the clear-sky UV index at the specified location and time
        clear_sky_UVI_list = [
            incident_UV.clear_sky_UVI(
                utc_day = day_of_year, 
                zenith = zenith, 
                tot_ozone = ozone_thickness
            )
            for zenith in zenith_angles
        ]
        
        # We can convert from UV index to W/m^2 by multiplying by 0.025
        # Source: https://www.researchgate.net/post/How-can-I-convert-Ultra-Violet-index-into-Ultra-Violet-irradiation-Dose#:~:text=An%20index%20of%2010%20corresponds,(24%20h%20x%202600%20s).
        clear_sky_absorbed_UV = sum([x * 0.025 * time_inc.total_seconds() for x in clear_sky_UVI_list])
        
        print('\nIn {} on {} from {} to {} the accumulated UV is: \n{} Joules per m^2\nNote that this does not account for weather conditions.'.format(args.location, start_time_.strftime("%d/%m/%Y"), start_time_.strftime("%H:%M"), end_time_.strftime("%H:%M"), round(clear_sky_absorbed_UV, 2)))
    
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
        args.time = datetime.datetime.strptime(args.time, '%d/%m/%y %H:%M')
    
    # Convert start and end times to datetime objects
    if args.start_time or args.end_time:
        try:
            args.start_time = datetime.datetime.strptime(args.start_time, '%d/%m/%y %H:%M')
            args.end_time = datetime.datetime.strptime(args.end_time, '%d/%m/%y %H:%M')
        except TypeError as exc:
            raise Exception('Both the start time and end time have to be specified together.') from exc
                    
    # Call the runner
    runner(args)
