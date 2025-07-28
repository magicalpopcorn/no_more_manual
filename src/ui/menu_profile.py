from src import logger
from src.element import Button, P
from src.element.shortcut import SC_CLOSE, SC_USER_PROFILE

from .base_menu import _Menu


class MenuProfile(_Menu):
    RECT_GOVERNOR_NAME = Button("Governer_name", P(41, 413), P(325, 446))
    BTN_SETTINGS = Button("Settings", P(441, 907), P(486, 947))

    @classmethod
    def open(cls):
        super().open()
        SC_USER_PROFILE.press()
