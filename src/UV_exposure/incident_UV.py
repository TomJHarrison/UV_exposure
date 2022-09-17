from datetime import datetime, timedelta
from tzwhere import tzwhere

import math
import pytz


def metric_ang_decl():
    """
    Returns the declination angle of the Earth in degrees.
    
    Parameters:
        day (int): the day of the year
        
    Returns:
        ang_decl (float): the angle of declination of the Earth in degrees
    """
    
    day = datetime.utcnow().timetuple().tm_yday
    return(-23.45 * math.cos((360 / 365) * (day + 10)))


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


def LSTM(lat, long):
    """
    Returns the Local Standard Time Meridian
    """
    
    local_time = get_local_time(lat = lat, long = long)
    delta_utc =  local_time.hour - datetime.utcnow().hour
    return(15 * delta_utc)


def time_correct_fact(lat, long):
    """
    Returns the time correction factor for a particular longitude
    """
    
    local_time = get_local_time(lat = lat, long = long)
    day = local_time.timetuple().tm_yday
    b = (360 / 365) * (day - 81)
    
    tcf = 4*(long-LSTM(lat = lat, long = long)) + 9.87*math.sin(2*b) - 7.53*math.cos(b) - 1.5*math.sin(b)
    return(tcf)


def hour_angle(lat, long):
    """
    Returns the hour angle for a particular longitude
    """
    
    local_time = get_local_time(lat = lat, long = long)
    time_corrected = local_time + timedelta(hours = -12, minutes = time_correct_fact(lat = lat, long = long) / 60, seconds = 0)
    
    hr_angle = 15 * (time_corrected.hour + time_corrected.minute / 60 + time_corrected.second / 3600)
    
    return(hr_angle)
    
    