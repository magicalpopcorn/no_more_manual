#!python
# -*- coding: utf-8 -*-
import sys
import time

from src import action, boot, logger
from src.const import MAIN_INSTANCE

instance = MAIN_INSTANCE

if __name__ == "__main__":
    try:
        boot.init_instance(instance)
        gather_gem = action.gather.GatherGem()
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
        sys.exit(1)
    except Exception:
        logger.exception("Exception", stack_info=True)
        time.sleep(30)
        sys.exit(1)
