from typing import Optional
from functools import lru_cache
from matplotlib import ticker, axes
from matplotlib.ticker import Formatter, Locator, MaxNLocator, AutoLocator, AutoMinorLocator
from tempoo.utc import *
import numpy as np

MINUTE = 60.
HOUR = 60. * MINUTE
DAY = 24. * HOUR
YEAR = 365.25 * DAY
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


class YearTicker(object):
    """
    An object to find "nice" tick positions in a given year
    """
    def __init__(self, year: int):
        self.year_int: int = year
        self.year_start_utc: UTC = UTC(year=self.year_int, month=1, day=1, hour=0)
        self.year_end_utc: UTC = UTC(year=self.year_int + 1, month=1, day=1, hour=0)
        self.year_start_timestamp: float = self.year_start_utc.timestamp
        self.year_end_timestamp: float = self.year_end_utc.timestamp - 1e-9

    def months(self) -> list:
        """list the month timestamps in this year"""
        return [UTC(year=self.year_int, month=m, day=1, hour=0).timestamp
                for m in range(1, 13)]

    def mondays(self) -> list:
        """list the monday timestamps in this year"""
        t = self.year_start_utc
        mondays = []
        while t < self.year_end_utc:
            if t.weekday == 0:
                mondays.append(t.timestamp)
            t += 24. * 3600.
        return mondays

    def days(self) -> list:
        """list the day timestamps in this year"""
        last_day_of_year = (self.year_end_utc - 12. * 3600.).julday
        return [UTCFromJulday(year=self.year_int, julday=j, hour=0).timestamp
                for j in range(1, last_day_of_year)]

    @staticmethod
    def add_to_ticks(old_ticks, new_ticks, start_timestamp, end_timestamp):
        """update a list of ticks (timestamps) between two dates"""

        ticks = np.concatenate((old_ticks, new_ticks))
        ticks = np.unique(ticks)
        b, e = np.searchsorted(ticks, [start_timestamp, end_timestamp])
        ticks = ticks[b:e]
        #ticks = ticks[(ticks >= start_timestamp) & (ticks <= end_timestamp)]

        return ticks

    def ticks(self, start_timestamp: float, end_timestamp: float):
        """
        an generator which returns a list of tick values (timestamps)
        between two times.
        each iteration of the generator increases the precision
        user needs to close the generator when he has reached the desired level of precision
        """
        ticks = []

        if not start_timestamp < end_timestamp:
            start_timestamp, end_timestamp = end_timestamp, start_timestamp
        # ==== window outside this year?
        if end_timestamp < self.year_start_timestamp or \
           start_timestamp > self.year_end_timestamp:
            # window not in this year
            while True:
                yield ticks

        # ==== do not overlap the previous or next years
        start_timestamp = max([self.year_start_timestamp, start_timestamp])
        end_timestamp = min([self.year_end_timestamp, end_timestamp])
        assert self.year_start_timestamp <= start_timestamp < end_timestamp <= self.year_end_timestamp, \
            (str(UTCFromTimestamp(self.year_start_timestamp)),
             str(UTCFromTimestamp(start_timestamp)),
             str(UTCFromTimestamp(end_timestamp)),
             str(UTCFromTimestamp(self.year_end_timestamp)))

        # ==== year precision
        for prec in [1000, 500, 100, 50, 20, 10, 5, 2]:
            if self.year_int % prec:
                yield []  # avoid not round years first
            else:
                # this is a round year according to precision
                ticks = [self.year_start_timestamp]
                yield ticks

        # ==== month precision
        months = self.months()
        for prec in [6, 3, 1]:
            ticks = self.add_to_ticks(ticks, months[::prec], start_timestamp, end_timestamp)
            yield ticks

        # ==== week precision
        mondays = self.mondays()
        for prec in [2, 1]:
            ticks = self.add_to_ticks(ticks, mondays[::prec], start_timestamp, end_timestamp)
            yield ticks

        # ==== day precision
        days = self.days()
        for prec in [1]:
            ticks = self.add_to_ticks(ticks, days[::prec], start_timestamp, end_timestamp)
            yield ticks

        # ===========
        # ==== hour precision
        # no need to get all the hours in the year
        floorday_start_timestamp = UTCFromTimestamp(start_timestamp).floorday.timestamp
        ceilday_end_timestamp = UTCFromTimestamp(end_timestamp).ceilday.timestamp

        # do not overlap with the next year or previous year
        floorday_start_timestamp = max([self.year_start_timestamp, floorday_start_timestamp])
        ceilday_end_timestamp = min([self.year_end_timestamp, ceilday_end_timestamp])
        assert floorday_start_timestamp < ceilday_end_timestamp

        hours = np.arange(floorday_start_timestamp, ceilday_end_timestamp + 1., 3600.)
        for prec in [12, 6, 3, 1]:
            ticks = self.add_to_ticks(ticks, hours[::prec], start_timestamp, end_timestamp)
            yield ticks

        minutes = np.arange(floorday_start_timestamp, ceilday_end_timestamp + 1., 60.)
        for prec in [30, 10, 2, 1]:
            ticks = self.add_to_ticks(ticks, minutes[::prec], start_timestamp, end_timestamp)
            yield ticks

        seconds = np.arange(floorday_start_timestamp, ceilday_end_timestamp + 1., 1.)
        for prec in [30, 10, 5, 1]:
            ticks = self.add_to_ticks(ticks, seconds[::prec], start_timestamp, end_timestamp)
            yield ticks

        # ===========
        # ==== subsecond precision
        # no need to get all the seconds in the day
        floorminute_start_timestamp = UTCFromTimestamp(start_timestamp).floorminute.timestamp
        ceilminute_end_timestamp = UTCFromTimestamp(end_timestamp).ceilminute.timestamp
        number_of_minutes = int(round((ceilminute_end_timestamp - floorminute_start_timestamp) / 60.))

        # milliseconds = np.arange(floorminute_start_timestamp, ceilminute_end_timestamp + 1., 1e-3)  # NOOOOOOOO
        milliseconds = floorminute_start_timestamp + np.arange(number_of_minutes * 60000) * 1e-3
        for prec in [500, 100, 50, 25, 5, 1]:
            ticks = self.add_to_ticks(ticks, milliseconds[::prec], start_timestamp, end_timestamp)
            yield ticks

        floorsecond_start_timestamp = np.floor(start_timestamp)
        ceilsecond_end_timestamp = np.ceil(end_timestamp)
        number_of_seconds = int(round(ceilsecond_end_timestamp - floorsecond_start_timestamp))

        microseconds = floorsecond_start_timestamp + np.arange(number_of_seconds * 1000000) * 1e-6
        for prec in [500, 100, 50, 25, 5, 1]:
            ticks = self.add_to_ticks(ticks, microseconds[::prec], start_timestamp, end_timestamp)
            yield ticks


