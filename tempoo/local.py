import datetime
import pytz
import warnings

# I want time zone in CET : WARNING TZINFO ARG OF DATETIME
# IS NOT WORKING CORRECTLY WITH PYZT 
# SEE : STACKOVERFLOW
PARIS_TIME_ZONE = pytz.timezone('Europe/Paris')  # WARNING : DO NOT PASS ME TO TZINFO ARG OF DATETIME !!


def frenchdatetime(
        year: int, month: int, day: int, hour :int = 0, 
        minute: int = 0, second: int = 0, microsecond: int = 0):
    """The right way of creating local French time
       giving year, month, day, hour, minute, second and microsecond, expressed in local time
              
    :param year:   in local french time 
    :param month:  in local french time 
    :param day:    in local french time 
    :param hour:   in local french time 
    :param minute: in local french time 
    :param second: in local french time 
    :param microsecond: in local french time 

    :return frenchtime: 
    :rtype: datetime.datetime with timezone set to PARIS_TIME_ZONE
    """
    return datetime.datetime(
        year=year, month=month, day=day, 
        hour=hour, minute=minute, second=second, 
        microsecond=microsecond).astimezone(PARIS_TIME_ZONE)


def utc2french(utcdatetime: datetime.datetime):
    """
    Convert utc datetime to local time in Paris time zone, 
    WARNING : the timestamp of the object will not be modified !!
              only the hour and the string representation
    :param utcdatetime: an date stored into a datetime.datetime object
                        with tzinfo set to None (i.e. naive) => assumed utc+0
                          or tzinfo set to datetime.timezone.utc
    :return frenchtime:
    :rtype: datetime.datetime with timezone set to PARIS_TIME_ZONE
    """
    if utcdatetime.tzinfo is None:
        warnings.warn('got naive datetime object, I assume it is an UTC')

    elif utcdatetime.tzinfo == datetime.timezone.utc:
        # ok
        pass

    else:
        raise ValueError(f'time zone error : {str(utcdatetime.tzinfo)}')

    return utcdatetime.astimezone(PARIS_TIME_ZONE)

    
def french2utc(frenchdatetime: datetime.datetime):
    """
    naive datetimes not allowed
    WARNING : the timestamp of the object will not be changed !!
    """
    if frenchdatetime.tzinfo.zone == PARIS_TIME_ZONE.zone:
        # ok
        pass

    else:
        raise ValueError(f'time zone error : {frenchdatetime.tzinfo.__repr__()} != {PARIS_TIME_ZONE.__repr__()}')

    return frenchdatetime.astimezone(datetime.timezone.utc)


if __name__ == "__main__":

    now_in_local_time = frenchdatetime(2023, 7, 6, 15, 17, 21, 0)
    print(now_in_local_time, now_in_local_time.timestamp())

    now_in_utc_time = french2utc(now_in_local_time)
    print(now_in_utc_time, now_in_utc_time.timestamp())

    now_back_to_local_time = utc2french(now_in_utc_time)
    print(now_back_to_local_time, now_back_to_local_time.timestamp())
    






#    d = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)
#    while d.year < 2023:
#        print(str(d), d.timestamp())

#        l = utc2french(d)
#        print(str(l), l.timestamp())

#        d += datetime.timedelta(days=1)
#        print()

