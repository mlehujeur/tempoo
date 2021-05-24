import datetime
from timetools.utc import UTC, UTCFromJulday, UTCFromTimestamp, UTCFromStr
import numpy as np
import pickle
import pytest
import os


data_test_file = os.path.join(os.path.dirname(__file__), 'data_test.txt')
assert os.path.isfile(data_test_file)
A = np.loadtxt(data_test_file, dtype=str)
TIMESTAMPS = np.asarray(A[:, 0], float)
TIMESTRINGS = np.asarray(A[:, 1], str)
YEARS = np.asarray(A[:, 2], int)
MONTHS = np.asarray(A[:, 3], int)
DAYS = np.asarray(A[:, 4], int)
JULDAYS = np.asarray(A[:, 5], int)
WEEKDAYS = np.asarray(A[:, 6], int)
HOURS = np.asarray(A[:, 7], int)
MINUTES = np.asarray(A[:, 8], int)
SECONDS = np.asarray(A[:, 9], int)
MICROSECONDS = np.asarray(A[:, 10], int)


def test_utc_new():
    for t, s, y, m, d, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, HOURS, MINUTES, SECONDS, MICROSECONDS):
        utc_new = UTC(year=y, month=m, day=d, hour=h, minute=mn, second=sc, microsecond=ms)
        assert isinstance(utc_new, UTC)


def test_utc_str():
    for t, s, y, m, d, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, HOURS, MINUTES, SECONDS, MICROSECONDS):
        utc_new = UTC(year=y, month=m, day=d, hour=h, minute=mn, second=sc, microsecond=ms)
        assert isinstance(utc_new, UTC)
        assert str(utc_new) == s


def test_utc_timestamp():
    for t, s, y, m, d, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, HOURS, MINUTES, SECONDS, MICROSECONDS):
        utc_new = UTC(year=y, month=m, day=d, hour=h, minute=mn, second=sc, microsecond=ms)
        assert isinstance(utc_new.timestamp, float)
        assert utc_new.timestamp == t


def test_utc_float():
    for t, s, y, m, d, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, HOURS, MINUTES, SECONDS, MICROSECONDS):
        utc_new = UTC(year=y, month=m, day=d, hour=h, minute=mn, second=sc, microsecond=ms)
        assert float(utc_new) == t


def test_utc_weekday():
    for t, wd, y, m, d, h, mn, sc, ms in \
            zip(TIMESTAMPS, WEEKDAYS, YEARS, MONTHS, DAYS, HOURS, MINUTES, SECONDS, MICROSECONDS):
        utc_new = UTC(year=y, month=m, day=d, hour=h, minute=mn, second=sc, microsecond=ms)
        assert utc_new.weekday == wd


def test_utc_julday():
    for t, jd, y, m, d, h, mn, sc, ms in \
            zip(TIMESTAMPS, JULDAYS, YEARS, MONTHS, DAYS, HOURS, MINUTES, SECONDS, MICROSECONDS):
        utc_new = UTC(year=y, month=m, day=d, hour=h, minute=mn, second=sc, microsecond=ms)
        assert utc_new.julday == jd


def test_utc_from_decimal_year_new():
    for t, s, y, m, d, jd, wd, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, JULDAYS, WEEKDAYS,
                HOURS, MINUTES, SECONDS, MICROSECONDS):

        utc_new = UTC(year=y, month=m, day=d, hour=h, minute=mn, second=sc, microsecond=ms)
        decimal_year = utc_new.decimal_year
        assert utc_new.flooryear.year == int(decimal_year)
        assert utc_new.ceilyear.year - 1 == int(decimal_year)