class TimeLocator(ticker.LinearLocator):
    def __init__(self, maxticks=5):
        ticker.LinearLocator.__init__(self)
        self.maxticks = maxticks

    def tick_values(self, vmin: float, vmax: float):
        """
        return nice tick locations between two dates (timestamps)
        """

        # if vmin < 0:
        #     # this method does not work well for negative times
        #     # but if the user displays negative times (i.e. before 1970)
        #     # then it is likely not usefull to display dates
        #     return AutoLocator().tick_values(vmin, vmax)

        utmin = UTCFromTimestamp(vmin)
        utmax = UTCFromTimestamp(vmax)

        tick_generators = []
        for year in range(utmin.flooryear.year, utmax.ceilyear.year + 1):
            # initiate one tick generator per year between the two boundary dates
            tick_generator = YearTicker(year).ticks(vmin, vmax)
            tick_generators.append(tick_generator)

        ticks = []  # to store the tick positions (timestamps)
        while True:
            try:
                # prepare the next list of ticks (with one more level of accuracy)
                next_ticks = []
                for tick_generator in tick_generators:
                    year_ticks = next(tick_generator)  # get the next of list of ticks for this year
                    next_ticks.append(year_ticks)
                    # print('**', next_ticks)
                next_ticks = list(np.hstack(next_ticks))
                if len(ticks) and (len(next_ticks) > self.maxticks):
                    # if the desired level of accuracy has been exceeded
                    # ignore next_ticks and return ticks
                    break
                ticks = next_ticks  # move to new level of accuracy
                # for _ in ticks:
                #     print(str(UTCFromTimestamp(_)))
                # print(np.round(np.array(ticks)[1:] - np.array(ticks)[:-1],4))
                # print('')

            except StopIteration as err:
                # max accuracy reached for at least one year.
                break

        for tick_generator in tick_generators:
            tick_generator.close()

        return ticks


