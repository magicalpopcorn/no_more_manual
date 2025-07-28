from src import logger
from src.element import Button, P
from src.ui import MenuMain

from .base_menu import _Menu


class MenuProfile(_Menu):
    RECT_GOVERNOR_NAME = Button("Governer_name", P(712, 258), P(1107, 295))  # d
    BTN_SETTINGS = Button("Settings", P(1622, 840), P(1700, 905))  # d

    @classmethod
    def open(cls):
        super().open()
        MenuMain.BTN_USER_PROFILE.click()
