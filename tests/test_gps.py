from tempoo.gps import gps2utc
from tempoo.utc import UTC, UTCFromTimestamp


def test_gps_1988():

    # GPS[1988] must be exactly UTC + 5.0s
    number_of_seconds_since_gps_epoch = 275994595.0
    date_gps = UTC(1980, 1, 6) + number_of_seconds_since_gps_epoch
    date_utc = gps2utc(number_of_seconds_since_gps_epoch)
    assert date_gps.timestamp - date_utc.timestamp == +5.0
    
    
def test_gps_2023():    
    # GPS[2023] must be UTC + 18.0s    
    number_of_seconds_since_gps_epoch = 1378771200.0
    date_gps = UTC(1980, 1, 6) + number_of_seconds_since_gps_epoch
    date_utc = gps2utc(number_of_seconds_since_gps_epoch)
    assert date_gps.timestamp - date_utc.timestamp == +18.0

