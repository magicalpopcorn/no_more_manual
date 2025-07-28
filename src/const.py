import datetime
from enum import IntFlag
from pathlib import Path

# Constants
RESOLUTION = (1920, 1080)

# Units
MIL = 1000000  # 1M rss
BIL = 1000 * MIL  # 1B rss

# Time
# TODO: Implement smart switch_duration
DURATION_SWITCH_CHARACTER = 20000  # 15s
DURATION_SWITCH_ACCOUNT = 20000  # 15s

FARM_THREAD_POSITION = 1

TIME_EARLY_MORNING = (datetime.time(6, 0), datetime.time(8, 0))
TIME_NIGHT = (datetime.time(20, 0), datetime.time(23, 59))


class ActionMode(IntFlag):
    CHARACTER = 1
    ACCOUNT = 2
    ALL_ACCOUNTS = 3

    DEFAULT = CHARACTER


PROJECT_ROOT = Path(__file__).resolve().parent.parent
