import numpy as np
try:
    from obspy.core import UTCDateTime as ut
except ImportError:
    raise ImportError('obspy not installed')


start = ut(1970, 1, 1)
end = ut(2030, 1, 1)

time_values = np.round(np.sort(np.random.rand(10000)) * (end - start) + start.timestamp, 6)

s = ""
with open('data_test.txt', 'w') as fid:
    for t in time_values:
        tt = ut(t)

        fid.write(
            f'{t:.6f} {str(tt)} '\
            f'{tt.year} {tt.month} '\
            f'{tt.day} {tt.julday} {tt.weekday} '\
            f'{tt.hour} {tt.minute} '\
            f'{tt.second} {tt.microsecond}\n')

