from typing import Union
import numpy as np

"""
tools related to time windows
"""


def split_time_into_windows(
        starttime: float, endtime: float, 
        winlen: float, winstep: float, 
        winmode: Union[None, int] = 0) \
        -> (np.ndarray, np.ndarray):
    """
    :param starttime: startting time
    :param endtime: ending time
    :param winlen: length of the slidding window, in seconds
    :param winstep: step between slidding windows, in seconds
    :param winmode: window mode, see split_time_into_windows
    :return starttimes, endtimes: arrays of float
    :rtype  starttimes, endtimes: numpy arrays

    winmode None : one window

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

    if winmode is None:
        return np.array([starttime]), np.array([endtime])

    if not 0 < winstep <= winlen:
        raise ValueError("winlen must be lower or equal to winstep")

    if (endtime - starttime) < winlen:
        raise ValueError('winlen ({}) is longer than endtime - starttime ({})'.format(
            winlen, endtime - starttime))

    if winmode == 0:
        starttimes = np.arange(starttime, endtime - winlen, winstep)
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
