import re

from src.lib import logger, utils
from src.lib.api import adb
from src.lib.element import Button, P, RectZone, SwipeStrategyType, TextButton
from src.lib.vision import cv, image, ocr

from .base_menu import _Menu
from .swipeable_mixin import SwipeMixin


class MenuMain:
    BTN_HOME = Button("Home", P(45, 942), P(140, 1022))
    BTN_HOME_RESOURCES = Button("Resources", P(352, 809), P(416, 870))
    BTN_HOME_BUILDINGS = Button("Buildings", P(375, 1000), P(440, 1055))

    BTN_USER_PROFILE = Button("User_Profile", P(25, 10), P(105, 95))

    # Expansion
    BTN_SUB_MENU = Button("Sub_Menu", P(1800, 970), P(1890, 1037))
    BTN_ITEMS = Button("Items", P(1203, 970), P(1284, 1037))
    BTN_ALLIANCE = Button("Alliance", P(1355, 970), P(1430, 1037))

    RECT_SWORD = RectZone("Sword_of_Power", P(144, 16), P(180, 54))
    RECT_MARCH = RectZone("Rect_March_Status", P(1815, 207), P(1860, 232))

    # Troop focus
    BTN_TROOP_STOP = Button("Stop_Troop", P(920, 670), P(1005, 747))

    BTN_LOCATION = Button("Btn_Location", P(482, 13), P(646, 46))

    BTN_ASSIST = TextButton("ASSIST", P(205, 680), P(465, 750))

    RECT_CITY_LOC = RectZone("City_Location", P(1360, 280), P(1508, 315))
    CITY_INFO_ICON = RectZone("City_Info_Symbol", P(1089, 277), P(1108, 302))

    @classmethod
    def open_map_screen(cls):
        if cls.is_in_map_screen():
            logger.debug("In Map Screen")
            return

        logger.info("Open Map screen")
        cls.BTN_HOME.click(verify=cls.is_in_map_screen)

    @classmethod
    def open_sub_menu(cls):
        if cls.is_sub_menu_expanded():
            logger.debug("Sub menu already expanded")
            return

        logger.info("Open Sub Menu")
        cls.BTN_SUB_MENU.click(verify=cls.is_sub_menu_expanded)

    @classmethod
    @utils.timed_polling(timeout=60, interval=5, info="Wait for loading ingame")
    def wait_for_ingame_ready(cls):
        """
        After login or switching account & characters, wait for game to load.
        Check the sword symbol from RECT_SWORD
        """
        if cv.match_region_with_template(cls.RECT_SWORD, image.RokImages.SWORD_ICON, verbose=False):
            logger.info("Game is ready")
            return True
        return False

    @classmethod
    def get_unused_march_on_screen(cls):
        unused_m = 5  # Default to 5 marches
        obj = ocr.extract_text_from_rect(cls.RECT_MARCH)
        if match_obj := re.search(r"(\d)/(\d)", obj):
            used_m, all_m = map(int, match_obj.groups())
            unused_m = all_m - used_m
        return unused_m

    @classmethod
    def is_in_map_screen(cls):
        return cv.match_region_with_template(
            cls.BTN_HOME, image.RokImages.CASTLE_ICON, verbose=False
        )

    @classmethod
    def is_sub_menu_expanded(cls):
        return cv.match_region_with_template(cls.BTN_ITEMS, image.RokImages.BTN_ITEMS)

    @classmethod
    def is_home_dropdown_visible(cls):
        """
        Check if the home dropdown menu is visible by looking for the resources button.
        """
        return cv.match_region_with_template(
            cls.BTN_HOME_RESOURCES, image.RokImages.BTN_HOME_RESOURCES, verbose=True, save=False
        )

    @classmethod
    def is_btn_assist_visible(cls):
        # return cv.match_region_with_template(
        #     cls.BTN_ASSIST, image.RokImages.BTN_ASSIST, verbose=False
        # )
        return ocr.extract_text_from_rect(cls.BTN_ASSIST, verbose=False) == cls.BTN_ASSIST.name

    @classmethod
    def is_city_info_visible(cls):
        return cv.match_region_with_template(
            cls.CITY_INFO_ICON, image.RokImages.CITY_INFO_ICON, verbose=False
        )


class MenuHomeResources(SwipeMixin):
    BTN_HOME_RESOURCES_FILTER = Button("Home_Resources_Filter", P(30, 10), P(70, 50))

    # Define the swipeable area for the home resources screen
    SWIPE_AREA = RectZone("Home_Resources_Swipe_Area", P(100, 150), P(1500, 855))

    # Define the swipe strategy for this screen
    SWIPE_STRATEGY = SwipeStrategyType.ZONE
    _swipe_options = {"zone_width": 15, "variation_range": 10}

    @classmethod
    def open(cls):
        if MenuHomeResources.is_open():
            logger.debug("Home Resources already opened")
            return True
        logger.info("Open Home Resources")
        MenuMain.BTN_HOME.hold(duration=1.5, verify=MenuMain.is_home_dropdown_visible)
        MenuMain.BTN_HOME_RESOURCES.click(verify=cls.is_open)

    @classmethod
    def is_open(cls):
        return cv.match_region_with_template(
            cls.BTN_HOME_RESOURCES_FILTER,
            image.RokImages.BTN_HOME_RESOURCES_FILTER,
            verbose=True,
            save=False,
        )


class MenuSearchLocation:
    BTN_SEARCH_LOCATION = Button("Search_Location", P(1300, 185), P(1358, 240))
    INPUT_X = Button("Input_X", P(887, 200), P(1025, 230))
    INPUT_Y = Button("Input_Y", P(1120, 200), P(1255, 230))
    BTN_OK = TextButton("OK", P(1792, 996), P(1864, 1053))

    # Once clicked, "ASSIST" will visible
    # BTN_ASSIST = Button("Assist", P(100, 100), P(200, 200))

    @classmethod
    def open(cls):
        if cls.is_open():
            logger.debug("Location menu already opened")
            return

        logger.info("Open Location menu")
        MenuMain.BTN_LOCATION.click(verify=cls.is_open)

    @classmethod
    def is_open(cls):
        """Check if the location menu is open by looking for the location button."""
        return cv.match_region_with_template(
            cls.BTN_SEARCH_LOCATION, image.RokImages.BTN_SEARCH_LOCATION, verbose=False
        )

    @classmethod
    def is_input_open(cls):
        return ocr.extract_text_from_rect(cls.BTN_OK) == cls.BTN_OK.name

    @classmethod
    def locate(cls, x, y):
        print(f"Locating to ({x}, {y})")
        cls.open()
        cls.INPUT_X.click(verify=cls.is_input_open)
        adb.input_text(str(x))
        adb.send_enter()
        cls.INPUT_Y.click(verify=cls.is_input_open)
        adb.input_text(str(y))
        adb.send_enter()
        cls.BTN_SEARCH_LOCATION.click(verify=lambda: not cls.is_open(), delay=1.5)
