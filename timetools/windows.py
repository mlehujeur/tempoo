from typing import Union
import numpy as np

"""
tools related to time windows
"""


def split_time_into_windows(
        starttime: float, endtime: float, 
        winlen: float = 0.,
        winstep: float = 0.,
        winmode: int = 0) \
        -> (np.ndarray, np.ndarray):
    """
    :param starttime: startting time
    :param endtime: ending time
    :param winlen: length of the slidding window, in seconds
    :param winstep: step between slidding windows, in seconds
    :param winmode: window mode, see split_time_into_windows
    :return starttimes, endtimes: arrays of float
    :rtype  starttimes, endtimes: numpy arrays

    winmode 0 : last samples lost
    s                  e
    ********************
    --------           |
         --------      |
              -------- |
                      xx

    winmode 1 : endtime applies to the beginning of the window
    s                  e
    ********************
    --------           |
      --------         |
        --------       |
          --------     |
            --------   |
              -------- |
                --------
                  --------
                    --------
                      --------

    winmode 2 : reduce winstep for last window, add one more window
    s                  e
    ********************
    --------           |
         --------      |
              -------- |
                --------  => overlap longer for this last window


    winmode 3 : increase winstep for last window
    s                  e
    ********************
    ----------         |
        ----------     |
              ----------   => overlap shorter for this last window

    """
    if endtime <= starttime:
        raise ValueError("starttime must be lower than endtime")

    if not 0 < winstep <= winlen:
        raise ValueError("winlen must be lower or equal to winstep")

    if (endtime - starttime) < winlen:
        raise ValueError('winlen ({}) is longer than endtime - starttime ({})'.format(
            winlen, endtime - starttime))

    if winmode == 0:
        eps = winlen / 1000.
        starttimes = np.arange(starttime, endtime - winlen + eps, winstep)
        endtimes = starttimes + winlen

    elif winmode == 1:
        starttimes = np.arange(starttime, endtime, winstep)
        endtimes = starttimes + winlen

    elif winmode == 2:
        starttimes = np.arange(starttime, endtime - winlen, winstep)
        endtimes = starttimes + winlen
        if endtimes[-1] < endtime:
            # add one more window
            starttimes = np.concatenate((starttimes, [endtime - winlen]))
            endtimes = np.concatenate((endtimes, [endtime]))

    elif winmode == 3:
        starttimes = np.arange(starttime, endtime - winlen, winstep)
        endtimes = starttimes + winlen
        if len(endtimes) > 1:
            if endtimes[-1] < endtime:
                # shift last window
                endtimes[-1] = endtime
                starttimes[-1] = endtime - winlen
        elif len(endtimes) == 1:
            # recall with mode 2 : i.e. add one window
            return split_time_into_windows(starttime, endtime, winlen, winstep, winmode=2)

    else:
        raise ValueError('unexpected mode number')

    return starttimes, endtimes


def split_time_into_windows_best(
        starttime: float, endtime: float,
        winlen: float, winstep: float) \
        -> (np.ndarray, np.ndarray):
    """
    test the four window modes 0 1 2 3 above
    returns the result time windows for the mode
    with best fit to the required parameters
        in terms of deviation to winlen, winstep, loss of data or overlapp missing part of the signal

    """

    winmodes = np.arange(4)
    option_costs = np.zeros(len(winmodes), float)
    outputs = []
    for nmode, winmode in enumerate(winmodes):
        starttimes, endtimes = split_time_into_windows(
            starttime=starttime,
            endtime=endtime,
            winlen=winlen,
            winstep=winstep,
            winmode=winmode)

        deviation_to_winlen = (np.abs((endtimes - starttimes) - winlen) / winlen).sum()
        deviation_to_winstep = (np.abs((starttimes[1:] - starttimes[:-1]) - winstep) / winstep).sum()
        data_loss = (max([0., starttimes[0] - starttime]) + max([0., endtime - endtimes[-1]])) / (endtime - starttime)
        overlap_null = (max([0., starttime - starttimes[0]]) + max([0., endtimes[-1] - endtime])) / (endtime - starttime)

        option_costs[nmode] = \
            deviation_to_winlen + \
            deviation_to_winstep + \
            data_loss + \
            overlap_null
        outputs.append((starttimes, endtimes))

    i_best_winmode = np.argmin(option_costs)
    starttimes, endtimes = outputs[i_best_winmode]
    # print(f'best mode : {winmodes[i_best_winmode]}')
    return starttimes, endtimes


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    while True:
        start = np.random.rand()
        end = start + np.random.rand()
        winlen = (end - start) / 2.  # * np.random.rand()
        winstep = winlen / 2.  # * np.random.rand()

        plt.gca().cla()
        plt.plot([start, end], [-1, -1], 'k')

        for winmode in range(4):
            starttimes, endtimes = split_time_into_windows(
                starttime=start,
                endtime=end,
                winlen=winlen,
                winstep=winstep,
                winmode=winmode)

            for nwin, (winstart, winend) in enumerate(zip(starttimes, endtimes)):
                plt.plot([winstart, winend], [winmode + 0.1*nwin, winmode + 0.1*nwin],
                         label=winmode if nwin == 0 else None)

        starttimes, endtimes = split_time_into_windows_best(
            starttime=start,
            endtime=end,
            winlen=winlen,
            winstep=winstep)

        plt.gca().grid(True)
        plt.legend()
        plt.show()