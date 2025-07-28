import re
import time

from src import logger
from src.element import Button, Distance, P, RectZone
from src.vision import ocr

from .base_menu import _Menu
from .menu_main import MenuMain


class MenuCity(_Menu):
    BTN_FOOD_DEPOSITE = Button("FOOD_DEPOSITE", P(1215, 775), P(1300, 820))
    BTN_WOOD_DEPOSITE = Button("WOOD_DEPOSITE", P(1315, 696), P(1400, 745))
    BTN_STONE_DEPOSITE = Button("STONE_DEPOSITE", P(1415, 640), P(1500, 690))
    BTN_GOLD_DEPOSITE = Button("GOLD_DEPOSITE", P(1515, 555), P(1600, 600))

    BTN_COURIER_STATION = Button("Courier_Station", P(1040, 370), P(1170, 450))
    BTN_COURIER_MERCHANT = Button("Courier_Merchant", P(1185, 530), P(1275, 620))

    _is_opened = False

    @classmethod
    def open(cls):
        super().open()
        MenuMain.navigate_to_map_screen()
        MenuMain.BTN_HOME.click()
        cls._is_opened = True

    @classmethod
    def close(cls):
        if cls._is_opened:
            MenuMain.BTN_HOME.click()
        cls._is_opened = False

    @classmethod
    def get_deposite_buttons(cls):
        return (
            cls.BTN_FOOD_DEPOSITE,
            cls.BTN_WOOD_DEPOSITE,
            cls.BTN_STONE_DEPOSITE,
            cls.BTN_GOLD_DEPOSITE,
        )

    @classmethod
    def is_open(cls):
        return cls._is_opened


class MenuMerchant(_Menu):
    MENU_WINDOW = RectZone("Mechant Menu", P(555, 220), P(1470, 860))
    MERCHANT_TITLE = RectZone("Merchant Title", P(665, 236), P(1255, 270))

    BTN_REFRESH = Button("Refresh", P(1245, 305), P(1440, 370))

    # captured in row 1 Resources
    ITEM_1 = Button("Item_1", P(705, 580), P(825, 610))
    ITEM_2 = Button("Item_2", P(897, 580), P(1018, 610))
    ITEM_3 = Button("Item_3", P(1090, 580), P(1210, 610))
    ITEM_4 = Button("Item_4", P(1280, 580), P(1400, 610))

    _ITEM_8 = Button("Item_8", P(1280, 700), P(1400, 820))

    ITEMS = (ITEM_1, ITEM_2, ITEM_3, ITEM_4)

    @classmethod
    def open(cls):
        super().open()
        if not MenuCity.is_open():
            raise RuntimeError("Not in city")

        MenuCity.BTN_COURIER_STATION.click()
        MenuCity.BTN_COURIER_MERCHANT.click()

    @classmethod
    def scrollup_for_next(cls):
        """I set up some magic number here
        offset_x=(25, 50) -> drag to right direction
        offset_y=(-267,) -> drag to upper around 265-270 pixel, but some buggies
        that I cannot control then I pick 267 and it works.
        """
        cls._ITEM_8.drag(offset_x=(Distance(25), Distance(50)), offset_y=(Distance(-267),))