class CalendarTimeFormatter(Formatter):
    offset_string: str = ""
    range_separator = "~"

    def __init__(self, force_offset_string: Optional[str]=None, *args, **kwargs):
        Formatter.__init__(self, *args, **kwargs)
        self.force_offset_string = force_offset_string

    def get_offset(self):
        ans = self.offset_string
        if self.force_offset_string is not None:
            ans = self.force_offset_string

        return ans

    def format_ticks(self, timevalues):
        self.set_locs(timevalues)
        utimes = [UTCFromTimestamp(timevalue) for timevalue in timevalues]
        time_range = timevalues[-1] - timevalues[0]
        utimes_str = [str(_) for _ in utimes]
        self.offset_string = ""

        # ===== strip the left side of the tick labels
        if utimes[0].year == utimes[-1].year:
            utimes_str = self.format_ticks_same_year(utimes, utimes_str)

        elif time_range < YEAR:
            utimes_str = self.format_ticks_cross_year(time_range, utimes, utimes_str)

        # ===== strip the right side of the tick labels
        utimes_str = self.strip_ticklabels(utimes_str)

        return utimes_str

    def format_ticks_same_year(self, utimes, utimes_str):
        # year is the same for all ticks; move year name to offset_string and remove it from ticklabels
        self.offset_string = f"{utimes[0].year:04d}"
        utimes_str = [_[5:] for _ in utimes_str]
        if utimes[0].month == utimes[-1].month:
            # month is the same for all ticks; move it name to offset_string and remove it from ticklabels
            self.offset_string += f"-{utimes[0].month:02d}"
            utimes_str = [_[3:] for _ in utimes_str]

            if utimes[0].day == utimes[-1].day:
                # day is the same for all ticks; move it name to offset_string and remove it from ticklabels
                self.offset_string += f"-{utimes[0].day:02d}"
                utimes_str = [_[3:] for _ in utimes_str]

                if utimes[0].hour == utimes[-1].hour:
                    # hour is the same for all ticks; move it name to offset_string and remove it from ticklabels
                    self.offset_string += f"T{utimes[0].hour:02d}"
                    utimes_str = [":".join(_.split(':')[1:]) for _ in utimes_str]

                    if utimes[0].minute == utimes[-1].minute:
                        # minute is the same for all ticks;
                        # move it name to offset_string and remove it from ticklabels
                        self.offset_string += f":{utimes[0].minute:02d}"
                        utimes_str = [_.split(':')[-1] for _ in utimes_str]

                        if utimes[0].second == utimes[-1].second:
                            # second is the same for all ticks;
                            # move it name to offset_string and remove it from ticklabels
                            self.offset_string += f":{utimes[0].second:02d}"
                            utimes_str = ["." + _.split('.')[1] for _ in utimes_str]
        return utimes_str

    def format_ticks_cross_year(self, time_range, utimes, utimes_str):
        # year is not the same for all ticks
        # maybe we are looking a small time range but
        # overlapping the start of the year
        # year precision is not needed
        # => move start and end times to offset_string
        # and display only the required accuracy in tick labels
        utime_first_str = str(utimes[0])
        utime_last_str = str(utimes[-1])
        sep = self.range_separator
        self.offset_string = f"{utime_first_str[:4]}{sep}{utime_last_str[:4]}"
        utimes_str = [_[5:] for _ in utimes_str]
        if time_range < 30 * DAY:

            self.offset_string = f"{utime_first_str[:7]}{sep}{utime_last_str[:7]}"
            utimes_str = [_[3:] for _ in utimes_str]

            if time_range < DAY:

                self.offset_string = f"{utime_first_str[:10]}{sep}{utime_last_str[:10]}"
                utimes_str = [_[3:] for _ in utimes_str]

                if time_range < HOUR:

                    self.offset_string = f"{utime_first_str[:13]}{sep}{utime_last_str[:13]}"
                    utimes_str = [_[3:] for _ in utimes_str]

                    if time_range < MINUTE:

                        self.offset_string = f"{utime_first_str[:16]}{sep}{utime_last_str[:16]}"
                        utimes_str = [_[3:] for _ in utimes_str]

                        if time_range < 1.:
                            self.offset_string = f"{utime_first_str[:19]}{sep}{utime_last_str[:19]}"
                            utimes_str = [_[2:] for _ in utimes_str]
        return utimes_str

    def strip_ticklabels(self, utimes_str):
        # count the number of non-zero digits after "."

        ndigits = [len(_.split('.')[1].rstrip("Z").rstrip('0')) for _ in utimes_str]
        ndigit = max(ndigits)
        if ndigit > 0:
            # remove sub second zeros,
            # make sure all ticks have the same number of digits after .
            utimes_str = [_.split('.')[0] + "." + _.split('.')[1][:ndigit] for _ in utimes_str]
        else:
            # remove 00...0Z on the right hand side of the label
            utimes_str = [_.rstrip('Z').rstrip('0').rstrip('.') for _ in utimes_str]

            if np.all([_.endswith(':00') for _ in utimes_str]):
                # seconds are all ":00",  not needed
                utimes_str = [_[:-3] for _ in utimes_str]

                if np.all([_.endswith(':00') for _ in utimes_str]):
                    # minutes not needed
                    utimes_str = [_[:-3] for _ in utimes_str]

                    if np.all([_.endswith('T00') for _ in utimes_str]):
                        # hours not needed
                        utimes_str = [_[:-3] for _ in utimes_str]

                        if np.all([_.endswith('-01') for _ in utimes_str]):
                            # days not needed
                            utimes_str = [_[:-3] for _ in utimes_str]

                            if np.all([_.endswith('-01') for _ in utimes_str]):
                                # months not needed
                                utimes_str = [_[:-3] for _ in utimes_str]
        return utimes_str

    def __call__(self, timevalue, pos=None):
        # format the dynamic ticker on top of the window
        ans = str(UTCFromTimestamp(timevalue))
        if self.range_separator in self.offset_string:
            beg, end = self.offset_string.split(self.range_separator)
            ans = ans.split(beg)[-1].split(end)[-1]

        else:
            ans = ans.split(self.offset_string)[-1]
        return ans


