#!/usr/bin/env python
import sys, glob, os, time
import curses
import numpy as np
import matplotlib.pyplot as plt
from tempoo.utc import UTCFromStr, UTCFromTimestamp
from tempoo.timetick import timetick


if __name__ == "__main__":

    timeline_file = sys.argv[1]

    while True:
        try:
            now = UTCFromTimestamp(time.time())
            fig = plt.figure(figsize=(18, 4))
            fig.subplots_adjust(left=0.3, right=1. - 0.01)
            ax = plt.gca()

            yticks = {}

            with open(timeline_file, 'r') as fid:
                for n, l in enumerate(fid):
                    if l.startswith('#'):
                        continue
                    if "," not in l:
                        continue
                    linenumber, rgb, start, end, title = l.split('\n')[0].split(',')
                    linenumber = int(linenumber)
                    r, g, b = np.asarray(rgb.split('/'), int) / 255.
                    try:
                        start = UTCFromStr(start)                        
                        end = UTCFromStr(end)
                    except:
                        raise Exception(start, end)

                    hdl, = ax.plot(
                        [start.timestamp, end.timestamp],
                        [linenumber, linenumber],
                        '|-',
                        linewidth=3,
                        color=[r, g, b])
                    ax.text(
                        start.timestamp,
                        linenumber, title,
                        ha="left", 
                        va="bottom",
                        color=hdl.get_color())
                    try:
                        yticks[linenumber] += " / " + title
                    except KeyError:
                        yticks[linenumber] = f"{linenumber:03d} {title}"

            ylim = ax.get_ylim()
            ax.plot(now.timestamp * np.ones(2), ylim, 'r--')
            ax.grid(True)
            timetick(ax)

            ax.set_yticks(list(yticks.keys()))
            ax.set_yticklabels(list(yticks.values()))

            plt.ion()
            plt.show()
            ans = input('q=quit, else redraw')

            if ans.lower() == "q":
                break
            plt.close(fig)
        except KeyboardInterrupt:
            sys.exit(1)
