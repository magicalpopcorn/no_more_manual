from src import logger
from src.element import P, RectZone, TextButton

from ..base_menu import _Menu
from ..menu_main import MenuMain


class MenuAlliance(_Menu):
    RECT_TITLE = RectZone("ALLIANCE", P(445, 45), P(1080, 90))

    # buttons in the alliance menu
    BTN_TERRITORY = TextButton("TERRITORY", P(1180, 570), P(1280, 665))
    BTN_GIFTS = TextButton("GIFTS", P(1545, 570), P(1640, 665))
    BTN_TECHNOLOGY = TextButton("TECHNOLOGY", P(1010, 790), P(1100, 830))

    @classmethod
    def open(cls):
        super().open()
        if cls.is_open():
            logger.debug("Menu Alliance already opened")
            return
        MenuMain.open_sub_menu()
        super().open()
        MenuMain.BTN_ALLIANCE.click(verify=cls.is_open)

    class MenuAllianceTerritory(_Menu):
        RECT_TITLE = RectZone("ALLIANCE TERRITORY", P(720, 45), P(1210, 90))

        BTN_CLAIM = TextButton("CLAIM", P(1440, 180), P(1600, 230))

        @classmethod
        def open(cls):
            if cls.is_open():
                logger.debug("Menu Alliance Territory already opened")
                return
            MenuAlliance.open()
            super().open()
            MenuAlliance.BTN_TERRITORY.click(verify=cls.is_open)
