#!python
# -*- coding: utf-8 -*-

import os
import sys
import time

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
    # btn = vision.cv.find_template_in_image(
    #     vision.image.TemplateImage("sample/sample_4.png"),
    #     vision.image.TemplateImage("mining_icon.png"),
    # )
    # print(btn)
    # with ui.MenuMerchant() as mm:
    # ui.MenuMerchant.swipe_up()
    # time.sleep(2)
    # img = vision.image.TemplateImage("boost_24h_gather.png")
    # print(vision.cv.find_template_in_image(vision.image.fullscreen_cap(), img, threshold=0.6))
    btn_price = ui.MenuMerchant.search_boost_24_gather()
    if btn_price:
        btn_price.click()


if __name__ == "__main__":
    boot.init_instance(instance, rok_ready=True)
    test()
    sys.exit(0)
