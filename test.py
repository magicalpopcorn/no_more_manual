#!python
# -*- coding: utf-8 -*-

import sys

from src import boot, vision

FARM_INSTANCE = "farm1"
MAIN_INSTANCE = "main"
instance = FARM_INSTANCE
# instance = MAIN_INSTANCE


def test():
    # ui.MenuCity.open()
    # time.sleep(1)
    # ui.MenuMain.open_map_screen()

    # item_user = action.UseItems()
    # item_user.use_item("dei 2f3", ui.MenuItems.BOOST_SHIELD_8)

    # with ui.MenuMerchant() as mm:
    #     logger.debug(f"is open for sell ?? {mm.is_open_for_sell()}")
    #     time.sleep(1)

    # ui.MenuMerchant.scrollup()
    # vision.ocr.extract_text_from_rect(ui.MenuMerchant.RECT_ITEM_TYPE, save=True)
    vision.image.RokImages.BTN_MULTI_CHECKED.as_array()


if __name__ == "__main__":
    boot.init_instance(instance)
    test()
    sys.exit(0)
