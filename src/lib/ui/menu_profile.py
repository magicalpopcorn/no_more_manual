from src.lib import logger
from src.lib.element import Button, P, RectZone
from src.lib.ui import MenuMain
from src.lib.vision import cv, image, ocr

from .base_menu import _Menu


class MenuProfile(_Menu):
    RECT_TITLE = RectZone("GOVERNOR PROFILE", P(730, 86), P(1185, 135))

    RECT_GOVERNOR_NAME = Button("Governer_name", P(712, 258), P(1107, 295))  # d
    BTN_SETTINGS = Button("Settings", P(1622, 840), P(1700, 905))  # d

    @classmethod
    def open(cls):
        super().open()
        if cls.is_open():
            logger.warning("Menu Profile already opened")
            return
        MenuMain.BTN_USER_PROFILE.click(verify=cls.is_open)

    @classmethod
    def get_char_name(cls):
        return ocr.extract_text_from_rect(cls.RECT_GOVERNOR_NAME, save=True)
