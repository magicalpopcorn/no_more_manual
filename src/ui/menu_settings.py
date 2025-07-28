from math import floor

from src.element import SC_CLOSE, Button, Gap, P, RectZone
from src.window import ROKWindow

from .menu_profile import MenuProfile


class MenuSettings:
    BTN_ACCOUNT_MENU = Button("Account/Characters", P(216, 702), P(376, 737))

    @classmethod
    def open(cls):
        MenuProfile.BTN_SETTINGS.click()

    @classmethod
    def close(cls):
        SC_CLOSE.press()


class MenuAccountCharacters:
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

    # Buttons in Menu Account/Characters
    BTN_ACCOUNT_CENTER = Button("Account", P(531, 282), P(826, 327))
    _BTN_CHARACTER_BASE = Button("Slot 1", P(591, 452), P(891, 502))
    _HORIZONTAL_GAP = Gap(560)
    _VERTICAL_GAP = Gap(130)

    # Click to User profile -> Sub menu "CHARACTER LOGIN" pop to confirm
    BTN_SWITCH_NO = Button("Switch_No", P(726, 682), P(871, 707))
    BTN_SWITCH_YES = Button("Switch_Yes", P(1076, 682), P(1221, 707))

    # BTN_ACCOUNT -> Sub Menu "Trung Tâm Người Dùng" pop
    # This sub menu create another window
    ZONE_UID = RectZone("UID", P(1045, 345), P(1190, 373))  # technically not a button
    BTN_SWITCH_ACCOUNT = Button("Chuyển tài khoản", P(816, 712), P(1091, 747))
    # BTN_SWITCH_ACCOUNT ->  Sub Menu "Chọn tài khoản" pop
    BTN_START_SWITCHING = Button("BẮT ĐẦU", P(816, 602), P(1091, 632))
    BTN_CLOSE_ACCOUNT_CENTER = Button("Close_Account_Center_X", P(1177, 292), P(1193, 308))

    @classmethod
    def get_character_button(cls, slot_number: int) -> Button:
        if slot_number < 1 or slot_number > 8:
            raise ValueError(f"Invalid character slot: {slot_number}")

        row = floor((slot_number - 1) / 2)
        col = (slot_number - 1) % 2

        x_offset = col * cls._HORIZONTAL_GAP
        y_offset = row * cls._VERTICAL_GAP

        p1 = P(cls._BTN_CHARACTER_BASE.p1.x + x_offset, cls._BTN_CHARACTER_BASE.p1.y + y_offset)
        p2 = P(cls._BTN_CHARACTER_BASE.p2.x + x_offset, cls._BTN_CHARACTER_BASE.p2.y + y_offset)

        return Button(f"Slot_{slot_number}", p1, p2)

    @classmethod
    def open(cls):
        MenuSettings.BTN_ACCOUNT_MENU.click(delay=1200)

    @classmethod
    def open_account_center(cls):
        cls.BTN_ACCOUNT_CENTER.click(delay=7000)

    @classmethod
    def close_account_center(cls):
        cls.BTN_CLOSE_ACCOUNT_CENTER.click(delay=1500)
        ROKWindow.focus()
