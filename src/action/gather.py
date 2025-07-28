import re
import time

from src import logger
from src.element import BTN_GATHER, BTN_HOME, BTN_HOME_BUILDINGS, P, RectZone
from src.rok_profile import RokProfile
from src.ui import MenuDispatch, MenuMain, MenuSearch
from src.vision import ocr, screenshot


class Gather:
    def __init__(self):
        # You can inject shared UI state here if needed later
        self.profile = RokProfile()

    def run(self, char_id: str):
        char = self.profile.chars[char_id]
        rss_level = char.rss_level
        rss_order = list(char.rss_order)

        MARCH_STATUS = RectZone("March_status", P(1855, 158), P(1885, 178))
        text = ocr.extract_text_from_rect(MARCH_STATUS)
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
            node_level = rss_level
            MenuSearch.open()
            self.find_and_click_deposit_button(rss_type)

            is_valid_node_level = lambda n: 6 <= n <= 8
            while is_valid_node_level(node_level):
                self.find_and_click_level_button(rss_type, node_level)
                MenuSearch.get_search_button(rss_type).click(1200)

                # Apply for all resource types
                if self.is_gather_popup_shown():
                    # If searching with exhausted nodes and pointer stay at previous node
                    # we don't count on it
                    cur_loc = ocr.extract_text_from_rect(MenuSearch.BTN_DEPOSITE_LOC)
                    if MenuSearch.is_different_loc(cur_loc):
                        logger.debug(f"Found node level {node_level}")
                        MenuSearch.update_last_deposite_loc(cur_loc)
                        break
                    else:
                        logger.debug("The same node found, still search for next one")
                        screenshot.capture_fullscreen()
                        MenuSearch.open()
                else:
                    screenshot.capture_fullscreen()

                cur_level = node_level
                node_level -= 1
                if is_valid_node_level(node_level):
                    logger.info(f"Node level {cur_level} not found. Retry with level {node_level}")
                    time.sleep(0.3)

            if not is_valid_node_level(node_level):
                logger.error("No node found. Skip this march")
                continue

            BTN_GATHER.click(1000)
            MenuDispatch.dispatch(march_number)

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
