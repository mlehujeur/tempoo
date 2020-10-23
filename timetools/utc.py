from __future__ import annotations
from typing import Union
import datetime
import numpy as np

MINUTE = 60.
HOUR = 60. * MINUTE
DAY = 24. * HOUR
YEAR = 365.25 * DAY
WEEK = 7. * DAY

UTCTZINFO = datetime.timezone(datetime.timedelta(0), 'UTC')

"""
policy
UTC + float => UTC
UTC + datetime.timedelta => UTC
UTC + UTC => UTC

UTC - float => UTC
UTC - datetime.timedelta => UTC
UTC - UTC => UTC
"""


class UTC(datetime.datetime):

    def __new__(cls, year=1970, month=1, day=1,
                hour=0, minute=0, second=0, microsecond=0):

        if isinstance(year, (bytes, str)):
            # pickle support by datetime.datetime
            # year might be a byte object and month corresponds to tzinfo
            d = datetime.datetime(year, month)
            year, month, day, hour, minute, second, microsecond = \
                d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond

        self = super().__new__(
            cls,
            year=year, month=month, day=day,
            hour=hour, minute=minute,
            second=second, microsecond=microsecond,
            # WARNING : VERY IMPORTANT ARG !!
            tzinfo=UTCTZINFO)
        return self

    def __getstate__(self):
        return (self.year, self.month, self.day,
                self.hour, self.minute, self.second,
                self.microsecond)

    # def __setstate__(self, state):
    #     NO : cannot init self since the initation is done in __new__
    #     year, month, day, hour, minute, second, microsecond = state
    #     UTC.__init__(self,
    #         year=year, month=month, day=day,
    #         hour=hour, minute=minute, second=second,
    #         microsecond=microsecond)

    def __str__(self):
        return f'{self.year:04d}-{self.month:02d}-{self.day:02d}T' \
               f'{self.hour:02d}:{self.minute:02d}:{self.second:02d}.{self.microsecond:06d}Z'

    @property
    def timestamp(self):
        return datetime.datetime.timestamp(self)

    def __float__(self):
        return self.timestamp

    @property
    def weekday(self):
        # 0 = Monday
        return datetime.datetime.weekday(self)

    @property
    def julday(self):
        # timedelta = (self - self.flooryear)
        # julday = int(np.floor(timedelta.total_seconds() / DAY)) + 1
        timedelta = self.timestamp - self.flooryear.timestamp
        julday = int(np.floor(timedelta / DAY)) + 1
        return julday

    @property
    def flooryear(self):
        return UTC(year=self.year, month=1, day=1,
                   hour=0, minute=0, second=0, microsecond=0)

    @property
    def ceilyear(self):
        fy = self.flooryear
        if self == fy:
            return fy
        return UTC(year=self.year+1, month=1, day=1,
                   hour=0, minute=0, second=0, microsecond=0)

    @property
    def floormonth(self):
        return UTC(year=self.year, month=self.month, day=1,
                   hour=0, minute=0, second=0, microsecond=0)

    @property
    def ceilmonth(self):
        fm = self.floormonth
        if self == fm:
            return fm
        if self.month < 12:
            return UTC(year=self.year, month=self.month+1, day=1,
                       hour=0, minute=0, second=0, microsecond=0)
        else:
            return self.ceilyear

    @property
    def floorday(self):
        return UTC(year=self.year, month=self.month, day=self.day,
                   hour=0, minute=0, second=0, microsecond=0)

    @property
    def ceilday(self):
        fd = self.floorday
        if self == fd:
            return fd
        try:
            return UTC(year=self.year, month=self.month, day=self.day+1,
                       hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            return self.ceilmonth

    @property
    def floorhour(self):
        return UTC(year=self.year, month=self.month, day=self.day,
                   hour=self.hour, minute=0, second=0, microsecond=0)

    @property
    def ceilhour(self):
        fh = self.floorhour
        if self == fh:
            return fh
        try:
            return UTC(year=self.year, month=self.month, day=self.day,
                       hour=self.hour+1, minute=0, second=0, microsecond=0)
        except ValueError:
            return self.ceilday

    @property
    def floorminute(self):
        return UTC(year=self.year, month=self.month, day=self.day,
                   hour=self.hour, minute=self.minute, second=0, microsecond=0)

    @property
    def ceilminute(self):
        fm = self.floorminute
        if self == fm:
            return fm
        try:
            return UTC(year=self.year, month=self.month, day=self.day,
                       hour=self.hour, minute=self.minute+1, second=0, microsecond=0)
        except ValueError:
            return self.ceilhour

    @property
    def floorweek(self):
        fd = self.floorday
        return UTCFromTimestamp(fd.timestamp - self.weekday * DAY)

    @property
    def ceilweek(self):
        fd = self.floorweek
        if fd == self:
            return fd
        return UTCFromTimestamp(self.timestamp + WEEK).floorweek

    def _operate(self, method, other: Union[datetime.timedelta, float]):
        if isinstance(other, float):
            other = datetime.timedelta(seconds=other)

        elif not isinstance(other, datetime.timedelta):
            raise TypeError(str(method), type(other))

        new = method(other)

        return UTC(
            year=new.year, month=new.month, day=new.day,
            hour=new.hour, minute=new.minute, second=new.second,
            microsecond=new.microsecond)

    def _operate(self, method, other: Union[datetime.timedelta, float, int, UTC]) -> UTC:

        if isinstance(other, datetime.timedelta):
            pass

        elif isinstance(other, float) or isinstance(other, int):
            other = datetime.timedelta(seconds=other)

        elif isinstance(other, UTC):
            other = datetime.timedelta(seconds=other.timestamp)

        else:
            raise TypeError(type(other))

        new = method(other)

        return UTC(
            year=new.year, month=new.month, day=new.day,
            hour=new.hour, minute=new.minute, second=new.second,
            microsecond=new.microsecond)

    def __add__(self, other):
        return self._operate(method=super(UTC, self).__add__, other=other)

    def __sub__(self, other):
        return self._operate(method=super(UTC, self).__sub__, other=other)


class UTCFromJulday(UTC):
    def __new__(cls, year=1970, julday=1,
                hour=0, minute=0, second=0, microsecond=0):

        if isinstance(year, (bytes, str)):
            # pickle support by datetime.datetime
            d = UTC(year, julday)
            year, julday, hour, minute, second, microsecond = \
                d.year, d.julday, d.hour, d.minute, d.second, d.microsecond

        if not isinstance(julday, int) and not isinstance(julday, np.int64):
            raise TypeError(type(julday))

        first_day_of_year_same_clock = UTC(
            year, month=1, day=1,
            hour=hour, minute=minute,
            second=second, microsecond=microsecond)

        end_of_year = UTC(year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        last_julday_of_year = (end_of_year - 12. * HOUR).julday

        if not 1 <= julday <= last_julday_of_year:
            raise ValueError(
                f'in year {year}, '
                f'julday must be between 1 and {last_julday_of_year}, '
                f'got {julday}')

        utc = (first_day_of_year_same_clock + (julday - 1) * DAY)

        self = super(UTCFromJulday, cls).__new__(
            cls,
            year=utc.year, month=utc.month, day=utc.day,
            hour=utc.hour, minute=utc.minute, second=utc.second,
            microsecond=utc.microsecond)

        return self


class UTCFromTimestamp(UTC):
    def __new__(cls, timestamp, *_args):

        if isinstance(timestamp, (bytes, str)):
            # pickle support by datetime.datetime
            d = datetime.datetime(timestamp, *_args)
            timestamp = d.timestamp()

        # d = datetime.datetime.fromtimestamp(timestamp - HOUR)   # ????
        d = datetime.datetime.fromtimestamp(timestamp, tz=UTCTZINFO)   # ????
        self = UTC.__new__(
            cls, year=d.year, month=d.month, day=d.day,
            hour=d.hour, minute=d.minute,
            second=d.second, microsecond=d.microsecond)
        return self


class UTCFromStr(UTC):
    def __new__(cls, string, *_args):

        if isinstance(string, (bytes)):
            # pickle support by datetime.datetime
            d = UTC(string, *_args)
            string = str(d)

        yyyymtdd, hhmnssnnnnnnZ = string.split('T')
        yyyy, mt, dd = yyyymtdd.split('-')
        hh, mn, ssnnnnnnZ = hhmnssnnnnnnZ.split(':')
        ss, nnnnnnZ = ssnnnnnnZ.split('.')
        n = nnnnnnZ.strip('Z')

        self = UTC.__new__(
            cls,
            year=int(yyyy),
            month=int(mt),
            day=int(dd),
            hour=int(hh),
            minute=int(mn),
            second=int(ss),
            microsecond=int(n))
        return self


def years_between(t1: UTC, t2: UTC) -> list:
    """bounds included"""
    if t1 >= t2:
        raise ValueError('utmin must be lower than utmax')
    yearmin = t1.ceilyear.year
    yearmax = t2.flooryear.year
    if yearmin > yearmax:
        return []
    years = [UTC(y) for y in range(yearmin, yearmax + 1)]
    return years


def months_between(t1: UTC, t2: UTC) -> list:
    """bounds included"""
    if t1 >= t2:
        raise ValueError('utmin must be lower than utmax')

    print(t1, t2, t2 - t1, (t2 - t1).timestamp)
    if (t2 - t1).timestamp > 50. * YEAR:
        raise ValueError('time period too large')

    monthmin = t1.ceilmonth
    monthmax = t2.floormonth
    if monthmin > monthmax:
        return []

    months = [monthmin]
    while months[-1] < monthmax:
        months.append(UTCFromTimestamp(months[-1].timestamp + 1.).ceilmonth)

    return months


def days_between(t1: UTC, t2: UTC, step: int=1) -> list:
    """bounds included"""
    if t1 >= t2:
        raise ValueError('utmin must be lower than utmax')

    t1_timestamp = t1.timestamp
    t2_timestamp = t2.timestamp

    days = np.arange(t1.flooryear.timestamp, t2.ceilyear.timestamp + 1, step * DAY)
    days = [UTCFromTimestamp(d) for d in days if t1_timestamp <= d <= t2_timestamp]
    return days


def hours_between(t1: UTC, t2: UTC, step: int=1) -> list:
    """bounds included"""
    if t1 >= t2:
        raise ValueError('utmin must be lower than utmax')

    t1_timestamp = t1.timestamp
    t2_timestamp = t2.timestamp

    hours = np.arange(t1.floorday.timestamp, t2.ceilday.timestamp + 1., step * HOUR)
    hours = [UTCFromTimestamp(h) for h in hours if t1_timestamp <= h <= t2_timestamp]
    return hours


def minutes_between(t1: UTC, t2: UTC, step: int=1) -> list:
    """bounds included"""
    if t1 >= t2:
        raise ValueError('utmin must be lower than utmax')

    t1_timestamp = t1.timestamp
    t2_timestamp = t2.timestamp

    minutes = np.arange(t1.floorhour.timestamp, t2.ceilhour.timestamp + 1., step * MINUTE)
    minutes = [UTCFromTimestamp(m) for m in minutes if t1_timestamp <= m <= t2_timestamp]
    return minutes


if __name__ == '__main__':
    utc = UTC(year=2000, month=12, day=31, hour=10)
    utc = UTCFromTimestamp(timestamp=utc.timestamp)
    utc = UTCFromStr(string=str(utc))

    print(utc)

    print(utc.timestamp)
    print(utc.year)
    print(utc.julday)
    print(utc.flooryear)
    print(utc.ceilyear)
    print(utc.floormonth)
    print(utc.ceilmonth)
    print(utc.floorday)
    print(utc.ceilday)

    u1 = UTCFromTimestamp(1)
    u2 = UTCFromTimestamp(2)
    assert u2 > u1
    dt = u2 - u1
    print(dt.timestamp)

    print(years_between(
        UTC(2000, 2), UTC(2010, 2)))

    print(months_between(
        UTC(2000, 2), UTC(2010, 2)))
