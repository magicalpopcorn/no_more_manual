import re
import time

from src import logger
from src.api import adb
from src.element import BTN_GATHER, P, RectZone
from src.rok_profile import RokProfile
from src.ui import MenuDispatch, MenuMain, MenuSearch
from src.vision import ocr


class Gather:
    MARCH_STATUS = RectZone("March_status", P(1815, 205), P(1860, 230))  # d

    def __init__(self):
        self.profile = RokProfile()

    def gather(self, char_id: str):
        char = self.profile.chars[char_id]
        rss_level = char.rss_level
        rss_order = list(char.rss_order)

        text = ocr.extract_text_from_rect(Gather.MARCH_STATUS)
        if text:
            if obj := re.match(r"(\d)/(\d)", text):
                used_m, all_m = map(int, obj.groups())
                for _ in range(used_m):
                    rss_order.pop()

        logger.action(
            "Gather Resources",
            f"Name: {char.name}, Level: {rss_level}, Order: {rss_order}"
            f", Marches available: {len(rss_order)}",
        )

        MenuMain.navigate_to_map_screen()
        MenuSearch.reset()

        if not rss_order:
            logger.info("There is no marches available, skip farming")
            return
        for march_number, rss_type in enumerate(rss_order, start=1):
            try:
                self.search_rss(rss_type, rss_level)
            except RuntimeWarning as warning:
                logger.warning(
                    f"NO DEPOSITE LEFT !!! REALLY ???. Skip this gathering for char {char_id}"
                )
                break
            else:
                BTN_GATHER.click(1000)
                MenuDispatch.dispatch(march_number)

    @staticmethod
    def search_rss(rss_type, rss_level):
        """Searching for rss type. If rss level not found, try to decrease the level till 5.
        If still not found, try to search for next rss type with same mechanic
        If still not found, I have no words to say LOL
        """
        logger.info(f"Trying to search for {rss_type} - level {rss_level}")
        node_level = rss_level
        MenuSearch.open()
        Gather.find_and_click_deposit_button(rss_type)

        is_valid_node_level = lambda n: 6 <= n <= 8
        while is_valid_node_level(node_level):
            Gather.find_and_click_level_button(rss_type, node_level)
            MenuSearch.get_search_button(rss_type).click(1200)

            # Apply for all resource types
            if Gather.is_gather_popup_shown():
                # If searching with exhausted nodes and pointer stay at previous node
                # we don't count on it
                cur_loc = ocr.extract_text_from_rect(MenuSearch.ZONE_DEPOSITE_LOC)
                if MenuSearch.is_different_loc(cur_loc):
                    logger.debug(f"Found node level {node_level}")
                    MenuSearch.update_last_deposite_loc(cur_loc)
                    # once found, MenuSearch close
                    MenuSearch.update_state(False)
                    break
                else:
                    logger.debug("The same node found, still search for next one")
                    adb.screenshot()
                    # If found the same node, MenuSearch closed
                    # Re-open to search for next one
                    MenuSearch.update_state(False)
                    MenuSearch.open()
            else:
                adb.screenshot()

            cur_level = node_level
            node_level -= 1
            if is_valid_node_level(node_level):
                logger.info(f"Node level {cur_level} not found. Retry with level {node_level}")
                time.sleep(0.3)

        if not is_valid_node_level(node_level):
            # Fallback to farm next rss
            rss_index = MenuSearch.RSS_TYPES.index(rss_type)
            if rss_index == 0:
                raise RuntimeWarning("No node found for any rss types. Skip this march")

            next_rss_index = rss_index - 1
            next_rss_type = MenuSearch.RSS_TYPES[next_rss_index]
            logger.info(f"FALLBACK !!! SEARCH FOR NEXT RSS")
            Gather.search_rss(next_rss_type, rss_level)

    @staticmethod
    def find_and_click_deposit_button(rss_type):
        if MenuSearch.selected_rss_type == rss_type:
            logger.debug(f"Resource type {rss_type} is already selected")
            return

        deposite = MenuSearch.get_deposite_button(rss_type)
        deposite.click()
        MenuSearch.update_selected_rss_type(rss_type)

    @staticmethod
    def find_and_click_level_button(rss_type: str, rss_level: int):
        if rss_level == MenuSearch.selected_rss_level:
            logger.debug(f"Level {rss_level} is already selected")
            return

        level_btn = MenuSearch.get_level_button(rss_type, rss_level)
        level_btn.click()
        MenuSearch.update_selected_rss_level(rss_level)

    @staticmethod
    def is_gather_popup_shown():
        text = ocr.extract_text_from_rect(BTN_GATHER)
        return text.upper() == BTN_GATHER.name.upper()
