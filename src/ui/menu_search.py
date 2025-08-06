import re
from functools import cache
from math import ceil, floor

from src import logger
from src.element import BTN_SEARCH_NODE, Button, Distance, Gap, Length, P, RectZone, Width
from src.vision import cv, image


class MenuSearch:
    """
    Factory class to generate location of button in Rss Search Menu
    Open MenuSearch by choosing button "Search" in Main Menu
    KNOWN ISSUE: If the clicked button is wrong, it could be because the current user
    have not set loadouts
    """

    RSS_TYPES = ["food", "wood", "stone", "gold"]
    _GAP = Gap(290)

    # These private static buttons are captured based on Food
    # They are declared in private static scope to avoid being accessed directly
    _BTN_BASE_DEPOSITE = Button("Deposite", P(605, 908), P(740, 999))  # d
    _BTN_BASE_LEVEL_START = Button("LevelStart", P(508, 587), P(530, 623))  # d
    _BTN_BASE_SEARCH = Button("SearchRss", P(570, 700), P(783, 765))  # d

    _BTN_SEARCH_BARB = Button("Search Barbarians", P(300, 700), P(525, 765))

    RECT_DEPOSITE_LOC = RectZone("Deposite_Location", P(1356, 279), P(1505, 315))  # d

    # Shared state
    selected_rss_level = 0
    selected_rss_type = ""
    last_deposite_loc = ""
    _deposite_loc_template = re.compile(r"X:\d{1,4} Y:\d{1,4}")

    # menu state
    _is_open = False

    @classmethod
    def open(cls):
        if cls.is_open():
            logger.warning("Menu Search already opened")
            return

        logger.info("Open Search Menu")
        BTN_SEARCH_NODE.click(verify=cls.is_open)

    @classmethod
    def is_open(cls):
        """If Menu Search open, deposites should exist"""
        return cv.match_region_with_template(
            cls._BTN_BASE_DEPOSITE, image.RokImages.CROPLAND, verbose=True
        )

    @classmethod
    def reset(cls):
        """
        Reset the selected rss type
        This must be called when switching characters
        At this point, ROK already supported to not search out the nodes that someone else already
        being sending march to, either reset last_deposite_loc or not is okay
        """
        cls.selected_rss_level = 0
        cls.selected_rss_type = ""
        cls._is_open = False

    @classmethod
    def update_state(cls, state: bool):
        """state: true | false -> opened | closed"""
        cls._is_open = state

    @classmethod
    def update_last_deposite_loc(cls, loc):
        cls.last_deposite_loc = cls._refine_deposite_loc(loc)

    @classmethod
    def is_different_loc(cls, other_loc):
        return cls.last_deposite_loc != cls._refine_deposite_loc(other_loc)

    @classmethod
    def _refine_deposite_loc(cls, loc):
        # Loc will be form of X:20 Y:1000 (x and y can vary from 2-4 digits)
        if res := cls._deposite_loc_template.search(loc):
            return res.group()
        return ""

    @classmethod
    def update_selected_rss_level(cls, rss_level: int):
        if not (1 <= rss_level <= 8):
            raise ValueError(f"Invalid rss level: {rss_level}")
        cls.selected_rss_level = rss_level

    @classmethod
    def update_selected_rss_type(cls, rss_type: str):
        if rss_type not in cls.RSS_TYPES:
            raise ValueError(f"Invalid rss type: {rss_type}")
        cls.selected_rss_type = rss_type

    @classmethod
    @cache
    def get_deposite_button(cls, rss_type: str) -> Button:
        return cls._get_button(rss_type, cls._BTN_BASE_DEPOSITE)

    @classmethod
    @cache
    def get_search_button(cls, rss_type: str) -> Button:
        return cls._get_button(rss_type, cls._BTN_BASE_SEARCH)

    @classmethod
    @cache
    def get_level_button(cls, rss_type: str, rss_level: int) -> Button:
        """
        Getters for rss level buttons based on rss type and level
        """
        start_btn = cls._get_button(rss_type, cls._BTN_BASE_LEVEL_START)

        LEVEL_COUNT = 8
        SLIDER_LENGTH = Length(325)
        BUTTON_WIDTH = Width(22)
        SHIFT = Distance(6)  # shift to ensure the choosen point closer to the middle

        # rss_level 1 - 8
        step = (SLIDER_LENGTH - BUTTON_WIDTH) / (LEVEL_COUNT - 1)
        x1 = start_btn.p1.x + step * (rss_level - 1)
        x2 = start_btn.p2.x + step * (rss_level - 1)

        return Button(
            f"{rss_type}_Level_{rss_level}_Search",
            P(ceil(x1 + SHIFT), start_btn.p1.y),
            P(floor(x2 - SHIFT), start_btn.p2.y),
        )

    @classmethod
    def _get_button(cls, rss_type: str, base_button: Button) -> Button:
        if rss_type not in cls.RSS_TYPES:
            raise ValueError(f"Unknown resource type: {rss_type}")

        index = cls.RSS_TYPES.index(rss_type) + 1  # 1-based index like AHK
        offset = (index - 1) * cls._GAP

        p1 = P(base_button.p1.x + offset, base_button.p1.y)
        p2 = P(base_button.p2.x + offset, base_button.p2.y)
        return Button(f"{rss_type}_{base_button.name}", p1, p2)
