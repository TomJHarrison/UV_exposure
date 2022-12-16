import pytz
import warnings

from . import incident_UV
from . import ozone
from datetime import datetime, timedelta
from tzwhere import tzwhere

__all__ = ["cloud_cover", "incident_UV", "ozone"]


def get_times(lat, long, time = None):
    """
    A function to return the local time and the utc time. If the user does not enter a time then the function finds the current local time and the current utc time. If the user enter s atime, then the function returns that time and calculates what the UTC time would be, given the specified time for a particular location.
    """
    
    # find timezone name
    # we expect a warning here which is generated from the tzwhere package - suppress it.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        timezone_str = tzwhere.tzwhere().tzNameAt(lat, long)

    # find time difference between timezone and UTC
    timezone = pytz.timezone(timezone_str)
    utc_offset = timezone.utcoffset(datetime.utcnow())

    if time is None:
        utc_time = datetime.utcnow().replace(second = 0, microsecond = 0)
        # add time difference to UTC time
        local_time = utc_time + timedelta(days = utc_offset.days,
                                          seconds = utc_offset.seconds) 
        return local_time, utc_time

    else:
        # subtract time difference from UTC
        utc_time = time - timedelta(days = utc_offset.days,
                                    seconds = utc_offset.seconds)
        return time, utc_time