def test_utc_add():
    i, j = np.array(np.random.rand(2) * len(TIMESTAMPS), int)

    utc1 = UTC(
        YEARS[i], MONTHS[i], DAYS[i],
        HOURS[i], MINUTES[i], SECONDS[i],
        MICROSECONDS[i])

    utc2 = UTC(
        YEARS[j], MONTHS[j], DAYS[j],
        HOURS[j], MINUTES[j], SECONDS[j],
        MICROSECONDS[j])

    assert isinstance(utc1 + utc2, UTC)
    assert (utc1 + utc2).timestamp == round(utc1.timestamp + utc2.timestamp, 6)

    assert isinstance(utc1 + utc2.timestamp, UTC)
    assert (utc1 + utc2.timestamp).timestamp == round(utc1.timestamp + utc2.timestamp, 6)

    assert isinstance(utc1 + int(utc2.timestamp), UTC)
    assert (utc1 + int(utc2.timestamp)).timestamp == round(utc1.timestamp + int(utc2.timestamp), 6)

    assert isinstance(utc1 + datetime.timedelta(seconds=utc2.timestamp), UTC)
    assert (utc1 + datetime.timedelta(seconds=utc2.timestamp)).timestamp == round(utc1.timestamp + utc2.timestamp, 6)

    with pytest.raises(TypeError):
        utc1 + object()


def test_utc_sub():
    i, j = np.array(np.random.rand(2) * len(TIMESTAMPS), int)

    utc1 = UTC(
        YEARS[i], MONTHS[i], DAYS[i],
        HOURS[i], MINUTES[i], SECONDS[i],
        MICROSECONDS[i])

    utc2 = UTC(
        YEARS[j], MONTHS[j], DAYS[j],
        HOURS[j], MINUTES[j], SECONDS[j],
        MICROSECONDS[j])

    assert isinstance(utc1 - utc2, UTC)
    assert (utc1 - utc2).timestamp == round(utc1.timestamp - utc2.timestamp, 6)

    assert isinstance(utc1 - utc2.timestamp, UTC)
    assert (utc1 - utc2.timestamp).timestamp == round(utc1.timestamp - utc2.timestamp, 6)

    assert isinstance(utc1 - int(utc2.timestamp), UTC)
    assert (utc1 - int(utc2.timestamp)).timestamp == round(utc1.timestamp - int(utc2.timestamp), 6)

    assert isinstance(utc1 - datetime.timedelta(seconds=utc2.timestamp), UTC)
    assert (utc1 - datetime.timedelta(seconds=utc2.timestamp)).timestamp == round(utc1.timestamp - utc2.timestamp, 6)

    with pytest.raises(TypeError):
        utc1 - object()


def test_julian_utc_new():
    for t, s, y, m, d, jd, wd, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, JULDAYS, WEEKDAYS,
                HOURS, MINUTES, SECONDS, MICROSECONDS):

        utc_new = UTCFromJulday(
            year=y, julday=jd, hour=h, minute=mn, second=sc, microsecond=ms)

        assert isinstance(utc_new, UTCFromJulday)
        assert utc_new.year == y
        assert utc_new.month == m
        assert utc_new.day == d
        assert utc_new.julday == jd
        assert utc_new.weekday == wd
        assert utc_new.hour == h
        assert utc_new.minute == mn
        assert utc_new.second == sc
        assert utc_new.microsecond == ms
        assert utc_new.timestamp == t
        assert str(utc_new) == s


def test_utc_from_timestamp_new():
    for t, s, y, m, d, jd, wd, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, JULDAYS, WEEKDAYS,
                HOURS, MINUTES, SECONDS, MICROSECONDS):

        utc_new = UTCFromTimestamp(t)
        assert isinstance(utc_new, UTCFromTimestamp)
        assert utc_new.year == y
        assert utc_new.month == m
        assert utc_new.day == d
        assert utc_new.julday == jd
        assert utc_new.weekday == wd
        assert utc_new.hour == h
        assert utc_new.minute == mn
        assert utc_new.second == sc
        assert utc_new.microsecond == ms
        assert utc_new.timestamp == t
        assert str(utc_new) == s


