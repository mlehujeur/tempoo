import os

# fuck distutils2
version_file = os.path.join(os.path.dirname(__file__), 'version.txt')
with open(version_file, "r") as fh:
    __version__ = fh.read().rstrip('\n')

from timetools.utc import UTC, UTCFromTimestamp, UTCFromStr
from timetools.timetick import timetick