import math
import numpy as np
import os
import pandas as pd
import pytz
import requests

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from tzwhere import tzwhere
from os.path import exists


def get_ozone_data(): 
    
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    
    # Find current datetime for UTC
    date = datetime.utcnow() - timedelta(days=1) 
    end_filepath = "./data/ozone_data_raw_" + str(date.year) + str(date.month) + str(date.day) + ".txt"
    
    # Check whether ozone data file already exists
    if not exists(end_filepath):
        # Extract all links on the url webpage. This page contains links to text files containing global ozone data
        url = "https://ozonewatch.gsfc.nasa.gov/data/omps/Y2022/"
        reqs = requests.get(url)
        links = BeautifulSoup(reqs.text, 'html.parser')

        # Combine year, month and day into a format that we expect to be in the relevant text file link
        date_suffix = '{:04d}'.format(date.year) + 'm' + '{:02d}'.format(date.month) + '{:02d}'.format(date.day - 1)

        # Find text file link
        txt_file_suffix = [link.get('href') for link in links.find_all('a') if date_suffix in link.get('href')]
        file_url = url + txt_file_suffix[0]

        r = requests.get(file_url, allow_redirects=True)
        
        open(f'{end_filepath}', 'wb').write(r.content)


def clean_ozone_data():
    
    # Find current datetime for UTC
    date = datetime.utcnow() - timedelta(days=1) 
    raw_filepath = "./data/ozone_data_raw_" + str(date.year) + str(date.month) + str(date.day) + ".txt"
    clean_filepath = "./data/ozone_data_clean_" + str(date.year) + str(date.month) + str(date.day) + ".txt"
    
    if exists(clean_filepath):
        return(pd.read_csv(clean_filepath, sep = ' '))
    
    else: 
        # Read in ozone data
        df_ozone = pd.read_csv(raw_filepath, skiprows=3, names = ["raw_values"])

        # Create a dataframe containing our latitude and longitude intervals
        df_out = pd.DataFrame({'Latitude': np.repeat(np.linspace(-89.5, 89.5, 180), 360),
                               'Longitude': np.linspace(-179.5, 179.5, 360).tolist() * 180})

        # Remove leading whitespace on each row
        df_ozone['raw_values'] = df_ozone['raw_values'].str[1:]

        # Remove the word 'lat' and anything that comes after it
        df_ozone['raw_values'] = df_ozone['raw_values'].str.split('lat').str[0]

        # Remove trailing whitespace on each row
        df_ozone['raw_values'] = df_ozone['raw_values'].str.rstrip(' ')

        # Now we will separate our row entries into 3-digit long values using nested list comprehension.
        # We then flatten our list using list comprehension.
        two_d_list = [[row[n:(n+3)] for n in range(0, len(row), 3)] for row in df_ozone['raw_values']]
        flatten_list = [ii for item in two_d_list for ii in item]
        df_out['ozone_dobson_value'] = flatten_list

        # Write output to a text file
        df_out.to_csv(clean_filepath, header = True, sep = ' ', index = False)

        return(df_out)


def get_ozone_thickness(df_ozone, lat, long):
    lat_rounded = math.floor(lat) + 0.5
    long_rounded = math.floor(long) + 0.5
    
    return(int(df_ozone.loc[(df_ozone['Latitude'] == lat_rounded) & (df_ozone['Longitude'] == long_rounded)]['ozone_dobson_value']))

