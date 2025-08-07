import copy
import re
from typing import Callable, List

from src import logger
from src.api import ldp
from src.const import ActionMode
from src.element import BTN_ISSUE_CONFIRM
from src.rok_profile import RokProfile
from src.ui import MenuAccounts, MenuCharacters, MenuMain, MenuProfile, MenuSettings
from src.utils import sleep_random
from src.vision import image, ocr


class Walker:
    def __init__(self, mode: ActionMode = ActionMode.DEFAULT):
        self.profile = RokProfile()
        self._tasks: List[Callable[[str], None]] = []
        self.confirm_after_done = self.profile.data["gather"]["confirm_after_done"]
        self.fallback = True
        self.mode = mode

    def execute(self):
        match self.mode:
            case ActionMode.CHARACTER:
                self.walk_character()
            case ActionMode.ACCOUNT:
                self.walk_account()
            case ActionMode.ALL_ACCOUNTS:
                self.walk_all()
            case _:
                raise RuntimeError(f"Weird action mode {self.mode}")

    def register_task(self, task: Callable[[str], None]):
        if callable(task):
            self._tasks.append(task)
        else:
            raise TypeError(f"Expected a callable, got {type(task).__name__}")

    def walk_character(self, char_id: str = ""):
        # if not set, run task with current character profile
        # if current character not in RokProfile, return
        if not char_id:
            char_id = self.profile.get_char_id_by_name(self._get_current_char_name())
            if char_id is None:
                return
        logger.info(f"walk_character {char_id}")
        char = self.profile.chars[char_id]
        if self._tasks:
            logger.info(f"Proceed tasks on character '{char.name}'")
            for task in self._tasks:
                try:
                    task(char_id)
                except Exception:
                    logger.exception(
                        f"Error occurred while processing task {task.__name__} on character '{char.name}'"
                    )
                    logger.info("Reload app and continue with next task...")
                    ldp.reload_app()
                    MenuMain.wait_for_ingame_ready()
        else:
            logger.warning(f"No tasks registered on character '{char.name}', ignore")
        # TODO: this should be one of registered tasks
        if self.confirm_after_done:
            self.confirm_done()

    def walk_account(self, acc_id: str = ""):
        """
        Walk through characters in the given account.
        If no account is passed, it will detect the current account.

        This method reorders characters so that the currently active one
        is walked first, avoiding redundant character switching.
        """
        if not acc_id:
            acc_id = self._get_current_acc_id()
        logger.info(f"walk_account {acc_id}")
        account = self.profile.accounts[acc_id]

        current_account = copy.deepcopy(account)
        char_name = self._get_current_char_name()
        starting_char_id = self.profile.get_char_id_by_name(char_name)

        # Re-order, current character should be prioritized to walk to reduce redundant moves
        if starting_char_id:
            current_account.characters.remove(starting_char_id)
            current_account.characters.insert(0, starting_char_id)
        else:
            logger.warning(f"Starting character '{char_name}' not found in Profile")

        for char_id in current_account.characters:
            if starting_char_id == char_id:
                logger.info("Walk current character")
            else:
                self.switch_character(char_id)
            self.walk_character(char_id)

    def walk_all(self):
        """
        Walk through all configured accounts, performing the registered task for each character.

        This method detects the currently active character and prioritizes their account first
        in the traversal order. This avoids unnecessary account switching, which improves macro
        efficiency and user experience.

        Behavior:
            - Detects the ID of the currently active account via character ID.
            - Reorders the account list so that the current account is processed first.
            - Skips redundant account switching.
            - Delegates character processing to `walk_account()`.

        Raises:
            RuntimeError: If no valid account or profile is found.
        """
        logger.action("WALK ALL", "start with current account & user")
        all_accounts = self.profile.all_accounts()
        uid = self._get_current_acc_id()
        # if account is configured, it should be prioritized
        if uid in self.profile.accounts:
            all_accounts.remove(uid)
            all_accounts.insert(0, uid)

        for i, acc_id in enumerate(all_accounts):
            if i == 0:
                logger.info("Walk current account")
            else:
                self.switch_account(acc_id)
            self.walk_account(acc_id)

    # --- UI hooks / placeholders ---

    def switch_account(self, acc_id: str):
        """
        Switches to the given account via the settings and account center menus.
        Assumes only two accounts are managed and switches directly to the other.
        """
        account = self.profile.accounts[acc_id]
        logger.action("Switching account", f"Account {account.name}")
        MenuProfile.open()
        MenuSettings.open()
        MenuAccounts.open()

        # At this point, we are only managing 2 accounts
        # That means when open the account center, we just proceed the switching
        # TODO: Implement to choose account from Menu "Switch Accounts"
        MenuAccounts.BTN_SWITCH_ACCOUNT.click(2000, verify=MenuAccounts.is_switch_menu_open)
        MenuAccounts.BTN_LOGIN.click(verify=MenuAccounts.is_switch_menu_close)

        MenuMain.wait_for_ingame_ready()

    def switch_character(self, char_id: str):
        """
        Switches to a character by slot number using the Account/Characters menu.

        Args:
            slot_number (int): The character slot number (1-8).
        """
        character = self.profile.get_char(char_id)
        logger.action(
            "Switching character", f"Character {character.name} - slot {character.slot_number}"
        )

        MenuProfile.open()
        MenuSettings.open()
        MenuCharacters.open()

        btn = MenuCharacters.get_character_button(character.slot_number)
        btn.click(verify=MenuCharacters.is_login_menu_open)
        sleep_random(500, 800)

        # Check for network error confirmation
        # TODO: Should be handled more properly - a Error Checking Class ???
        if ocr.extract_text_from_rect(BTN_ISSUE_CONFIRM) == "CONFIRM":
            image.screenshot("network_issue")
            BTN_ISSUE_CONFIRM.click()
        image.screenshot(f"Confirm_switch_{char_id}")
        MenuCharacters.BTN_SWITCH_YES.click(verify=MenuCharacters.is_login_menu_close)

        logger.info(f"Switching to character slot {character.slot_number}")
        MenuMain.wait_for_ingame_ready()

    def confirm_done(self):
        """UI logic to confirm farming completion"""
        # confirm_done()

    def _get_current_char_name(self) -> str:
        """Open profile menu to capture character name, retrieve char_id from RokProfile"""
        with MenuProfile() as mp:
            sleep_random(300, 500)
            char_name = ocr.extract_text_from_rect(mp.RECT_GOVERNOR_NAME, save=True)
        return char_name

    def _get_current_acc_id(self) -> str:
        """Open sub menu Accounts in Settings to capture account ID"""
        with MenuProfile():
            with MenuSettings():
                with MenuAccounts() as ma:
                    uid_text = ocr.extract_text_from_rect(ma.RECT_UID, save=True)
                    if not (match_obj := re.match(r"UID (\d+)", uid_text)):
                        image.screenshot("uid_not_found")
                        raise RuntimeError("Failed to get account UID")
                    uid = match_obj.group(1)
        return uid
