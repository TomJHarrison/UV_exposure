from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from tzwhere import tzwhere
from os.path import exists

import requests
import pytz

def get_local_time(lat, long):
    """
    Returns the current local time for a given location.
    """

    # find timezone name
    timezone_str = tzwhere.tzwhere().tzNameAt(lat, long)

    # find time difference of timezone compare to UTC
    timezone = pytz.timezone(timezone_str)

    utc_offset = timezone.utcoffset(datetime.utcnow())

    # subtract time difference from UTC
    local_time = datetime.utcnow() + timedelta(days = utc_offset.days,
                                               seconds = utc_offset.seconds) 

    return(local_time)

def get_ozone_data(lat, long): 

    if not exists('./data/ozone_data.txt'):
        # Extract all links on the url webpage. This page contains links to text files containing global ozone data
        url = "https://ozonewatch.gsfc.nasa.gov/data/omps/Y2022/"
        reqs = requests.get(url)
        links = BeautifulSoup(reqs.text, 'html.parser')

        # Find current datetime at given latitude and longitude
        date = get_local_time(lat, long)

        # Combine year, month and day into a format that we expect to be in the relevant text file link
        date_suffix = '{:04d}'.format(date.year) + 'm' + '{:02d}'.format(date.month) + '{:02d}'.format(date.day - 1)

        # Find text file link
        txt_file_suffix = [link.get('href') for link in links.find_all('a') if date_suffix in link.get('href')]
        file_url = url + txt_file_suffix[0]

        r = requests.get(file_url, allow_redirects=True)

        open('./data/ozone_data.txt', 'wb').write(r.content)
            