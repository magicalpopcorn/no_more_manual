from src.element import P, TextButton
from src.vision import ocr


class MenuQueue:
    """
    Represents the MenuQueue interface.
    MenuQueue opens after initiating a gathering or attack action.
    """

    BTN_NEW_TROOP = TextButton("New_Troop", P(1383, 178), P(1651, 257))  # d

    @classmethod
    def is_new_troop_btn_visible(cls):
        """
        Check if the 'New Troop' button is visible on the screen.
        """
        return "New Troop" in ocr.extract_text_from_rect(cls.BTN_NEW_TROOP)
