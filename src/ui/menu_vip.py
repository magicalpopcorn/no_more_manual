from src.element import Button, P

from .base_menu import _Menu


class MenuVip(_Menu):
    BTN_EXCLUSIVE_CHEST = Button("Chest_Exclusive", P(1070, 517), P(1150, 560))
    BTN_DAILY_VIP = Button("Chest_Daily_VIP", P(1323, 330), P(1377, 352))

    @classmethod
    def open(cls):
        super().open()
        SC_VIP.press()
