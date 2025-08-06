#!python
# -*- coding: utf-8 -*-
import sys
import time

try:
    from src import action, boot, const, logger
    from src.const import ActionMode
    from src.rok_profile import RokProfile
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


instance = const.FARM_INSTANCE


if __name__ == "__main__":
    try:
        boot.init_instance(instance)

        profile = RokProfile()
        walker = action.Walker()

        # Declare and register actions to walker
        gatherer = action.Gather()
        use_item = action.UseItems()
        collector = action.Collect()
        reporter = action.Report()

        for action in [
            collector.collect_all,
            use_item.use_24h_gather_boost,
            reporter.collect_info,
            gatherer.gather,
        ]:
            walker.register_action(action)

        # Run with action mode
        action_mode = profile.action_mode
        # action_mode = ActionMode.CHARACTER
        match action_mode:
            case ActionMode.CHARACTER:
                walker.walk_character()
            case ActionMode.ACCOUNT:
                walker.walk_account()
            case ActionMode.ALL_ACCOUNTS:
                walker.walk_all()
            case _:
                raise RuntimeError(f"Weird action mode {action_mode}")

        logger.info("Finished !!!")
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
        sys.exit(1)
    except Exception:
        logger.exception("Exception", stack_info=True)
        time.sleep(30)
        sys.exit(1)
