from src.lib import logger, utils
from src.lib.element import BTN_ISSUE_CONFIRM
from src.lib.rok_data import Account, Character, CharactersDB
from src.lib.ui import MenuAccounts, MenuCharacters, MenuMain, MenuProfile, MenuSettings
from src.lib.vision import image, ocr

from .reload import reload_game


class Switch:
    def __init__(self):
        self.char_db = CharactersDB()

    @utils.retry_on_exception(action_if_fail=reload_game)
    def switch_account(self, account: Account):
        """
        Switches to the given account via the settings and account center menus.
        Assumes only two accounts are managed and switches directly to the other.
        """
        logger.action("Switching account", f"Account {account.name}")
        MenuProfile.open()
        MenuSettings.open()
        MenuAccounts.open()

        # At this point, we are only managing 2 accounts
        # That means when open the account center, we just proceed the switching
        # TODO: Implement to choose account from Menu "Switch Accounts"
        MenuAccounts.BTN_SWITCH_ACCOUNT.click(delay=2, verify=MenuAccounts.is_switch_menu_open)
        MenuAccounts.BTN_LOGIN.click(verify=MenuAccounts.is_switch_menu_close)

        MenuMain.wait_for_ingame_ready()

    @utils.retry_on_exception(action_if_fail=reload_game)
    def switch_character(self, char: Character):
        """
        Switches to a character by slot number using the Account/Characters menu.

        Args:
            slot_number (int): The character slot number (1-8).
        """
        character = self.char_db.get_by_id(char._id)
        MenuProfile.open()
        char_name = MenuProfile.get_char_name()
        if self.char_db.get_by_name(char_name)._id == char._id:
            MenuProfile.close()
            return

        logger.action(
            "Switching character", f"Character {character.name} - slot {character.slot_number}"
        )
        MenuSettings.open()
        MenuCharacters.open()

        btn = MenuCharacters.get_character_button(character.slot_number)
        btn.click(verify=MenuCharacters.is_login_menu_open)
        utils.sleep_random(0.5, 0.8)

        # Check for network error confirmation
        # TODO: Should be handled more properly - a Error Checking Class ???
        if ocr.extract_text_from_rect(BTN_ISSUE_CONFIRM) == "CONFIRM":
            image.screenshot("network_issue")
            BTN_ISSUE_CONFIRM.click()
        image.screenshot(f"Confirm_switch_{char._id}")
        MenuCharacters.BTN_SWITCH_YES.click(verify=MenuCharacters.is_login_menu_close)

        logger.info(f"Switching to character slot {character.slot_number}")
        MenuMain.wait_for_ingame_ready()