def test_utc_from_str_new():
    for t, s, y, m, d, jd, wd, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, JULDAYS, WEEKDAYS,
                HOURS, MINUTES, SECONDS, MICROSECONDS):

        utc_new = UTCFromStr(s)
        assert isinstance(utc_new, UTCFromStr)
        assert utc_new.year == y
        assert utc_new.month == m
        assert utc_new.day == d
        assert utc_new.julday == jd
        assert utc_new.weekday == wd
        assert utc_new.hour == h
        assert utc_new.minute == mn
        assert utc_new.second == sc
        assert utc_new.microsecond == ms
        assert utc_new.timestamp == t
        assert str(utc_new) == s


# pickling is a very important feature for multiprocessing
# these tests ensure that pickling-unpickling is safe for all objects
def test_getstate():
    utc = UTC(1234, 5, 6, 7, 8, 9, 123456)
    state = utc.__getstate__()
    assert state == (1234, 5, 6, 7, 8, 9, 123456)


def test_pickle_utc():
    for t, s, y, m, d, jd, wd, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, JULDAYS, WEEKDAYS,
                HOURS, MINUTES, SECONDS, MICROSECONDS):

        utc = UTC(year=y, month=m, day=d, hour=h, minute=mn, second=sc, microsecond=ms)

        pkl = pickle.dumps(utc)
        del utc
        utc = pickle.loads(pkl)

        assert utc.year == y
        assert utc.month == m
        assert utc.day == d
        assert utc.julday == jd
        assert utc.weekday == wd
        assert utc.hour == h
        assert utc.minute == mn
        assert utc.second == sc
        assert utc.microsecond == ms
        assert utc.timestamp == t
        assert str(utc) == s


def test_pickle_utc_from_julday():
    for t, s, y, m, d, jd, wd, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, JULDAYS, WEEKDAYS,
                HOURS, MINUTES, SECONDS, MICROSECONDS):

        utc = UTCFromJulday(year=y, julday=jd, hour=h, minute=mn, second=sc, microsecond=ms)
        pkl = pickle.dumps(utc)
        del utc
        utc = pickle.loads(pkl)
        assert utc.year == y
        assert utc.month == m
        assert utc.day == d
        assert utc.julday == jd
        assert utc.weekday == wd
        assert utc.hour == h
        assert utc.minute == mn
        assert utc.second == sc
        assert utc.microsecond == ms
        assert utc.timestamp == t
        assert str(utc) == s


def test_pickle_utc_from_timestamp():
    for t, s, y, m, d, jd, wd, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, JULDAYS, WEEKDAYS,
                HOURS, MINUTES, SECONDS, MICROSECONDS):

        utc = UTCFromTimestamp(t)
        pkl = pickle.dumps(utc)
        del utc
        utc = pickle.loads(pkl)
        assert utc.year == y
        assert utc.month == m
        assert utc.day == d
        assert utc.julday == jd
        assert utc.weekday == wd
        assert utc.hour == h
        assert utc.minute == mn
        assert utc.second == sc
        assert utc.microsecond == ms
        assert utc.timestamp == t
        assert str(utc) == s


def test_pickle_utc_from_str():
    for t, s, y, m, d, jd, wd, h, mn, sc, ms in \
            zip(TIMESTAMPS, TIMESTRINGS, YEARS, MONTHS, DAYS, JULDAYS, WEEKDAYS,
                HOURS, MINUTES, SECONDS, MICROSECONDS):
        utc = UTCFromStr(s)
        pkl = pickle.dumps(utc)
        del utc
        utc = pickle.loads(pkl)
        assert utc.year == y
        assert utc.month == m
        assert utc.day == d
        assert utc.julday == jd
        assert utc.weekday == wd
        assert utc.hour == h
        assert utc.minute == mn
        assert utc.second == sc
        assert utc.microsecond == ms
        assert utc.timestamp == t
        assert str(utc) == s




