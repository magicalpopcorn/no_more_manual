import datetime
import os
from enum import IntFlag
from pathlib import Path

# Constants
INPUT_MOUSE = 0
RESOLUTION = (1920, 1080)
BASE_SCALE = 1.25  # 125% dpi scaling
# Units
MIL = 1000000  # 1M rss
BIL = 1000 * MIL  # 1B rss

# Time
DURATION_SWITCH_CHARACTER = 15000  # 15s
DURATION_SWITCH_ACCOUNT = 15000  # 15s

FARM_THREAD_POSITION = 1

TIME_EARLY_MORNING = (datetime.time(6, 0), datetime.time(8, 0))
TIME_NIGHT = (datetime.time(20, 0), datetime.time(23, 59))


class MouseEventFlag(IntFlag):
    MOVE = 0x0001
    LEFTDOWN = 0x0002
    LEFTUP = 0x0004
    RIGHTDOWN = 0x0008
    RIGHTUP = 0x0010
    MIDDLEDOWN = 0x0020
    MIDDLEUP = 0x0040
    ABSOLUTE = 0x8000


class ActionMode(IntFlag):
    CHARACTER = 1
    ACCOUNT = 2
    ALL_ACCOUNTS = 3

    DEFAULT = CHARACTER


PROJECT_ROOT = Path(__file__).resolve().parent.parent
