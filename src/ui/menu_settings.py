from functools import cache
from math import floor

from src import logger
from src.element import Button, Gap, P, RectZone
from src.vision import ocr

from .base_menu import _Menu
from .menu_profile import MenuProfile


class MenuSettings(_Menu):
    RECT_TITLE = RectZone("SETTINGS", P(847, 41), P(1076, 91))

    BTN_CHARACTERS_MENU = Button("Characters", P(753, 509), P(868, 605))  # d
    BTN_ACCOUNT_MENU = Button("Account", P(1050, 510), P(1165, 605))  # d

    @classmethod
    def open(cls):
        super().open()
        if cls.is_open():
            logger.warning("Menu Settings already opened")
            return
        MenuProfile.BTN_SETTINGS.click(2000, verify=cls.is_open)


class MenuCharacters(_Menu):
    RECT_TITLE = RectZone("CHARACTERS", P(810, 100), P(1110, 153))

    _BTN_CHARACTER_BASE = Button("Slot 1", P(313, 335), P(784, 463))
    _X_GAP = Gap(705)
    _Y_GAP = Gap(200)

    # Click to User profile -> Sub menu "CHARACTER LOGIN" pop to confirm
    RECT_LOGIN = RectZone("CHARACTER LOGIN", P(745, 180), P(1175, 230))

    BTN_SWITCH_NO = Button("Switch_No", P(573, 732), P(858, 797))
    BTN_SWITCH_YES = Button("Switch_Yes", P(1081, 732), P(1367, 797))

    @classmethod
    def open(cls):
        super().open()
        if cls.is_open():
            logger.warning("Menu Characters already opened")
            return
        MenuSettings.BTN_CHARACTERS_MENU.click(2500, verify=cls.is_open)

    @classmethod
    def is_login_menu_open(cls):
        return ocr.extract_text_from_rect(cls.RECT_LOGIN) == cls.RECT_LOGIN.name

    @classmethod
    def is_login_menu_close(cls):
        return not cls.is_login_menu_open()

    @classmethod
    @cache
    def get_character_button(cls, slot_number: int) -> Button:
        """Support up to 6th slot, unless implement to scroll down"""
        if slot_number < 1 or slot_number > 6:
            raise ValueError(f"Invalid character slot: {slot_number}")

        row = floor((slot_number - 1) / 2)
        col = (slot_number - 1) % 2

        x_offset = col * cls._X_GAP
        y_offset = row * cls._Y_GAP

        p1 = P(cls._BTN_CHARACTER_BASE.p1.x + x_offset, cls._BTN_CHARACTER_BASE.p1.y + y_offset)
        p2 = P(cls._BTN_CHARACTER_BASE.p2.x + x_offset, cls._BTN_CHARACTER_BASE.p2.y + y_offset)

        return Button(f"Slot_{slot_number}", p1, p2)


class MenuAccounts(_Menu):
    """
    Menu for managing accounts and characters.

    This menu appears after opening the Settings menu and clicking the "Account/Characters" button.
    It supports switching between accounts and selecting up to 8 characters arranged in a 2-row grid.
    Character buttons are computed dynamically based on slot number.

    Notes:
        - UID zone is not a button, and its location may vary.
        - Character slots are currently supported to 8 (2 columns x 4 rows).
        - CloseAccountCenter() is used to exit the sub-menu that opens in a separate window.
    """

    RECT_TITLE = RectZone("User Center", P(13, 12), P(159, 51))

    RECT_UID = RectZone("UID", P(78, 92), P(234, 127))  # d
    BTN_SWITCH_ACCOUNT = Button("Switch_Accounts", P(775, 92), P(922, 129))  # d
    # BTN_SWITCH_ACCOUNT ->  Sub Menu "Chọn tài khoản" pop
    RECT_SWITCH_ACCOUNT_TITLE = RectZone("Switch Accounts", P(860, 386), P(1060, 425))
    BTN_LOGIN = Button("Login", P(765, 560), P(1060, 615))  # d

    @classmethod
    def open(cls):
        if cls.is_open():
            logger.warning("Menu Accounts already opened")
            return
        MenuSettings.BTN_ACCOUNT_MENU.click(delay=1200, verify=cls.is_open)

    @classmethod
    def is_switch_menu_open(cls):
        return (
            ocr.extract_text_from_rect(cls.RECT_SWITCH_ACCOUNT_TITLE)
            == cls.RECT_SWITCH_ACCOUNT_TITLE.name
        )

    @classmethod
    def is_switch_menu_close(cls):
        return not cls.is_switch_menu_open()
