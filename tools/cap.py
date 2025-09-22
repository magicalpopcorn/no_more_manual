#!python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.getcwd())
from src import boot, ui, vision

FARM_INSTANCE = "farm1"
MAIN_INSTANCE = "main"
# instance = FARM_INSTANCE
instance = MAIN_INSTANCE


def capture():
    if len(sys.argv) > 2:
        if sys.argv[2] == "full":
            # capture full screen
            while True:
                vision.image.screenshot()
                input()

    # capture button
    btn = ui.MenuMain.CITY_INFO_ICON
    vision.image.get_image_from_rect(btn, save=True)

    return


if __name__ == "__main__":
    boot.init_instance(instance, rok_ready=True)
    capture()
    sys.exit(0)
