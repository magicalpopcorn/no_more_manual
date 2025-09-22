import datetime
from enum import IntFlag
from pathlib import Path

# Constants
RESOLUTION = (1920, 1080)

# Units
MIL = 1000000  # 1M rss
BIL = 1000 * MIL  # 1B rss

FARM_THREAD_POSITION = 1

TIME_EARLY_MORNING = (datetime.time(6, 0), datetime.time(9, 0))
TIME_NIGHT = (datetime.time(20, 0), datetime.time(23, 59))


class ActionMode(IntFlag):
    CHARACTER = 1
    ACCOUNT = 2
    ALL_ACCOUNTS = ACCOUNT | CHARACTER
    DEFAULT = CHARACTER


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(PROJECT_ROOT, "tmp", ".data")
RSS_PATH = DATA_DIR / "rss.json"

ROK_PACKAGE = "com.rok.gp.vn"

FARM_INSTANCE = "farm1"
FARM2_INSTANCE = "farm2"
MAIN_INSTANCE = "main"
