from functools import lru_cache
from matplotlib import ticker
from matplotlib.ticker import MaxNLocator, AutoLocator, AutoMinorLocator
from timetools.utc import *
import time
from proton.timer import Timer
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

        assert start_timestamp < end_timestamp
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
        self.maxticks = maxticks

    def tick_values(self, vmin: float, vmax: float):
        """
        return nice tick locations between two dates (timestamps)
        """

        if vmin < 0:
            # this method does not work well for negative times
            # but if the user displays negative times (i.e. before 1970)
            # then it is likely not usefull to display dates
            return AutoLocator().tick_values(vmin, vmax)

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




from matplotlib.ticker import Formatter
class TimeFormatter(Formatter):

    def get_offset(self):
        return self.offset_string

    @lru_cache(maxsize=None)
    def __call__(self, timevalue, pos=None):
        """
        Return the format for tick value *x* at position pos.
        ``pos=None`` indicates an unspecified location.
        """
        utime = UTCFromTimestamp(timevalue)
        offset_string = str(utime)

        if timevalue < 0.:
            # problem with negative times (before 1970)
            ans = f'{round(timevalue, 9)}'
            return ans

        if timevalue % 1.0:
            offset_string = f"{utime.year:04d}-{utime.month:02d}-{utime.day:02d} {utime.hour:02d}:{utime.minute:02d}'"

            # ans = f'{utime.second}.' + f"{timevalue}".split('.')[-1].rstrip('0')
            # ans = f"{utime.second}." + f"{timevalue}''".split('.')[-1].rstrip('0')

            tens_of_seconds = f"{timevalue}".split('.')[-1].rstrip('0')
            dec = float("0." + tens_of_seconds)

            milliseconds = dec * 1e3
            if not milliseconds % 1.:
                ans = f"{milliseconds:.0f}$_{{ms}}$"
            else:
                microseconds = dec * 1e6
                if not microseconds % 1.:
                    ans = f"{microseconds:.0f}$_{{\mu s}}$"
                else:
                    nanoseconds = dec * 1e9
                    if not nanoseconds % 1.:
                        ans = f"{nanoseconds:.0f}$_{{ns}}$"
                    else:
                        ans = f'{utime.second}.{dec}'

        elif utime.second:
            offset_string = f"{utime.year:04d}-{utime.month:02d}-{utime.day:02d} {utime.hour:02d}:{utime.minute:02d}'"

            ans = f"{utime.minute:02d}':" \
                  f'{utime.second:02d}"'

        elif utime.minute:
            offset_string = f"{utime.year:04d}-{utime.month:02d}-{utime.day:02d} {utime.hour:02d}:"

            ans = f"{utime.hour:02d}:" \
                  f"{utime.minute:02d}'"

        elif utime.hour:
            offset_string = f"{utime.year:04d}-{utime.month:02d}-{utime.day:02d}"

            ans = f"{utime.hour:02d}:00'"

        elif utime.day != 1:
            offset_string = f"{utime.year:04d}-{utime.month:02d}"

            ans = f"{utime.day:02d}"
            # if tickposition == 0:
            #     ans += "\n" + MONTHS[utime.month - 1]

        elif utime.julday != 1:
            offset_string = ""

            ans = MONTHS[utime.month - 1]

        elif utime.year != 1970:
            offset_string = ""

            ans = f"{utime.year:04d}"

        else:
            offset_string = ""
            ans = "0"

        if pos == 0:
            # update the offset string
            self.offset_string = offset_string

        return ans


def timetick(ax, axis='x', major=True, minor=True, major_maxticks=10, minor_maxticks=20):
    """
    set the tick locators and formatters for time data
    """
    formatter = TimeFormatter()

    if 'x' in axis:
        ax.xaxis.set_major_formatter(formatter)
        if major:
            ax.xaxis.set_major_locator(TimeLocator(maxticks=major_maxticks))
        if minor:
            ax.xaxis.set_minor_locator(TimeLocator(maxticks=minor_maxticks))

    if 'y' in axis:
        ax.yaxis.set_major_formatter(formatter)
        if major:
            ax.yaxis.set_major_locator(TimeLocator(maxticks=major_maxticks))
        if minor:
            ax.yaxis.set_minor_locator(TimeLocator(maxticks=minor_maxticks))


def MilliTimeFormatter(timevalue, tickposition=None):
    timevalue = round(timevalue * 1e3, 9)

    ans = f"{timevalue}"  # nice number representation

    if timevalue and "." in ans:
        ans = ans.rstrip('0').rstrip('.')

    ans += "$_{ms}$"  # I fear the plot is mis understood otherwhise
    return ans


def millitimetick(ax, axis='x', major=True, minor=True, major_maxticks=5, minor_maxticks=10, fill_label=" [ms]"):
    tf = MilliTimeFormatter

    if 'x' in axis:
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(tf))

        if major:
            # ax.xaxis.set_major_locator(MaxNLocator(major_maxticks))
            ax.xaxis.set_major_locator(AutoLocator())

        if minor:
            ax.xaxis.set_minor_locator(AutoMinorLocator())

        if isinstance(fill_label, str):
            ax.set_xlabel(ax.get_xlabel() + fill_label)

    if 'y' in axis:
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(tf))

        if major:
            ax.yaxis.set_major_locator(AutoLocator())

        if minor:
            ax.yaxis.set_minor_locator(AutoMinorLocator())

        if isinstance(fill_label, str):
            ax.set_ylabel(ax.get_ylabel() + fill_label)


def MicroTimeFormatter(timevalue, tickposition=None):
    timevalue = round(timevalue * 1e6, 9)

    ans = f"{timevalue}"  # nice number representation

    if timevalue and "." in ans:
        ans = ans.rstrip('0').rstrip('.')

    ans += "$_{\mu s}$"  # I fear the plot is mis understood otherwhise

    return ans


def microtimetick(ax, axis='x', major=True, minor=True, major_maxticks=5, minor_maxticks=10, fill_label=" [$\mu s$]"):
    tf = MicroTimeFormatter

    if 'x' in axis:
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(tf))

        if major:
            ax.xaxis.set_major_locator(AutoLocator()) # MaxNLocator(major_maxticks))

        if minor:
            ax.xaxis.set_minor_locator(AutoMinorLocator()) #MaxNLocator(minor_maxticks))

        if isinstance(fill_label, str):
            ax.set_xlabel(ax.get_xlabel() + fill_label)

    if 'y' in axis:
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(tf))

        if major:
            ax.yaxis.set_major_locator(AutoLocator())

        if minor:
            ax.yaxis.set_minor_locator(AutoMinorLocator())

        if isinstance(fill_label, str):
            ax.set_ylabel(ax.get_ylabel() + fill_label)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    start = UTC(2018, 1, 1, 12, 1, 9, 998500)
    end = UTC(2018, 1, 1, 12, 1, 10, 5000)
    t = np.linspace(start.timestamp, end.timestamp, 100000)
    plt.plot(t, t, 'k+')
    timetick(plt.gca(), 'x')
    # plt.setp(plt.gca().get_xticklabels(), rotation=-25, ha="left", va="top")
    plt.gca().grid(True, linestyle=":")
    plt.show()
