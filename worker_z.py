#!python
# -*- coding: utf-8 -*-
import sys
import time

start_time = time.time()
print("Starting import...")
try:
    from src import boot, const, logger, task
    from src.agent.walker import Walker
    from src.const import ActionMode
    from src.rok_profile import RokProfile
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
else:
    import_time = time.time() - start_time
    print(f"Import time: {import_time:.4f} seconds")


instance = const.FARM_INSTANCE


if __name__ == "__main__":
    try:
        logger.setup_logger()
        start_time = time.time()
        boot.init_instance(instance)

        profile = RokProfile()
        mode = ActionMode(profile.action_mode)
        # mode = ActionMode.CHARACTER
        walker = Walker(mode)

        # Declare and register tasks to walker
        gatherer = task.Gather()
        use_item = task.UseItems()
        collector = task.Collect()
        reporter = task.Report()

        for task in [
            collector.claim_alliance_rss,
            collector.purchase_items,
            use_item.use_24h_gather_boost,
            reporter.collect_info,
            gatherer.gather,
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
        total_time = time.time() - start_time
        logger.info(f"Total time: {total_time:.4f} seconds")
        logger.info(f"Log saved at {logger.LOG_FOLDER / 'macro.log'}")
        time.sleep(60)
