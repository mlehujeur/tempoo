from tempoo.utc import UTCFromTimestamp, UTC


"""
values 
in secs ^
        |
        |                      TAI   GPS=TAI -19s
        |                    +     * 
        |                  +     *
        |                +     * 
        |              +     * 
        |            +     *         . UTC[date] = GPS - cumulative_leap_seconds[date] 
        |          +     *   .     .         UTC[1980] = GPS -0s
        |        + |   *   . .   .           UTC[1988] = GPS -5s
        |      +   | *   .   . .             UTC[2023] = GPS -18s 
        |    + .   * . .     .               ... future leap corrections not published yet
        |  + . . . | .
        |+ .   .   | 
        -------------------------------------> dates
                 6/1/1980    ^
                             |leap correction (+1 or -1)
                              to keep the lag between UTC and UT1 < 0.9s
""" 

# GPS origin expressed in UTC time reference system, no leap correction because it was 0 by definition
GPS_EPOCH = UTC(1980, 1, 6, 0, 0, 0) 
# or equivalently
# GPS_EPOCH = datetime.datetime(
#     1980, 1, 6, tzinfo=datetime.timezone.utc)     
 
def cumulative_leap_seconds(timestamp: float):

    """
    source : https://en.wikipedia.org/wiki/Leap_second
    to convert GPS times into UTC times, you must subtract the leap seconds :
        utc[date] = number_of_seconds_since_gps_epoch - cumulative_leap_seconds[date]   
    """
    if timestamp <= UTC(1980, 1, 1).timestamp:
        raise NotImplementedError(timestamp)
    elif timestamp < UTC(1981, 7, 1).timestamp:
        cumulative_leap_seconds = 0.
    elif timestamp < UTC(1982, 7, 1).timestamp:
        cumulative_leap_seconds = 1.
    elif timestamp < UTC(1983, 7, 1).timestamp:
        cumulative_leap_seconds = 2.
    elif timestamp < UTC(1985, 7, 1).timestamp:
        cumulative_leap_seconds = 3.
    elif timestamp < UTC(1988, 1, 1).timestamp:
        cumulative_leap_seconds = 4.
    elif timestamp < UTC(1990, 1, 1).timestamp:
        cumulative_leap_seconds = 5.
    elif timestamp < UTC(1991, 1, 1).timestamp:
        cumulative_leap_seconds = 6.
    elif timestamp < UTC(1992, 7, 1).timestamp:
        cumulative_leap_seconds = 7.
    elif timestamp < UTC(1993, 7, 1).timestamp:
        cumulative_leap_seconds = 8.
    elif timestamp < UTC(1994, 7, 1).timestamp:
        cumulative_leap_seconds = 9.
    elif timestamp < UTC(1996, 1, 1).timestamp:
        cumulative_leap_seconds = 10.
    elif timestamp < UTC(1997, 7, 1).timestamp:
        cumulative_leap_seconds = 11.
    elif timestamp < UTC(1999, 1, 1).timestamp:
        cumulative_leap_seconds = 12.
    elif timestamp < UTC(2006, 1, 1).timestamp:
        cumulative_leap_seconds = 13.
    elif timestamp < UTC(2009, 1, 1).timestamp:
        cumulative_leap_seconds = 14.
    elif timestamp < UTC(2012, 1, 1).timestamp:
        cumulative_leap_seconds = 15.
    elif timestamp < UTC(2015, 7, 1).timestamp:
        cumulative_leap_seconds = 16.
    elif timestamp < UTC(2017, 1, 1).timestamp:
        cumulative_leap_seconds = 17.
    elif timestamp < UTC(2024, 1, 1).timestamp:
        cumulative_leap_seconds = 18.
    elif timestamp < UTC(2025, 1, 1).timestamp:
        cumulative_leap_seconds = 18.
    else:
        raise NotImplementedError(
            'leap second corrections after 2025/01/01 not announced yet')        
    return cumulative_leap_seconds
    
                   
def gps2timestamp(number_of_seconds_since_gps_epoch: float):
    """
    convert a number of seconds in the GPS TIME reference
        (number of seconds elapsed since GPS_EPOCH = 1980-01-06T00:00:00.000000 in UTC reference
    """
    # adding the GPS offset returns a number of seconds which must be corrected to get true UTC
    uncorrected_timestamp = GPS_EPOCH.timestamp + number_of_seconds_since_gps_epoch
    
    # the time correction is adjusted by exactly +1 ou -1s, the correction is cummulative
    leap_seconds_corrections = cumulative_leap_seconds(uncorrected_timestamp)
    
    # leap_seconds_corrections is positive (since 1980) and must be subtracted to get true utc timestamps
    corrected_timestamp = uncorrected_timestamp - leap_seconds_corrections
    return corrected_timestamp # in UTC reference system


def gps2utc(number_of_seconds_since_gps_epoch: float):
    return UTCFromTimestamp(gps2timestamp(number_of_seconds_since_gps_epoch))
    
    
if __name__ == "__main__":

    import numpy as np 
    import matplotlib.pyplot as plt
    from tempoo.timetick import timetick
    
    timestamp = np.linspace(GPS_EPOCH.timestamp, UTC(2023, 12, 24).timestamp, 10000)
    cum_leap_seconds = np.asarray([cumulative_leap_seconds(_) for _ in timestamp], float)

    plt.plot(timestamp, cum_leap_seconds)
    plt.gca().set_ylabel('Cumulative Leap second correction [sec]')
    plt.gca().set_xlabel('Time [years]')
    plt.gca().set_title('UTC(datetime) = number_of_seconds_since_gps_epoch - cumulative_leap_seconds(datetime)')
    timetick(plt.gca(), "x")
    plt.show()
    
    
    
    
