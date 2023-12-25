#!/usr/bin/env python

help_message = """daysofyear (doy) : list days in a year, use grep
    argument 1 : year
"""

if __name__ == "__main__":
    import datetime
    from tempoo.utc import UTC, UTCFromTimestamp, DAY
    import sys

    day_delta = datetime.timedelta(seconds=DAY)
    weekdays = "mon.tue.wed.thu.fri.sat.sun".split('.')
    months = "jan.feb.mar.apr.may.jun.jul.aug.sep.oct.nov.dec".split('.')
    yr = int(sys.argv[1])
    t = UTC(year=yr, month=1, day=1)

    while t.year == yr:
        wd = weekdays[t.weekday]
        month = months[t.month - 1]

        # print("%04.0f %03.0f   %s  %02.0f %s %.0f" % (t.year, t.julday, wd, t.day, month, t.timestamp))
        print(f"{t.year:04d} {t.julday:03d} {wd:s} {t.day:} {month:s} {t.timestamp:.0f}")

        t + datetime.timedelta(seconds=24 * 3600.)
        (t + datetime.timedelta(seconds=24 * 3600.)).timestamp
        t + 24 * 3600.
        t = UTCFromTimestamp((t + datetime.timedelta(seconds=24 * 3600.)).timestamp)
