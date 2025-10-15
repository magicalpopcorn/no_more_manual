import copy
from typing import Callable, List, Optional, Tuple

from src.lib import logger, utils
from src.lib.action.reload import reload_game
from src.lib.action.switching import Switch
from src.lib.const import ActionMode
from src.lib.rok_data import Account, AccountsDB, Character, CharactersDB
from src.lib.ui import MenuProfile
from src.lib.utils import sleep_random


class Walker:
    def __init__(self):
        self.char_db = CharactersDB()
        self.account_db = AccountsDB()
        self._tasks: List[Callable[[Character], None]] = []
        self.switcher = Switch()

    def execute(self, mode: ActionMode = ActionMode.DEFAULT):
        match mode:
            case ActionMode.CHARACTER:
                self.walk_character()
            case ActionMode.ACCOUNT:
                self.walk_account()
            case ActionMode.ALL_ACCOUNTS:
                self.walk_all()
            case _:
                raise RuntimeError(f"Weird action mode {mode}")

    def register_task(self, task: Callable[[Character], None]):
        if callable(task):
            self._tasks.append(task)
        else:
            raise TypeError(f"Expected a callable, got {type(task).__name__}")

    def walk_character(self, char: Optional[Character] = None):
        # if not set, run task with current character profile
        # if current character not in CharactersDB, return
        if char is None:
            char = self._get_current_character()

        logger.info(f"walk_character {char._id}")
        if self._tasks:
            logger.info(f"Proceed tasks on character '{char.name}'")
            for task in self._tasks:
                try:
                    utils.retry_on_exception(max_attempts=2, action_if_fail=reload_game)(task)(char)
                except (RuntimeError, TimeoutError) as e:
                    logger.error(
                        f"Error occurred while processing task {task.__name__} on character '{char.name}':\n{e}",
                        exc_info=True,
                    )
                    logger.info("Reload app and continue with next task...")
                    reload_game()
        else:
            logger.warning(f"No tasks registered on character '{char.name}', ignore")

    def walk_account(
        self, account: Optional[Account] = None, starting_char: Optional[Character] = None
    ):
        """
        Walk through characters in the given account.
        If no account is passed, it will detect the current account.

        This method reorders characters so that the currently active one
        is walked first, avoiding redundant character switching.
        """
        if account is None:
            account, starting_char = self._get_current_account()
        logger.info(f"walk_account {account._id}")

        current_account = copy.deepcopy(account)
        if not starting_char:
            starting_char = self._get_current_character()

        # Re-order, current character should be prioritized to walk to reduce redundant moves
        if starting_char is not None and starting_char._id in current_account.characters:
            current_account.characters.remove(starting_char._id)
            current_account.characters.insert(0, starting_char._id)
        else:
            logger.warning(
                f"Starting character '{starting_char.name}' neither found or in any accounts"
            )

        for char_id in current_account.characters:
            if char_id == "main":  # skip this shit
                continue
            char = self.char_db.get_by_id(char_id)
            if starting_char._id == char_id:
                logger.info("Walk current character")
            else:
                self.switcher.switch_character(char)
            self.walk_character(char)

    def walk_all(self):
        """
        Walk through all configured accounts, performing the registered task for each character.

        This method detects the currently active character and prioritizes their account first
        in the traversal order. This avoids unnecessary account switching, which improves macro
        efficiency and user experience.

        Behavior:
            - Detects the name of the currently active account via Gorvernor name.
            - Reorders the account list so that the current account is processed first.
            - Skips redundant account switching.
            - Delegates character processing to `walk_account()`.

        Raises:
            RuntimeError: If no valid account or profile is found.
        """
        logger.action("WALK ALL", "start with current account & user")
        all_accounts = self.account_db.get_all()
        stating_account, starting_char = self._get_current_account()
        # if account is configured, it should be prioritized
        if stating_account in all_accounts:
            all_accounts.remove(stating_account)
            all_accounts.insert(0, stating_account)

        for i, account in enumerate(all_accounts):
            if i == 0:
                logger.info("Walk current account")
            else:
                self.switcher.switch_account(account)
                starting_char = None
            self.walk_account(account, starting_char)

    def _get_current_character(self) -> Character:
        """Open profile menu to capture character name, retrieve character from db"""
        with MenuProfile() as mp:
            sleep_random(0.3, 0.5)
            char_name = mp.get_char_name()
        return self.char_db.get_by_name(char_name)

    def _get_current_account(self) -> Tuple[Account, Character]:
        """get Account & Character based on current character"""
        character = self._get_current_character()
        for account in self.account_db.get_all():
            if character._id in account.characters:
                return account, character
        raise RuntimeError("Failed to get current account ID, no character found in any accounts")
