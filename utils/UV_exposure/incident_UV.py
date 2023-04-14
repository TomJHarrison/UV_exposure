import math

from datetime import timedelta


def zenith_angle(lat, long, local_time, utc_time):
    """
    Finds the solar zenith angle for a given location and time. The zenith angle is the angle between a line from a location on the Earth's surface to the Sun, and a line which points perpendicularly outwards from that location on Earth. Therefore, a zenith angle of 0 indicates that the Sun is directly overhead.
    
    Parameters:
        lat (float): latitude coordinate of the given location
        long (float): longitude coordinate of the given location
        time (datetime): the time of day
    
    Returns:
        zenith_angle (float): the solar zenith angle in radians
    """
    
    
    def metric_ang_decl(utc_time):
        """
        Returns the declination angle of the Earth in degrees.

        Parameters:
            day (int): the day of the year

        Returns:
            ang_decl (float): the angle of declination of the Earth in degrees
        """

        day = utc_time.timetuple().tm_yday
        return -23.45 * math.cos(math.radians((360 / 365) * (day + 10)))
    
    
    def LSTM(lat, long, local_time, utc_time):
        """
        Returns the Local Standard Time Meridian
        """

        delta_utc =  local_time.hour - utc_time.hour
        
        return 15 * delta_utc


    def time_correct_fact(lat, long, local_time, utc_time):
        """
        Returns the time correction factor for a particular longitude
        """

        day = local_time.timetuple().tm_yday

        b = (360 / 365) * (day - 81)

        tcf = 4 * (long - LSTM(lat = lat, long = long, local_time = local_time, utc_time = utc_time)) + 9.87*math.sin(math.radians(2*b)) - 7.53*math.cos(math.radians(b)) - 1.5*math.sin(math.radians(b))

        return tcf 


    def hour_angle(lat, long, local_time, utc_time):
        """
        Returns the hour angle for a particular longitude
        """

        time_corrected = local_time + timedelta(hours = -12, minutes = time_correct_fact(lat = lat, long = long, local_time = local_time, utc_time = utc_time) / 60, seconds = 0)

        hr_angle = 15 * (time_corrected.hour + time_corrected.minute / 60 + time_corrected.second / 3600)
        
        return hr_angle
    
    
    #------ function call begins ------#
    
    ang_decl = metric_ang_decl(utc_time = utc_time)

    elevation_angle = math.asin(math.sin(math.radians(ang_decl)) * math.sin(math.radians(lat)) + math.cos(math.radians(ang_decl)) * math.cos(math.radians(lat)) * math.cos(math.radians(hour_angle(lat = lat, long = long, local_time = local_time, utc_time = utc_time))))

    # convert from elevation angle to zenith angle
    zenith_angle = (math.pi / 2) - elevation_angle
    return zenith_angle
 
    
def UVA(utc_day, zenith):
    """
    Calculate the current UVA value for a given location.
    We don't have latitude and longitude because we want the zenith angle to be identical
    for this equation and for UVI (see below). Having zentih as an argument avoids calculating the 
    zenith angle twice and at two separate (albeit close) times.
    """
    
    mu = math.cos(zenith) * 0.83 + 0.17
    earth_sun_dist = 1 - 0.01672 * math.cos(0.9856 * (utc_day - 4))
    
    UVA = pow((1 / earth_sun_dist), 2) * 1.24 * mu * math.exp(- (0.58 / mu))
    return UVA


def clear_sky_UVI(utc_day, zenith, tot_ozone):
    """
    Calculate current clear-sky UVI for a given location
    """
    
    UVA_ = UVA(utc_day, zenith)

    X = 1000 * math.cos(zenith) / tot_ozone
    
    UVI = UVA_ * (2 * pow(X, 1.62) + 280 / tot_ozone + 1.4)
    
    if isinstance(UVI, complex) or UVI < 0:
        UVI = 0
        
    return UVI
    