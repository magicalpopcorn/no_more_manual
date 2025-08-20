from src import logger, utils
from src.api import adb
from src.element import Button, Gap, P, RectZone
from src.vision import cv, image

from .menu_queue import MenuQueue


class MenuDispatch:
    """
    Factory class to generate button locations in the Dispatch Menu.

    Precondition: MenuQueue must be open.
    Usage:
        - Call MenuDispatch.get_march_button(march_number) to get the button for a specific troop slot.
        - Click BTN_MARCH to finalize dispatch.
    """

    RECT_DISPATCH_TITLE = RectZone("Dispatch_Title", P(821, 37), P(1093, 94))

    MARCH_NUMBER_GAP = Gap(82)
    _BTN_BASE_MARCH_NUMBER = Button("March", P(1636, 371), P(1676, 409))
    SHIFT = -168
    BTN_MULTI_SELECT = Button("Multi_Select", P(1638, 936), P(1683, 979))
    BTN_MULTI_CHECKED = Button("Multi_Checked", P(1638 + SHIFT, 936), P(1683 + SHIFT, 979))

    BTN_MARCH = Button("March", P(1222, 905), P(1566, 994))

    selected_loadout = 1  # Assume loadout 1 is always available

    @classmethod
    def is_open(cls):
        return cv.match_region_with_template(
            cls.RECT_DISPATCH_TITLE, image.RokImages.RECT_DISPATCH_TITLE
        )

    @classmethod
    def close(cls):
        logger.debug("Close MenuDispatch")
        adb.send_escape()

    @classmethod
    def is_close(cls):
        return not cls.is_open()

    @classmethod
    def is_multi_select_checked(cls):
        return cv.match_region_with_template(
            cls.BTN_MULTI_CHECKED, image.RokImages.BTN_MULTI_CHECKED
        )

    @classmethod
    def click_multi_select(cls):
        if not cls.is_multi_select_checked():
            cls.BTN_MULTI_SELECT.click(verify=cls.is_multi_select_checked)

    @classmethod
    def get_march_button(cls, march_number: int) -> Button:
        if march_number < 1 or march_number > 7:
            raise ValueError(f"Invalid march number: {march_number}")
        offset_x = cls.SHIFT if cls.is_multi_select_checked() else 0
        offset_y = (march_number - 1) * cls.MARCH_NUMBER_GAP

        return cls._BTN_BASE_MARCH_NUMBER.shift(offset_x, offset_y)

    @staticmethod
    def dispatch_march(march_number: int):
        """
        Dispatch troops using the specified march number (1-7).
        Preconditions:
            - MenuQueue must be open
        Steps:
            1. Click 'New Troop' button from MenuQueue
            2. Click march slot button (e.g., March_1)
            3. Click final 'March' button to confirm
        """

        MenuQueue.BTN_NEW_TROOP.click(verify=MenuDispatch.is_open)
        MenuDispatch.get_march_button(march_number).click()
        MenuDispatch.BTN_MARCH.click(verify=MenuDispatch.is_close)

    @classmethod
    def dispatch_all(cls):
        cls.click_multi_select()
        shifted_btn_march = cls.BTN_MARCH.shift(offset_x=cls.SHIFT)
        shifted_btn_march.click(verify=cls.is_close)
        utils.sleep_random(1.5, 2.5)
