#!/usr/bin/env python
import sys, glob, os, time
import numpy as np
import matplotlib.pyplot as plt
from timetools.utc import UTCFromStr, UTCFromTimestamp
from timetools.timetick import timetick


if __name__ == "__main__":

    timeline_file = sys.argv[1]
    now = UTCFromTimestamp(time.time())

    ax = plt.gca()
    with open(timeline_file, 'r') as fid:
        for n, l in enumerate(fid):
            if l.startswith('#'):
                continue
            if "," not in l:
                continue
            start, end, title = l.split('\n')[0].split(',')

            start = UTCFromStr(start)                        
            end = UTCFromStr(end)

            hdl, = ax.plot(
                [start.timestamp, end.timestamp],
                [n, n],
                linewidth=3)
            ax.text(
                start.timestamp,
                n, title,
                ha="left", 
                va="bottom",
                color=hdl.get_color())
    ylim = ax.get_ylim()
    ax.plot(now.timestamp * np.ones(2), ylim, 'r--')
    ax.grid(True)
    timetick(plt.gca())
    plt.show()

