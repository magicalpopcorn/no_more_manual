#!python
# -*- coding: utf-8 -*-

import os
import sys
import time

sys.path.insert(0, os.getcwd())
from src import boot, element, task, ui, vision
from src.task import gather_gem

FARM_INSTANCE = "farm1"
MAIN_INSTANCE = "main"
instance = FARM_INSTANCE
# instance = MAIN_INSTANCE


def test():
    """Test anything"""
    a = task.Assist()
    # a.execute("2f4")
    element.CENTER_POINT.click(verify=ui.MenuMain.is_btn_assist_visible)


if __name__ == "__main__":
    boot.init_instance(sys.argv[1], rok_ready=True)
    test()
    sys.exit(0)
