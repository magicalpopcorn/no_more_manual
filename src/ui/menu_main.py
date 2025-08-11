import re

from src import logger, utils
from src.element import Button, Direction, P, RectZone, SwipeStrategyType
from src.vision import cv, image, ocr

from .swipeable_mixin import SwipeMixin


class MenuMain:
    BTN_HOME = Button("Home", P(45, 942), P(140, 1022))
    BTN_HOME_RESOURCES = Button("Resources", P(352, 809), P(416, 870))
    BTN_HOME_BUILDINGS = Button("Buildings", P(375, 1000), P(440, 1055))

    BTN_USER_PROFILE = Button("User_Profile", P(25, 10), P(105, 95))

    # Expansion
    BTN_SUB_MENU = Button("Sub_Menu", P(1800, 970), P(1890, 1037))
    BTN_ITEMS = Button("Items", P(1203, 970), P(1284, 1037))

    RECT_SWORD = RectZone("Sword_of_Power", P(144, 16), P(180, 54))
    RECT_MARCH = RectZone("Rect_March_Status", P(1815, 207), P(1860, 232))

    # Troop focus
    BTN_TROOP_STOP = Button("Stop_Troop", P(920, 670), P(1005, 747))

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


class MenuHomeResources(SwipeMixin):
    BTN_HOME_RESOURCES_FILTER = Button("Home_Resources_Filter", P(30, 10), P(70, 50))

    # Define the swipeable area for the home resources screen
    SWIPE_AREA = RectZone("Home_Resources_Swipe_Area", P(25, 150), P(1580, 855))

    @classmethod
    def open(cls):
        if MenuHomeResources.is_open():
            logger.debug("Home Resources already opened")
            return True
        logger.info("Open Home Resources")
        MenuMain.BTN_HOME.hold(1500, verify=MenuMain.is_home_dropdown_visible)
        MenuMain.BTN_HOME_RESOURCES.click(verify=cls.is_open)

    @classmethod
    def is_open(cls):
        return cv.match_region_with_template(
            cls.BTN_HOME_RESOURCES_FILTER,
            image.RokImages.BTN_HOME_RESOURCES_FILTER,
            verbose=True,
            save=False,
        )

    @classmethod
    def setup_swipe_strategy(cls):
        """Setup the swipe strategy for home resources screen"""
        cls.set_swipe_strategy(SwipeStrategyType.EDGE, margin_ratio=0.15)
