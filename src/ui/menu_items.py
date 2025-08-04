import json
import os

from src import const, logger, utils
from src.element import Button, Gap, P, RectZone, TextButton
from src.rok_profile import RokProfile
from src.vision import cv, image, ocr

from .base_menu import _Menu
from .menu_main import MenuMain

CACHE_DIR = os.path.join(const.PROJECT_ROOT, "tmp", ".cache")


class MenuItems(_Menu):
    """
    Menu Items

    RESOURCES | speedups | BOOSTS | equipment | armaments | other

    Only RESOURCES and BOOSTS are handled for now.

    Clicking a sub-menu opens a 2:1 layout:
    - Left: grid of items (6 per row max)
    - Right: info pane showing selected item information

    Grid layout:
        - Base item button at top-left: (280, 240) to (395, 350)
        - Horizontal gap between items: 165 px
        - Vertical gap between rows:    160 px
    """

    BTN_RESOURCES = TextButton("RESOURCES", P(261, 84), P(459, 165))  # d
    BTN_BOOSTS = TextButton("BOOSTS", P(723, 84), P(920, 165))  # d

    _BTN_BASE_ITEM = Button("Item_1_1", P(290, 237), P(447, 398))  # top left item
    _ITEM_WIDTH = Gap(240)  # Horizontal spacing between items (left edge)
    _ITEM_HEIGHT = Gap(228)  # Vertical spacing between rows (top edge)

    # Right side of the sub-menu
    _RECT_ITEM_NAME = RectZone("Item_name", P(1270, 445), P(1655, 550))
    BTN_USE_ITEM = TextButton("USE", P(1360, 890), P(1585, 970), 0.3)

    # If the buff already exits, confirm popup
    BTN_NOTICE_YES = TextButton("YES", P(550, 730), P(888, 807))
    BTN_NOTICE_NO = TextButton("NO", P(1050, 730), P(1395, 807))

    # Common items
    BOOST_GATHER_24 = "24-Hour Enhanced Gathering"
    BOOST_GATHER_8 = "8-Hour Enhanced Gathering"
    BOOST_SHIELD_8 = "8-Hour Peace Shield"

    def __init__(self, char_id: str):
        """Each character has their own item inventory"""
        self.char_id = char_id
        self._cache_path = os.path.join(CACHE_DIR, "items.json")
        self._cache_data = self._load_cache()
        self.profile = RokProfile()

    def __del__(self):
        self._save_cache()

    @classmethod
    def open(cls):
        if cls.is_open():
            logger.debug("Menu Items already opened")
            return
        MenuMain.open_sub_menu()
        super().open()
        MenuMain.BTN_ITEMS.click(verify=cls.is_open)

    @classmethod
    def is_open(cls):
        return cv.match_region_with_template(cls.BTN_RESOURCES, image.RokImages.BTN_ITEMS_RESOURCES)

    def _load_cache(self):
        if os.path.exists(self._cache_path):
            with open(self._cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self._cache_path), exist_ok=True)
        with open(self._cache_path, "w", encoding="utf-8") as f:
            json.dump(
                self._cache_data,
                f,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )

    def scan(self, item_type: Button):
        """
        Scans the grid and caches item names and their positions for the current character.
        """
        logger.info(f"Scan the whole inventory of char {self.char_id}, type: {item_type.name}")
        if self.char_id not in self._cache_data:
            self._cache_data[self.char_id] = {}

        item_type.click()
        max_rows, max_cols = 3, 4
        last_text = ""

        for i in range(max_rows):
            for j in range(max_cols):
                btn = self.get_item_by_pos(i, j)
                btn.click()
                text = self._get_item_name()

                if text == last_text:
                    logger.warning("Reached end of visible grid. Stopping scan.")
                    return

                last_text = text
                if text:
                    self._cache_data[self.char_id][text] = [i, j]
                    logger.debug(f"Cached '{text}' at ({i}x{j})")

    # method for sub-menu BOOSTS
    def get_item_by_pos(self, index_v: int, index_h: int) -> Button:
        """
        Returns a button for an item based on grid position.

        Args:
            index_v (int): Vertical index (row), 0 to 2
            index_h (int): Horizontal index (col), 0 to 3

        Returns:
            Button: Clickable button at given position
        """
        if not (0 <= index_v <= 2 and 0 <= index_h <= 3):
            raise ValueError("Invalid item position: outside grid bounds")

        x_offset = index_h * self._ITEM_WIDTH
        y_offset = index_v * self._ITEM_HEIGHT

        p1 = P(self._BTN_BASE_ITEM.p1.x + x_offset, self._BTN_BASE_ITEM.p1.y + y_offset)
        p2 = P(self._BTN_BASE_ITEM.p2.x + x_offset, self._BTN_BASE_ITEM.p2.y + y_offset)

        return Button(f"Item_{index_v}_{index_h}", p1, p2)

    def get_item_by_name(self, item_type: TextButton, item_name: str) -> Button | None:
        """
        Retrieves an item button by item_name, using cached position if available.
        If not found, rescans and retries once.
        Item will be clicked already, just use it
        """
        item_type.click(verify=lambda: self.is_item_type_menu_open(item_type))

        if self.char_id in self._cache_data and item_name in self._cache_data[self.char_id]:
            i, j = self._cache_data[self.char_id][item_name]
            logger.debug(f"Using cached position for '{item_name}' at ({i}x{j})")
            item_btn = self.get_item_by_pos(i, j)
            item_btn.click()
            if self._get_item_name() == item_name:
                return item_btn

        self.scan(item_type)
        if self.char_id in self._cache_data and item_name in self._cache_data[self.char_id]:
            i, j = self._cache_data[self.char_id][item_name]
            logger.debug(f"Found '{item_name}' after rescanning at ({i}x{j})")
            btn = self.get_item_by_pos(i, j)
            btn.click()
            return btn

        logger.warning(f"Item '{item_name}' not found for character {self.char_id}.")
        return None

    def get_boost_item_by_name(self, item_name: str) -> Button | None:
        return self.get_item_by_name(self.BTN_BOOSTS, item_name)

    def use_boost_item(self, force=False):
        logger.debug(f"Use item with {"" if force else "no "}force")
        self.BTN_USE_ITEM.click()

        # Check if popup Notice exists
        if ocr.extract_text_from_rect(self.BTN_NOTICE_YES) == self.BTN_NOTICE_YES.name:
            if force:
                self.BTN_NOTICE_YES.click()
            else:
                self.BTN_NOTICE_NO.click()

    @classmethod
    def _get_item_name(cls):
        return " ".join(ocr.extract_multi_text_from_rect(cls._RECT_ITEM_NAME))

    @classmethod
    def is_item_type_menu_open(cls, item_type: TextButton):
        match item_type.name:
            case cls.BTN_BOOSTS.name:
                img = image.RokImages.BTN_ITEMS_BOOSTS
            case _:
                raise NotImplemented(f"Item type: {item_type.name} not yet captured")
        return cv.match_region_with_template(item_type, img)
