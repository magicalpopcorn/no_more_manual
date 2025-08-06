from src import logger, utils
from src.element import Button, P, RectZone
from src.vision import cv, image, ocr


class MenuMain:
    BTN_HOME = Button("Home", P(45, 942), P(140, 1022))  # d
    BTN_HOME_BUILDINGS = Button("Buildings", P(375, 1000), P(440, 1055))  # d
    BTN_USER_PROFILE = Button("User_Profile", P(25, 10), P(105, 95))  # d

    # Expansion
    BTN_SUB_MENU = Button("Sub_Menu", P(1800, 970), P(1890, 1037))
    BTN_ITEMS = Button("Items", P(1203, 970), P(1284, 1037))  # d

    RECT_SWORD = RectZone("Sword_of_Power", P(144, 16), P(180, 54))
    RECT_MARCH = RectZone("Rect_March_Status", P(1815, 207), P(1860, 232))  # d

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
    def get_avail_march_on_screen(cls):
        return ocr.extract_text_from_rect(cls.RECT_MARCH)

    @classmethod
    def is_in_map_screen(cls):
        return cv.match_region_with_template(
            cls.BTN_HOME, image.RokImages.CASTLE_ICON, verbose=False
        )

    @classmethod
    def is_sub_menu_expanded(cls):
        return cv.match_region_with_template(cls.BTN_ITEMS, image.RokImages.BTN_ITEMS)
