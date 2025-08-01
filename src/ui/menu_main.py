from src import logger, utils
from src.element import Button, P, RectZone
from src.vision import cv, image, ocr


class MenuMain:
    BTN_HOME = Button("Home", P(45, 942), P(140, 1022))  # d
    BTN_HOME_BUILDINGS = Button("Buildings", P(375, 1000), P(440, 1055))  # d
    BTN_USER_PROFILE = Button("User_Profile", P(25, 10), P(105, 95))  # d
    BTN_ITEM = Button("Items", P(1203, 969), P(1284, 1034))  # d

    RECT_VIP = RectZone("VIP", P(200, 82), P(250, 110))
    RECT_SWORD = RectZone("Sword_of_Power", P(144, 16), P(180, 54))

    RECT_MARCH = RectZone("Rect_March_Status", P(1815, 207), P(1860, 232))  # d

    @classmethod
    @utils.retry(max_attempts=3, delay=1.0, info="Open Map screen", action_if_fail=BTN_HOME.click)
    def open_map_screen(cls):
        cls.BTN_HOME.hold(1500)
        cls.BTN_HOME_BUILDINGS.click()
        if cv.match_region_with_template(
            cls.BTN_HOME, image.RokImages.CASTLE_ICON.as_array(), verbose=True
        ):
            logger.debug("In Map Screen")
            return True
        return False

    @classmethod
    @utils.timed_polling(timeout=60, interval=5, info="Wait for loading ingame")
    def wait_for_ingame_ready(cls):
        """
        After login or switching account & characters, wait for game to load.
        We check the RECT_VIP to get text from it; if it's "VIP" then it's ready.
        """
        if cv.match_region_with_template(
            cls.RECT_SWORD, image.RokImages.SWORD_ICON.as_array(), verbose=True
        ):
            logger.info("Game is ready")
            return True
        return False

    @classmethod
    def get_available_march(cls):
        return ocr.extract_text_from_rect(cls.RECT_MARCH)
