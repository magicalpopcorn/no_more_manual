from src import logger
from src.element import Button, Distance, P, RectZone
from src.vision import cv, image

from .base_menu import _Menu
from .menu_main import MenuMain


class MenuCity(_Menu):
    BTN_FOOD_DEPOSITE = Button("FOOD_DEPOSITE", P(1215, 775), P(1300, 820))
    BTN_WOOD_DEPOSITE = Button("WOOD_DEPOSITE", P(1315, 696), P(1400, 745))
    BTN_STONE_DEPOSITE = Button("STONE_DEPOSITE", P(1415, 640), P(1500, 690))
    BTN_GOLD_DEPOSITE = Button("GOLD_DEPOSITE", P(1515, 555), P(1600, 600))

    BTN_COURIER_STATION = Button("Courier_Station", P(1060, 276), P(1260, 402))
    BTN_COURIER_MERCHANT = Button("Courier_Merchant", P(1296, 482), P(1429, 570))

    @classmethod
    def open(cls):
        super().open()
        if cls.is_open():
            logger.debug("In City Screen")
            return

        logger.info("Open City screen")
        MenuMain.BTN_HOME.click(verify=cls.is_open)

    @classmethod
    def close(cls):
        MenuMain.open_map_screen()

    @classmethod
    def is_open(cls):
        return cv.match_region_with_template(
            MenuMain.BTN_HOME, image.RokImages.MAP_ICON, verbose=False
        )

    @classmethod
    def get_deposite_buttons(cls):
        return (
            cls.BTN_FOOD_DEPOSITE,
            cls.BTN_WOOD_DEPOSITE,
            cls.BTN_STONE_DEPOSITE,
            cls.BTN_GOLD_DEPOSITE,
        )


class MenuMerchant(_Menu):
    MENU_WINDOW = RectZone("Mechant Menu", P(555, 220), P(1470, 860))
    RECT_TITLE = RectZone("BOUTIQUE", P(1136, 100), P(1376, 154))

    BTN_REFRESH = Button("Refresh", P(1380, 207), P(1650, 285))

    RECT_ITEM_TYPE = RectZone("Item_type", P(975, 307), P(1188, 360))
    # captured in row 1 Resources
    ITEM_PRICE_1 = Button("Item_price_1", P(600, 590), P(760, 643))
    ITEM_PRICE_2 = Button("Item_price_2", P(875, 590), P(1045, 643))
    ITEM_PRICE_3 = Button("Item_price_3", P(1150, 590), P(1320, 643))
    ITEM_PRICE_4 = Button("Item_price_4", P(1425, 590), P(1595, 643))

    RECT_DRAG_ZONE = Button("Drag_zone", P(1350, 765), P(1400, 950))

    ITEM_PRICES = (ITEM_PRICE_1, ITEM_PRICE_2, ITEM_PRICE_3, ITEM_PRICE_4)

    @classmethod
    def open(cls):
        if not MenuCity.is_open():
            raise RuntimeError("Not in city")

        if not cls.is_courier_located_right():
            image.get_image_from_rect(MenuCity.BTN_COURIER_STATION, save=True)
            raise RuntimeError("Courier station is not setup at right location")
        super().open()
        MenuCity.BTN_COURIER_STATION.click(verify=cls.is_station_menu_dropdown)
        MenuCity.BTN_COURIER_MERCHANT.click(verify=lambda: not cls.is_station_menu_dropdown())

    @classmethod
    def scrollup(cls, extra=0):
        """I set up some magic number here
        offset_x=(25, 50) -> drag to right direction
        offset_y=(-315,) -> drag to upper 315 pixel
        80 88
        """
        cls.RECT_DRAG_ZONE.drag(
            offset_x=(Distance(25), Distance(50)), offset_y=(Distance(-350) + extra,), duration=1500
        )

    @classmethod
    def is_open_for_sell(cls):
        return cls.is_open()

    @classmethod
    def is_courier_located_right(cls):
        """threshold is lower since it's affected by ingame day/night"""
        return cv.match_region_with_template(
            MenuCity.BTN_COURIER_STATION,
            image.RokImages.BTN_COURIER_STATION,
            threshold=0.8,
            verbose=True,
        )

    @classmethod
    def is_station_menu_dropdown(cls):
        return cv.match_region_with_template(
            MenuCity.BTN_COURIER_MERCHANT, image.RokImages.BTN_COURIER_MERCHANT
        )

    @classmethod
    def is_free_refresh_available(cls):
        return cv.match_region_with_template(MenuMerchant.BTN_REFRESH, image.RokImages.BTN_REFRESH)
