import os

import yaml

from src import const, logger
from src.element import SC_CLOSE, SC_ITEMS, Button, Gap, P, RectZone, TextButton
from src.rok_profile import Character, RokProfile
from src.vision import ocr

from .base_menu import _Menu

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

    BTN_RESOURCES = TextButton("RESOURCES", P(273, 140), P(472, 180))
    BTN_BOOSTS = TextButton("BOOSTS", P(730, 140), P(935, 180))

    _BTN_BASE_ITEM = Button("_", P(280, 240), P(395, 350))  # top left item
    _ITEM_WIDTH = Gap(165)  # Horizontal spacing between items (left edge)
    _ITEM_HEIGHT = Gap(160)  # Vertical spacing between rows (top edge)

    # Right side of the sub-menu
    _ITEM_NAME_ZONE = RectZone("Item_name", P(1325, 435), P(1655, 510))
    BTN_USE_ITEM = TextButton("USE", P(1390, 810), P(1560, 890), 0.3)

    # Common items
    BOOST_GATHER_24 = "24-Hour Enhanced Gathering"
    BOOST_GATHER_8 = "8-Hour Enhanced Gathering"

    def __init__(self, char_id: str):
        """Each character has their own item inventory"""
        self.char_id = char_id
        self._cache_path = os.path.join(CACHE_DIR, "items.yml")
        self._cache_data = self._load_cache()
        self.profile = RokProfile()

    def __del__(self):
        self._save_cache()

    @classmethod
    def open(cls):
        super().open()
        SC_ITEMS.press()

    def _load_cache(self):
        if os.path.exists(self._cache_path):
            with open(self._cache_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self._cache_path), exist_ok=True)
        with open(self._cache_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                self._cache_data, f, sort_keys=True, allow_unicode=True, default_flow_style=False
            )

    def scan(self, item_type: Button):
        """
        Scans the grid and caches item names and their positions for the current character.
        """
        logger.info(f"Scan the whole inventory of char {self.char_id}, type: {item_type.name}")
        if self.char_id not in self._cache_data:
            self._cache_data[self.char_id] = {}

        item_type.click()
        max_rows, max_cols = 4, 6
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
            index_v (int): Vertical index (row), starting from 0
            index_h (int): Horizontal index (col), 0 to 5

        Returns:
            Button: Clickable button at given position
        """
        if index_h > 5 or index_v < 0 or index_h < 0:
            raise ValueError("Invalid item position: outside grid bounds")

        x_offset = index_h * self._ITEM_WIDTH
        y_offset = index_v * self._ITEM_HEIGHT

        p1 = P(self._BTN_BASE_ITEM.p1.x + x_offset, self._BTN_BASE_ITEM.p1.y + y_offset)
        p2 = P(self._BTN_BASE_ITEM.p2.x + x_offset, self._BTN_BASE_ITEM.p2.y + y_offset)

        return Button(f"Item_{index_v}_{index_h}", p1, p2)

    def get_item_by_name(self, item_type: Button, item_name: str) -> Button | None:
        """
        Retrieves an item button by item_name, using cached position if available.
        If not found, rescans and retries once.
        Item will be clicked already, just use it
        """
        item_type.click()
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
        btn_yes = TextButton("YES", P(660, 665), P(920, 730))
        btn_no = TextButton("NO", P(1010, 665), P(1270, 730))
        self.BTN_USE_ITEM.click()

        # Check if popup Notice exists
        if ocr.extract_text_from_rect(btn_yes) == btn_yes.name:
            if force:
                btn_yes.click()
            else:
                btn_no.click()

    def _get_item_name(self):
        return ocr.extract_text_from_rect(self._ITEM_NAME_ZONE).replace("\n", " ").strip()
