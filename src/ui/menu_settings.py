from functools import cache
from math import floor

from src.element import Button, Gap, P, RectZone

from .base_menu import _Menu
from .menu_profile import MenuProfile


class MenuSettings(_Menu):
    BTN_CHARACTERS_MENU = Button("Characters", P(753, 509), P(868, 605))  # d
    BTN_ACCOUNT_MENU = Button("Account", P(1050, 510), P(1165, 605))  # d

    @classmethod
    def _open(cls):
        MenuProfile.BTN_SETTINGS.click(2000)
        return True


class MenuCharacters(_Menu):
    _BTN_CHARACTER_BASE = Button("Slot 1", P(313, 335), P(784, 463))
    _X_GAP = Gap(705)
    _Y_GAP = Gap(200)

    # Click to User profile -> Sub menu "CHARACTER LOGIN" pop to confirm
    BTN_SWITCH_NO = Button("Switch_No", P(573, 732), P(858, 797))
    BTN_SWITCH_YES = Button("Switch_Yes", P(1081, 732), P(1367, 797))

    @classmethod
    def _open(cls):
        MenuSettings.BTN_CHARACTERS_MENU.click(2500)
        return True

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

    ZONE_UID = RectZone("UID", P(78, 92), P(234, 127))  # d
    BTN_SWITCH_ACCOUNT = Button("Switch_Accounts", P(775, 92), P(922, 129))  # d
    # BTN_SWITCH_ACCOUNT ->  Sub Menu "Chọn tài khoản" pop
    BTN_LOGIN = Button("Login", P(765, 560), P(1060, 615))  # d

    @classmethod
    def _open(cls):
        MenuSettings.BTN_ACCOUNT_MENU.click(delay=1200)
        return True
