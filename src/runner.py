# Change to correct directory in case we aren't already there
import os
os.chdir('/Users/tomharrison/Documents/Projects/UV_exposure')


# import relevant packages
import math
import pandas as pd
import warnings

from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from utils.UV_exposure import *



def runner(lat, long, location, local_time, utc_time):
    # Find the current UTC datetime. We will use it for extracting ozone data, calculating the Earth-Sun distance, and more
    day_of_year = utc_time.timetuple().tm_yday
    
    # Get yesterday's ozone data and clean it
    # Today's data does not always exist yet
    ozone.get_ozone_data(utc_time - timedelta(days=1))
    df_ozone = ozone.clean_ozone_data(utc_time - timedelta(days=1))
    
    ozone_thickness = ozone.get_ozone_thickness(df_ozone = df_ozone, 
                                                lat = lat, 
                                                long = long)
    
    zenith = incident_UV.zenith_angle(lat = lat, 
                                      long = long, 
                                      local_time = local_time, 
                                      utc_time = utc_time)

    UVA = incident_UV.UVA(utc_day = day_of_year, 
                          zenith = zenith)
    clear_sky_UVI = incident_UV.clear_sky_UVI(utc_day = day_of_year, 
                                              zenith = zenith, 
                                              tot_ozone = ozone_thickness)

    print('\nThe clear-sky UV index in {} on {} at {} is {}.\n'.format(location, time.strftime("%d/%m/%Y"), time.strftime("%H:%M"), round(clear_sky_UVI, 2)))
    
    return(0)


if __name__ == "__main__":
    print('Where in the world are you?')
    location = input()
        
    # Find the coordinates of the specified location
    geolocator = Nominatim(timeout=10, user_agent="PDS")
    location_full = geolocator.geocode(location)
    lat, long = location_full.latitude, location_full.longitude

    print(lat, long)
    
    print('If you want the current UV index for {}, type "Now", otherwise type the date and time that you would like the UV index for. Date and time must be in the format "day/month/year hour:minute."'.format(location))
    time = input()

    # If the user wants the current time, then find the local time of that location
    if time.lower() == "now":
        local_time, utc_time = incident_UV.get_times(lat = lat, long = long)
    
    # Otherwise convert the time into a date format
    else:
        time = datetime.strptime(time, '%d/%m/%y %H:%M')
        local_time, utc_time = incident_UV.get_times(lat = lat, long = long, time = time)

 
    # Call the runner
    runner(lat = lat, 
           long = long, 
           location = location, 
           local_time = local_time, 
           utc_time = utc_time)


  
