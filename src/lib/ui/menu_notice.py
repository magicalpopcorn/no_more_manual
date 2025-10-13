from src.lib.element import P, RectZone, TextButton

from .base_menu import _Menu


class MenuNotice(_Menu):
    BTN_NOTICE_YES = TextButton("YES", P(550, 730), P(888, 807))
    BTN_NOTICE_NO = TextButton("NO", P(1050, 730), P(1395, 807))

    RECT_TITLE = RectZone("NOTICE", P(855, 180), P(1055, 230))


class MenuNetWorkDisconnect(_Menu):
    RECT_TITLE = RectZone("NETWORK DISCONNECTED", P(665, 272), P(1250, 320))

    BTN_CONFIRM = TextButton("CONFIRM", P(800, 675), P(1125, 745))
