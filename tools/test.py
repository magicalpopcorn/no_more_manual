#!python
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.getcwd())
from src import boot, ui, vision
from src.task import gather_gem

FARM_INSTANCE = "farm1"
MAIN_INSTANCE = "main"
instance = FARM_INSTANCE
# instance = MAIN_INSTANCE


def test():
    """Test anything"""
    # vision.image.RokImages.BTN_MULTI_CHECKED.as_array()
    # gatherer = gather_gem.GatherGem()
    # gatherer.gather()
    mhr = ui.MenuHomeResources()
    mhr.open()
    mhr.swipe_right()


if __name__ == "__main__":
    boot.init_instance(instance, rok_ready=True)
    test()
    sys.exit(0)
