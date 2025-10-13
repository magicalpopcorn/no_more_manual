#!python
# -*- coding: utf-8 -*-
import sys
import time

try:
    from src.lib import boot, const, logger, task
    from src.lib.agent.walker import Walker
    from src.lib.const import ActionMode
    from src.lib.rok_profile import RokProfile
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


instance = const.FARM_INSTANCE


if __name__ == "__main__":
    try:
        boot.init_instance(instance)

        profile = RokProfile()
        mode = ActionMode(profile.action_mode)
        # mode = ActionMode.ACCOUNT
        walker = Walker(mode)

        # Declare and register tasks to walker
        assistant = task.Assist()

        for task in [
            assistant.transport_rss,
        ]:
            walker.register_task(task)

        logger.info(f"Running walker with mode: {mode}")
        walker.execute()

        logger.info("Finished !!!")
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
        sys.exit(1)
    except Exception:
        logger.exception("Exception", stack_info=True)
        sys.exit(1)
    finally:
        logger.info(f"Log saved at {logger.LOG_FOLDER / 'macro.log'}")
        time.sleep(60)
