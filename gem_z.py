#!python
# -*- coding: utf-8 -*-
import sys
import time

from src import boot, logger, task
from src.const import FARM_INSTANCE, MAIN_INSTANCE

instance = FARM_INSTANCE

if __name__ == "__main__":
    try:
        boot.init_instance(instance, rok_ready=True)  # TODO: remove rok_ready
        gg = task.GatherGem()
        # gg.prepare()
        gg.get_avail_marches()
        while True:
            gg.gather()
            input("Press Enter to continue...")
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
        sys.exit(1)
    except Exception:
        logger.exception("Exception", stack_info=True)
        time.sleep(30)
        sys.exit(1)
