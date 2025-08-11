import copy
import re
from typing import Callable, List

from src import logger, utils
from src.action import Switch
from src.action.reload import reload_game
from src.const import ActionMode
from src.rok_profile import RokProfile
from src.ui import MenuAccounts, MenuProfile, MenuSettings
from src.utils import sleep_random
from src.vision import image, ocr


class Walker:
    def __init__(self, mode: ActionMode = ActionMode.DEFAULT):
        self.profile = RokProfile()
        self._tasks: List[Callable[[str], None]] = []
        self.confirm_after_done = self.profile.data["gather"]["confirm_after_done"]
        self.fallback = True
        self.mode = mode
        self.switcher = Switch()

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
                    # task(char_id)
                    utils.retry_on_exception(max_attempts=2, action_if_fail=reload_game)(task)(
                        char_id
                    )
                except (RuntimeError, TimeoutError) as e:
                    logger.error(
                        f"Error occurred while processing task {task.__name__} on character '{char.name}':\n{e}",
                        exc_info=True,
                    )
                    logger.info("Reload app and continue with next task...")
                    reload_game()
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
        if starting_char_id and starting_char_id in current_account.characters:
            current_account.characters.remove(starting_char_id)
            current_account.characters.insert(0, starting_char_id)
        else:
            logger.warning(f"Starting character '{char_name}' neither not found or in any accounts")

        for char_id in current_account.characters:
            if starting_char_id == char_id:
                logger.info("Walk current character")
            else:
                self.switcher.switch_character(char_id)
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
                self.switcher.switch_account(acc_id)
            self.walk_account(acc_id)

    def confirm_done(self):
        """UI logic to confirm farming completion"""
        # confirm_done()

    def _get_current_char_name(self) -> str:
        """Open profile menu to capture character name, retrieve char_id from RokProfile"""
        with MenuProfile() as mp:
            sleep_random(300, 500)
            char_name = mp.get_char_name()
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
