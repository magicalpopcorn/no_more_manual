import datetime
from enum import IntFlag
from pathlib import Path

# Constants
RESOLUTION = (1920, 1080)

# Units
MIL = 1000000  # 1M rss
BIL = 1000 * MIL  # 1B rss

FARM_THREAD_POSITION = 1

TIME_EARLY_MORNING = (datetime.time(6, 0), datetime.time(8, 0))
TIME_NIGHT = (datetime.time(20, 0), datetime.time(23, 59))


class ActionMode(IntFlag):
    CHARACTER = 1
    ACCOUNT = 2
    ALL_ACCOUNTS = ACCOUNT | CHARACTER
    DEFAULT = CHARACTER


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROK_PACKAGE = "com.rok.gp.vn"