class JuldayTimeFormatter(CalendarTimeFormatter):

    def format_ticks(self, timevalues):
        self.set_locs(timevalues)
        utimes = [UTCFromTimestamp(timevalue) for timevalue in timevalues]
        time_range = timevalues[-1] - timevalues[0]
        utimes_str = [f"{_.year:04d}-{_.julday:03d}T{_.hour:02d}:{_.minute:02d}:{_.second:02d}.{_.microsecond*1e6:06.0f}Z" for _ in utimes]
        self.offset_string = ""

        # ===== strip the left side of the tick labels
        if utimes[0].year == utimes[-1].year:
            utimes_str = self.format_ticks_same_year(utimes, utimes_str)

        elif time_range < YEAR:
            utimes_str = self.format_ticks_cross_year(time_range, utimes, utimes_str)

        # ===== strip the right side of the tick labels
        # count the number of non-zero digits after "."
        utimes_str = self.strip_ticklabels(utimes_str)

        return utimes_str

    def strip_ticklabels(self, utimes_str):
        ndigits = [len(_.split('.')[1].rstrip("Z").rstrip('0')) for _ in utimes_str]
        ndigit = max(ndigits)
        if ndigit > 0:
            # remove sub second zeros,
            # make sure all ticks have the same number of digits after .
            utimes_str = [_.split('.')[0] + "." + _.split('.')[1][:ndigit] for _ in utimes_str]
        else:
            # remove 00...0Z on the right hand side of the label
            utimes_str = [_.rstrip('Z').rstrip('0').rstrip('.') for _ in utimes_str]

            if np.all([_.endswith(':00') for _ in utimes_str]):
                # seconds are all ":00",  not needed
                utimes_str = [_[:-3] for _ in utimes_str]

                if np.all([_.endswith(':00') for _ in utimes_str]):
                    # minutes not needed
                    utimes_str = [_[:-3] for _ in utimes_str]

                    if np.all([_.endswith('T00') for _ in utimes_str]):
                        # hours not needed
                        utimes_str = [_[:-3] for _ in utimes_str]

                        if np.all([_.endswith('-01') for _ in utimes_str]):
                            # days not needed
                            utimes_str = [_[:-3] for _ in utimes_str]

                            if np.all([_.endswith('-01') for _ in utimes_str]):
                                # months not needed
                                utimes_str = [_[:-3] for _ in utimes_str]
        return utimes_str

    def format_ticks_same_year(self, utimes, utimes_str):
        # year is the same for all ticks; move year name to offset_string and remove it from ticklabels
        self.offset_string = f"{utimes[0].year:04d}"
        utimes_str = [_[5:] for _ in utimes_str]
        if utimes[0].julday == utimes[-1].julday:
            # julday is the same for all ticks; move it name to offset_string and remove it from ticklabels
            self.offset_string += f"-{utimes[0].julday:03d}"
            utimes_str = [_[3:] for _ in utimes_str]

            if utimes[0].hour == utimes[-1].hour:
                # hour is the same for all ticks; move it name to offset_string and remove it from ticklabels
                self.offset_string += f"T{utimes[0].hour:02d}"
                utimes_str = [":".join(_.split(':')[1:]) for _ in utimes_str]

                if utimes[0].minute == utimes[-1].minute:
                    # minute is the same for all ticks;
                    # move it name to offset_string and remove it from ticklabels
                    self.offset_string += f":{utimes[0].minute:02d}"
                    utimes_str = [_.split(':')[-1] for _ in utimes_str]

                    if utimes[0].second == utimes[-1].second:
                        # second is the same for all ticks;
                        # move it name to offset_string and remove it from ticklabels
                        self.offset_string += f":{utimes[0].second:02d}"
                        utimes_str = ["." + _.split('.')[1] for _ in utimes_str]
        return utimes_str


