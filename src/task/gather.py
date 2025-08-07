import re
import time

from src import logger
from src.element import BTN_GATHER
from src.rok_profile import RokProfile
from src.ui import MenuDispatch, MenuMain, MenuQueue, MenuSearch
from src.vision import cv, image, ocr


class Gather:
    MAX_MARCHES = 5

    def __init__(self):
        self.profile = RokProfile()

    def gather(self, char_id: str):
        char = self.profile.chars[char_id]
        rss_level = char.rss_level
        rss_order = list(char.rss_order)

        avail_m = MenuMain.get_avail_march_on_screen()
        if avail_m == 0:
            logger.info("There is no marches available, skip farming")
            return

        MenuMain.open_map_screen()
        MenuSearch.reset()

        if avail_m != Gather.MAX_MARCHES:
            marches = Gather.get_avail_marches()
            rss_order = [rss_type if marches[i] > 0 else "" for i, rss_type in enumerate(rss_order)]

        logger.action(
            "Gather Resources",
            f"Name: {char.name}, Level: {rss_level}, Order: {rss_order}"
            f", Marches available: {avail_m}",
        )

        for march_number, rss_type in enumerate(rss_order, start=1):
            if not rss_type:
                continue
            try:
                self.search_rss(rss_type, rss_level)
            except RuntimeWarning as warning:
                logger.warning(
                    f"NO DEPOSITE LEFT !!! REALLY ???. Skip this gathering for char {char_id}\n{warning}"
                )
                break
            else:
                BTN_GATHER.click(
                    1000,
                    verify=lambda: ocr.extract_text_from_rect(MenuQueue.BTN_NEW_TROOP)
                    == "New Troop",
                )
                MenuDispatch.dispatch_march(march_number)

    @staticmethod
    def get_avail_marches():
        logger.info("Try to get which marches are available")
        Gather.search_rss("wood", 7)  # No need to choose rss level
        BTN_GATHER.click(1000, verify=MenuQueue.is_new_troop_btn_visible)
        MenuQueue.BTN_NEW_TROOP.click(verify=MenuDispatch.is_open)
        MenuDispatch.click_multi_select()
        marches = []
        for i in range(1, Gather.MAX_MARCHES + 1):
            btn = MenuDispatch.get_march_button(i)
            if cv.match_region_with_template(btn, image.RokImages.get_march_image(i)):
                logger.debug(f"March {i} is available")
                marches.append(i)
            else:
                marches.append(0)
        MenuDispatch.close()
        return marches

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
                cur_loc = ocr.extract_text_from_rect(MenuSearch.RECT_DEPOSITE_LOC)
                if MenuSearch.is_different_loc(cur_loc):
                    logger.debug(f"Found node level {node_level}")
                    MenuSearch.update_last_deposite_loc(cur_loc)
                    # once found, MenuSearch close
                    MenuSearch.update_state(False)

                    # FIXME: There is small chance that the node is found with higher level
                    # which does not fit the load of the march.
                    break
                else:
                    logger.debug("The same node found, still search for next one")
                    image.screenshot("same_loc")
                    # If found the same node, MenuSearch closed
                    # Re-open to search for next one
                    MenuSearch.update_state(False)
                    MenuSearch.open()
            else:
                image.screenshot("gather_not_found")

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
            logger.info("FALLBACK !!! search for next rss type")
            Gather.search_rss(next_rss_type, rss_level)

    @staticmethod
    def find_and_click_deposit_button(rss_type: str):
        if MenuSearch.selected_rss_type == rss_type:
            logger.debug(f"Resource type {rss_type} is already selected")
            return

        deposite = MenuSearch.get_deposite_button(rss_type)
        deposite.click(
            verify=lambda: ocr.extract_text_from_rect(MenuSearch.get_search_button(rss_type))
            == "SEARCH"
        )

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
