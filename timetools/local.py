import datetime
import pytz
import warnings


PARIS_TIME_ZONE = pytz.timezone('Europe/Paris')
JAPAN_TIME_ZONE = pytz.timezone('Japan')


def utc2french(utcdatetime: datetime.datetime):
    """
    Convert utc datetime to local time in Paris time zone, 
    WARNING : the timestamp of the object will not be changed !!
              only the hour and the string representation
    
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
    if frenchdatetime.tzinfo == PARIS_TIME_ZONE:
        # ok
        pass

    else:
        raise ValueError(f'time zone error : {str(frenchdatetime.tzinfo)}')

    return frenchdatetime.astimezone(datetime.timezone.utc)


if __name__ == "__main__":
    d = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)
    while d.year < 2023:
        print(str(d), d.timestamp())

        l = utc2french(d)
        print(str(l), l.timestamp())

        d += datetime.timedelta(days=1)
        print()

