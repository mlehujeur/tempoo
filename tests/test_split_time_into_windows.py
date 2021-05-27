from timetools.utc import UTC, UTCFromTimestamp
from timetools.windows import split_time_into_windows
import pytest


def test_split_time_into_windows():
    starttime = UTC(2017, 4, 18, 5, 17, 32, 189).timestamp
    endtime = UTC(2017, 7, 12, 15, 2, 12, 8753).timestamp
    # print (str(starttime), str(endtime))
    assert endtime > starttime

    with pytest.raises(ValueError):
        # starttime after endtime
        starts, ends = split_time_into_windows(
            endtime, starttime,
            winlen=3600, winstep=3600)

    with pytest.raises(ValueError):
        # unexpected winmode
        starts, ends = split_time_into_windows(
            starttime, endtime,
            winlen=3600, winstep=3600, winmode=155)

    with pytest.raises(ValueError):
        # winstep larger than winlen
        starts, ends = split_time_into_windows(
            starttime, endtime,
            winlen=3600, winstep=2*3600)

    with pytest.raises(ValueError):
        # winlen longer than the time range
        starts, ends = split_time_into_windows(
            starttime, endtime,
            winlen=(endtime - starttime) + 1000.,
            winstep=(endtime - starttime) + 1000.)

    starts, ends = split_time_into_windows(
        starttime, endtime, winlen=3600, winstep=900, winmode=0)
    assert ((ends - starts) == 3600).all()  # winlen constant = 3600
    assert (starts[1:] > starts[:-1]).all() # starts growing
    assert ((starts[1:] - starts[:-1]) == 900).all()  # winstep constant = 900
    assert (starts >= starttime).all()
    assert (starts < endtime).all()
    assert (ends > starttime).all()
    assert (ends <= endtime).all()

    starts, ends = split_time_into_windows(
        starttime, endtime, winlen=3600, winstep=900, winmode=1)
    assert ((ends - starts) == 3600).all()  # winlen constant = 3600
    assert (starts[1:] > starts[:-1]).all() # starts growing
    assert ((starts[1:] - starts[:-1]) == 900).all()  # winstep constant = 900
    assert (starts >= starttime).all()
    assert (starts < endtime).all()
    assert (ends > starttime).all()

    starts, ends = split_time_into_windows(
        starttime, endtime, winlen=3600, winstep=900, winmode=2)
    assert ((ends - starts) == 3600).all()  # winlen constant = 3600
    assert (starts[1:] > starts[:-1]).all() # starts growing
    assert ((starts[1:-1] - starts[:-2]) == 900).all()  # winstep constant = 900 except for last window (shorter)
    assert (starts >= starttime).all()
    assert (starts < endtime).all()
    assert (ends > starttime).all()
    assert (ends <= endtime).all()
    print(UTCFromTimestamp(ends[-1]), endtime)
    assert (ends[-1] == endtime)

    starts, ends = split_time_into_windows(
        starttime, endtime, winlen=3600, winstep=900, winmode=3)
    assert ((ends - starts) == 3600).all()  # winlen constant = 3600
    assert (starts[1:] > starts[:-1]).all() # starts growing
    assert ((starts[1:-1] - starts[:-2]) == 900).all()  # winstep constant = 900 except for last window (longer)
    assert (starts >= starttime).all()
    assert (starts < endtime).all()
    assert (ends > starttime).all()
    assert (ends <= endtime).all()
    print(UTCFromTimestamp(ends[-1]), endtime)
    assert (ends[-1] == endtime)