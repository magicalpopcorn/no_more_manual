#!python
# -*- coding: utf-8 -*-
import sys
import time

from src import boot, logger, task, ui
from src.const import FARM_INSTANCE, MAIN_INSTANCE
from src.element.swipe_strategy import Direction

instance = MAIN_INSTANCE
rok_ready = False  # Set to True if Rok is ready to use
# rok_ready = True  # For testing purposes, set to True

if __name__ == "__main__":
    try:
        boot.init_instance(instance, rok_ready=rok_ready)
        gg = task.GatherGem()
        gg.execute("main")
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
        sys.exit(1)
    except Exception:
        logger.exception("Exception", stack_info=True)
        time.sleep(30)
        sys.exit(1)