class SubSecTimeFormatter(Formatter):
    offset_string: str = r"$^{*}$[s]"
    tick_extension: str = r"$^{*}$"
    scale: float = 1.0

    def get_offset(self):
        return self.offset_string

    def format_ticks(self, timevalues):

        timevalues = np.round(np.asarray(timevalues, float) * self.scale, 9)
        self.set_locs(timevalues)
        ans = []
        for timevalue in timevalues:
            timevalue_str = f"{timevalue}"   # nice number representation

            if timevalue and "." in timevalue_str:
                timevalue_str = timevalue_str.rstrip('0').rstrip('.')

            timevalue_str += self.tick_extension  # I fear the plot is misunderstood otherwhise
            ans.append(timevalue_str)
        return ans

    def __call__(self, timevalue, pos=None):
        # format the dynamic ticker on top of the window
        ans = f"{timevalue}"
        return ans


class MilliSecTimeFormatter(SubSecTimeFormatter):
    offset_string: str = "$ [ms] $" # r"$^{*}$[ms]"
    tick_extension: str = "" # r"$^{*}$"
    scale: float = 1e3


class MicroSecTimeFormatter(SubSecTimeFormatter):
    offset_string: str = r"$ [\mu s] $"
    tick_extension: str = ""  # r"$^{*}$"
    scale: float = 1e6


