import math
from datetime import datetime

def metric_ang_decl():
    """
    Returns the declination angle of the Earth in degrees.
    
    Parameters:
        day (int): the day of the year
        
    Returns:
        ang_decl (float): the angle of declination of the Earth in degrees
    """
    
    day = datetime.now().timetuple().tm_yday
    return(-23.45 * math.cos((360 / 365) * (day + 10)))

def LSTM():
    """
    Returns the Local Standard Time Meridian
    """
    
    delta_utc =  datetime.now().hour - datetime.utcnow().hour
    return(15 * delta_utc)

def time_correct_fact(longitude):
    """
    Returns the time correction factor for a particular longitude
    """
    
    day = datetime.now().timetuple().tm_yday
    b = (360 / 365) * (day - 81)
    
    tcf = 4*(longitude-LSTM()) + 9.87*math.sin(2*b) - 7.53*math.cos(b) - 1.5*math.sin(b)
    return(tcf)