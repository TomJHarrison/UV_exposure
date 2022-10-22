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



def runner(lat, long, location):
    # Find the current UTC datetime. We will use it for extracting ozone data, calculating the Earth-Sun distance, and more
    utc_date = datetime.utcnow()
    day_of_year = utc_date.timetuple().tm_yday
    
    # Get yesterday's ozone data and clean it
    # Today's data does not always exist yet
    ozone.get_ozone_data(utc_date - timedelta(days=1))
    df_ozone = ozone.clean_ozone_data(utc_date - timedelta(days=1))
    
    ozone_thickness = ozone.get_ozone_thickness(df_ozone = df_ozone, lat = lat, long = long)
    zenith = incident_UV.zenith_angle(lat = lat, long = long)

    UVA = incident_UV.UVA(utc_day = day_of_year, zenith = zenith)
    clear_sky_UVI = incident_UV.clear_sky_UVI(utc_day = day_of_year, zenith = zenith, tot_ozone = ozone_thickness)

    print(f'\nThe current clear-sky UV index in {location} is {round(clear_sky_UVI, 2)}.\n')
    
    return(0)


if __name__ == "__main__":
    print('Where in the world are you?')
    location = input()
    
    # Find the coordinates of the specified location
    geolocator = Nominatim(timeout=10, user_agent="PDS")
    location_full = geolocator.geocode(location)
    lat, long = location_full.latitude, location_full.longitude

    runner(lat = lat, long = long, location = location)


  
