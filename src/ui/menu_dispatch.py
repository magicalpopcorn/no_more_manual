# menu_dispatch.py
from src.element import Button, Gap, P

from .menu_queue import MenuQueue


class MenuDispatch:
    """
    Factory class to generate button locations in the Dispatch Menu.

    Precondition: MenuQueue must be open.
    Usage:
        - Call MenuDispatch.get_march_button(march_number) to get the button for a specific troop slot.
        - Click BTN_MARCH to finalize dispatch.
    """

    MARCH_NUMBER_GAP = Gap(82)  # d
    _BTN_BASE_MARCH_NUMBER = Button("March", P(1636, 371), P(1676, 409))  # d
    BTN_MARCH = Button("March", P(1222, 905), P(1566, 994))  # d
    selected_loadout = 1  # Assume loadout 1 is always available

    @classmethod
    def get_march_button(cls, march_number: int) -> Button:
        if march_number < 1 or march_number > 7:
            raise ValueError(f"Invalid march number: {march_number}")

        y_offset = (march_number - 1) * cls.MARCH_NUMBER_GAP
        p1 = P(cls._BTN_BASE_MARCH_NUMBER.p1.x, cls._BTN_BASE_MARCH_NUMBER.p1.y + y_offset)
        p2 = P(cls._BTN_BASE_MARCH_NUMBER.p2.x, cls._BTN_BASE_MARCH_NUMBER.p2.y + y_offset)

        return Button(f"March_{march_number}", p1, p2)

    @staticmethod
    def dispatch(march_number: int):
        """
        Dispatch troops using the specified march number (1-7).
        Preconditions:
            - MenuQueue must be open
        Steps:
            1. Click 'New Troop' button from MenuQueue
            2. Click march slot button (e.g., March_1)
            3. Click final 'March' button to confirm
        """

        MenuQueue.BTN_NEW_TROOP.click()
        MenuDispatch.get_march_button(march_number).click()
        MenuDispatch.BTN_MARCH.click()
