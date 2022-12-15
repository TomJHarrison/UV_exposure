# Change to correct directory in case we aren't already there
import os
os.chdir('/Users/tomharrison/Documents/Projects/UV_exposure')


# import relevant packages
import constants # a file where API keys are stored
import math
import pandas as pd
import warnings

from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from utils.UV_exposure import *



def runner(lat, long, location, time):
    # Find current local time and the corresponding UTC time
    local_time, utc_time = incident_UV.get_times(lat = lat, long = long, time = time)
    
    # Find the current UTC datetime. We will use it for extracting ozone data, calculating the Earth-Sun distance, and more
    day_of_year = utc_time.timetuple().tm_yday
    
    # Get yesterday's ozone data and clean it
    # Today's data does not always exist yet
    ozone.get_ozone_data(utc_time - timedelta(days=1))
    df_ozone = ozone.clean_ozone_data(utc_time - timedelta(days=1))
    
    # Find the thickness of the ozone layer at the location of interest
    ozone_thickness = ozone.get_ozone_thickness(df_ozone = df_ozone, 
                                                lat = lat, 
                                                long = long)
    
    # Find the solar zenith angle at the location and time given
    zenith = incident_UV.zenith_angle(lat = lat, 
                                      long = long, 
                                      local_time = local_time, 
                                      utc_time = utc_time)

    # Find the cleay-sky UV index at the specified location and time
    clear_sky_UVI = incident_UV.clear_sky_UVI(utc_day = day_of_year, 
                                              zenith = zenith, 
                                              tot_ozone = ozone_thickness)

    # Find the cloud modification factor based on weather
    cmf = cloud_cover.get_cloud_mod_factor(lat = lat, 
                                           long = long, 
                                           time = time, 
                                           api_key = constants.weatherstack_api_key)
    
    real_UVI = cmf * clear_sky_UVI
    
    print('\nIn {} on {} at {}: \nClear-sky UV index = {} \nReal UV index = {}\n'.format(location, local_time.strftime("%d/%m/%Y"), local_time.strftime("%H:%M"), round(clear_sky_UVI, 2), round(real_UVI, 2)))
    
    return 0



if __name__ == "__main__":
    print('Where in the world are you?')
    location = input()
        
    # Find the coordinates of the specified location
    geolocator = Nominatim(timeout=10, user_agent="PDS")
    location_full = geolocator.geocode(location)
    lat, long = location_full.latitude, location_full.longitude

    print('If you want the current UV index for {}, type "Now", otherwise type the date and time that you would like the UV index for. Date and time must be in the format "day/month/year hour:minute."'.format(location))
    time = input()

    # If the user wants the current time, then find the local time of that location
    # Otherwise convert the time into a date format
    if time.lower() == "now":
        time = None
    else:
        time = datetime.strptime(time, '%d/%m/%y %H:%M')

    # Call the runner
    runner(lat = lat, 
           long = long, 
           location = location, 
           time = time)
