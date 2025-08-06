#!python
# -*- coding: utf-8 -*-

import sys

from src import boot, ui, vision

FARM_INSTANCE = "farm1"
MAIN_INSTANCE = "main"
instance = FARM_INSTANCE
# instance = MAIN_INSTANCE


def capture():
    # capture button
    # btn = ui.MenuDispatch.BTN_MULTI_CHECKED
    # vision.image.get_image_from_rect(btn, save=True)

    for i in range(1, 6):
        btn = ui.MenuDispatch.get_march_button(i)
        vision.image.get_image_from_rect(btn, save=True)

    # capture fullscreen
    # vision.image.screenshot()
    sys.exit(0)


if __name__ == "__main__":
    boot.init_instance(instance)
    capture()
    sys.exit(0)
