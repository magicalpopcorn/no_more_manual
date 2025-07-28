#!python
# -*- coding: utf-8 -*-
import os
import sys
import time
from pprint import pprint as pp

import pyautogui  # Required to stabilize screenshot accuracy


def init_process():
    sys.stdout.reconfigure(encoding="utf-8")
    logger.info("Starting script")
    privilege.run_as_admin()
    ROKWindow.get()
    logger.info(
        "Client resolution: ({}x{}), DPI scale: {}".format(
            *ROKWindow.get_client_size(), get_system_dpi_scale()
        )
    )
    time.sleep(0.5)
    if not ROKWindow.is_correct_resolution():
        raise Exception("Wrong resolution")


def experiment_if_any():
    logger.info(str(sys.argv))
    if len(sys.argv) >= 2:
        if sys.argv[1] in ("test", "cap", "smoke"):
            match sys.argv[1]:
                case "test":
                    test()
                case "cap":
                    cap()
                case "smoke":
                    smoke_test()
                case _:
                    logger.critical(f"Unknown option {sys.argv[1]}")

            sys.exit(0)


def test():
    """"""
    # with ui.MenuCity():
    #     collector = action.Collect()
    #     collector.purchase_items()

    MARCH_STATUS = element.RectZone("", element.P(1855, 158), element.P(1885, 178))
    vision.ocr.extract_text_from_rect(MARCH_STATUS, save=True)
    time.sleep(2)


def cap():
    # btn = ui.menu_city.MenuMerchant.BTN_REFRESH
    # for btn in ui.menu_city.MenuMerchant.f_bttn():
    # vision.ocr.extract_text_from_rect(btn, save=True)
    time.sleep(0.5)
    vision.screenshot.capture_fullscreen()
    time.sleep(0.5)


def smoke_test():
    profile = RokProfile()
    walker = action.Walker()
    walker.walk_all()


if __name__ == "__main__":
    try:
        from src import action, element, logger, privilege, ui, vision
        from src.const import ActionMode
        from src.dpi import get_system_dpi_scale
        from src.rok_profile import RokProfile
        from src.window import ROKWindow

        DIR_PATH = os.path.dirname(os.path.realpath(__file__))

        init_process()
        experiment_if_any()

        profile = RokProfile()
        walker = action.Walker()

        # Declare and register actions to walker
        gather = action.Gather()
        use_item = action.UseItems()
        collector = action.Collect()

        for action in [
            use_item.use_24h_gather_boost,
            gather.run,
            collector.collect_all,
        ]:
            walker.register_action(action)

        # Run with action mode
        match profile.action_mode:
            case ActionMode.CHARACTER:
                walker.walk_character()
            case ActionMode.ACCOUNT:
                walker.walk_account()
            case ActionMode.ALL_ACCOUNTS:
                walker.walk_all()
            case _:
                raise RuntimeError(f"Weird action mode {profile.action_mode}")

        logger.info("Finished !!!")
    except Exception:
        logger.exception("Exception", stack_info=True)
        sys.exit(1)