def xy_ticker(
        ax,  # : axes._subplots.Subplot,
        axis: str = 'x',
        major_locator: Union[Locator, None] = None,
        minor_locator: Union[Locator, None] = None,
        formatter: Formatter = None):

    """
    set the tick locators and formatters for time data
    :param ax: the ax to modify
    :param axis: "x" or "y"
    :param major:
    :param minor:
    :param major_maxticks:
    :param minor_maxticks:
    :param formatter_class: CalendarTimeFormatter, MilliSecFormatter, MicroSecFormatter
    """

    if 'x' in axis:
        ax.xaxis.set_major_formatter(formatter)
        if major_locator is not None:
            ax.xaxis.set_major_locator(major_locator)
        if minor_locator is not None:
            ax.xaxis.set_minor_locator(minor_locator)

    if 'y' in axis:
        ax.yaxis.set_major_formatter(formatter)
        if major_locator is not None:
            ax.yaxis.set_major_locator(major_locator)
        if minor_locator is not None:
            ax.yaxis.set_minor_locator(minor_locator)


def timetick(ax,  # : axes._subplots.Subplot,
             axis: str='x',
             major: bool=True,
             minor: bool=True,
             major_maxticks: int=10,
             minor_maxticks: int=20,
             force_offset_string: Optional[str]=None):

    xy_ticker(
        ax=ax,
        axis=axis,
        major_locator=TimeLocator(maxticks=major_maxticks) if major else None,
        minor_locator=TimeLocator(maxticks=minor_maxticks) if minor else None,
        formatter=CalendarTimeFormatter(force_offset_string=force_offset_string))


def juldaytimetick(ax,  # : axes._subplots.Subplot,
             axis: str='x',
             major: bool=True,
             minor: bool=True,
             major_maxticks: int=10,
             minor_maxticks: int=20):

    xy_ticker(
        ax=ax,
        axis=axis,
        major_locator=TimeLocator(maxticks=major_maxticks) if major else None,
        minor_locator=TimeLocator(maxticks=minor_maxticks) if minor else None,
        formatter=JuldayTimeFormatter())

def millitimetick(
        ax,  # : axes._subplots.Subplot,
        axis: str='x',
        major: bool=True,
        minor: bool=True):

    xy_ticker(
        ax=ax,
        axis=axis,
        major_locator=AutoLocator() if major else None,
        minor_locator=AutoMinorLocator() if minor else None,
        formatter=MilliSecTimeFormatter())


def microtimetick(ax,  # : axes._subplots.Subplot,
             axis: str='x',
             major: bool=True,
             minor: bool=True,
             major_maxticks: int=10,
             minor_maxticks: int=20):

    xy_ticker(
        ax=ax,
        axis=axis,
        major_locator=AutoLocator() if major else None,
        minor_locator=AutoMinorLocator() if minor else None,
        formatter=MicroSecTimeFormatter())


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    start = UTC(2016, 1, 1, 12, 1, 9, 998500)
    end = UTC(2018, 1, 1, 12, 1, 10, 5000)
    t = np.linspace(start.timestamp, end.timestamp, 100000)
    plt.plot(t, t, 'k+')

    timetick(plt.gca(), 'x')
    #microtimetick(plt.gca(), 'y')
    juldaytimetick(plt.gca(), 'y')

    # plt.setp(plt.gca().get_xticklabels(), rotation=-25, ha="left", va="top")
    plt.gca().grid(True, linestyle=":")
    plt.show()
