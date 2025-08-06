import json
import os
import re
from dataclasses import dataclass

from src import const, logger
from src.element import Button, Gap, P, RectZone, TextButton
from src.rok_profile import RokProfile
from src.vision import cv, image, ocr

from .base_menu import _Menu
from .menu_main import MenuMain

DATA_DIR = os.path.join(const.PROJECT_ROOT, "tmp", ".data")


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

    BTN_STATISTICS = Button("Statistics", P(1775, 900), P(1875, 980))

    # If the buff already exits, confirm popup
    BTN_NOTICE_YES = TextButton("YES", P(550, 730), P(888, 807))
    BTN_NOTICE_NO = TextButton("NO", P(1050, 730), P(1395, 807))

    # Common items
    BOOST_GATHER_24 = "24-Hour Enhanced Gathering"
    BOOST_GATHER_8 = "8-Hour Enhanced Gathering"
    BOOST_SHIELD_8 = "8-Hour Peace Shield"

    ITEM_PATH = os.path.join(DATA_DIR, "items.json")

    def __init__(self, char_id: str):
        """Each character has their own item inventory"""
        self.char_id = char_id
        self._item_data = self._load_data()
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

    def _load_data(self):
        if os.path.exists(self.ITEM_PATH):
            with open(self.ITEM_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.ITEM_PATH), exist_ok=True)
        with open(self.ITEM_PATH, "w", encoding="utf-8") as f:
            json.dump(
                self._item_data,
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
        if self.char_id not in self._item_data:
            self._item_data[self.char_id] = {}

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
                    self._item_data[self.char_id][text] = [i, j]
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

        if self.char_id in self._item_data and item_name in self._item_data[self.char_id]:
            i, j = self._item_data[self.char_id][item_name]
            logger.debug(f"Using cached position for '{item_name}' at ({i}x{j})")
            item_btn = self.get_item_by_pos(i, j)
            item_btn.click()
            if self._get_item_name() == item_name:
                return item_btn

        self.scan(item_type)
        if self.char_id in self._item_data and item_name in self._item_data[self.char_id]:
            i, j = self._item_data[self.char_id][item_name]
            logger.debug(f"Found '{item_name}' after rescanning at ({i}x{j})")
            btn = self.get_item_by_pos(i, j)
            btn.click(verify=lambda: self._get_item_name() == item_name)
            return btn

        logger.warning(f"Item '{item_name}' not found for character {self.char_id}.")
        return None

    def get_boost_item_by_name(self, item_name: str) -> Button | None:
        return self.get_item_by_name(self.BTN_BOOSTS, item_name)

    def use_boost_item(self, force=False):
        logger.debug(f"Use item with {"" if force else "no "}force")
        self.BTN_USE_ITEM.click()

        # Check if popup Notice exists
        is_notice_menu_open = (
            lambda: ocr.extract_text_from_rect(self.BTN_NOTICE_YES) == self.BTN_NOTICE_YES.name
        )
        if is_notice_menu_open():
            if force:
                self.BTN_NOTICE_YES.click(verify=lambda: not is_notice_menu_open())
            else:
                self.BTN_NOTICE_NO.click(verify=lambda: not is_notice_menu_open())

    @classmethod
    def _get_item_name(cls):
        return " ".join(ocr.extract_multi_text_from_rect(cls._RECT_ITEM_NAME))

    @classmethod
    def is_item_type_menu_open(cls, item_type: TextButton):
        match item_type.name:
            case cls.BTN_BOOSTS.name:
                img = image.RokImages.BTN_ITEMS_BOOSTS
            case _:
                raise NotImplementedError(f"Item type: {item_type.name} not yet captured")
        return cv.match_region_with_template(item_type, img)


class ResourceAmount:
    """
    Stores resource values in millions (float).
    Supports parsing from strings like '100.0M' or '1.4B',
    conversion to int, and arithmetic operations.
    """

    MULTIPLIERS = {"M": 1, "B": 1000}

    def __init__(self, value: float | str):
        if isinstance(value, str):
            value = self.from_str(value).value
        elif not isinstance(value, (int, float)):
            raise TypeError(
                f"ResourceAmount must be initialized with a number or string, got {type(value)}"
            )
        self.value = value  # always in millions

    @classmethod
    def from_str(cls, s: str):
        """
        Parse a resource string like '100.0M' or '1.4B' to ResourceAmount.
        """
        match = re.match(r"([\d.,]+)\s*([MB])", s.strip().upper())
        if not match:
            raise ValueError(f"Invalid resource format: {s}")
        num, unit = match.groups()
        num = float(num.replace(",", ""))
        return cls(num * cls.MULTIPLIERS[unit])

    def to_int(self):
        """
        Convert to integer (units).
        """
        return int(self.value * 1_000_000)

    def __add__(self, other):
        if not isinstance(other, ResourceAmount):
            return NotImplemented
        return ResourceAmount(self.value + other.value)

    def __sub__(self, other):
        if not isinstance(other, ResourceAmount):
            return NotImplemented
        result = self.value - other.value
        # OCR bug: if result < 0 and self.value starts with 1, it's likely a misread 7
        if result < 0 and str(int(self.value))[0] == "1":
            # Replace first digit with 7 and recalculate
            corrected_str = "7" + str(int(self.value))[1:]
            try:
                corrected_value = float(corrected_str + str(self.value)[len(corrected_str) :])
                self.value = corrected_value  # update self.value
            except Exception:
                pass  # fallback to original result if conversion fails
        return ResourceAmount(self.value - other.value)

    def after_tax(self, tax_percent: float) -> "ResourceAmount":
        """
        Returns a new ResourceAmount after tax reduction.
        Args:
            tax_percent (float): Tax percentage (e.g., 10 for 10%).
        Returns:
            ResourceAmount: Value after tax reduction.
        """
        return ResourceAmount(self.value * (1 - tax_percent / 100))

    def __str__(self):
        if self.value >= 1000:
            return f"{self.value / 1000:.1f}B"
        return f"{self.value:.1f}M"

    def __repr__(self):
        return f"ResourceAmount({self.value:.1f}M)"


@dataclass
class ResourceSet:
    food: ResourceAmount
    wood: ResourceAmount
    stone: ResourceAmount
    gold: ResourceAmount

    @classmethod
    def from_list(cls, values):
        if len(values) != 4:
            raise ValueError(f"ResourceSet requires exactly 4 values, got {len(values)}: {values}")
        return cls(*values)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ResourceAmount(data["food"]),
            ResourceAmount(data["wood"]),
            ResourceAmount(data["stone"]),
            ResourceAmount(data["gold"]),
        )

    def __add__(self, other: "ResourceSet") -> "ResourceSet":
        return ResourceSet(
            self.food + other.food,
            self.wood + other.wood,
            self.stone + other.stone,
            self.gold + other.gold,
        )

    def __sub__(self, other: "ResourceSet") -> "ResourceSet":
        return ResourceSet(
            self.food - other.food,
            self.wood - other.wood,
            self.stone - other.stone,
            self.gold - other.gold,
        )

    def after_tax(self, tax_percent: float) -> "ResourceSet":
        return ResourceSet(
            self.food.after_tax(tax_percent),
            self.wood.after_tax(tax_percent),
            self.stone.after_tax(tax_percent),
            self.gold.after_tax(tax_percent),
        )

    def to_dict(self):
        return {
            "food": str(self.food),
            "wood": str(self.wood),
            "stone": str(self.stone),
            "gold": str(self.gold),
        }

    def __str__(self):
        return self.to_dict().__str__()


class MenuStatistics(_Menu):
    RECT_TITLE = RectZone("YOUR RESOURCES & SPEEDUPS", P(605, 97), P(1310, 147))

    RECT_FROM_ITEMS = RectZone("From_Items", P(920, 350), P(1045, 750))
    RECT_TOTAL_RSS = RectZone("Total_Resources", P(1425, 350), P(1550, 750))

    RSS_PATH = os.path.join(DATA_DIR, "rss.json")

    def __init__(self, char_id: str):
        """Each character has their own item inventory"""
        self.char_id = char_id
        self.total_rss: ResourceSet = None
        self.avail_rss: ResourceSet = None

    @classmethod
    def open(cls):
        super().open()
        if cls.is_open():
            logger.debug("Menu Statistics already opened")
            return
        MenuItems.BTN_STATISTICS.click(verify=cls.is_open)

    def get_total_rss(self) -> ResourceSet:
        if not self.total_rss:
            self.total_rss = ResourceSet.from_list(self.get_rss_values(self.RECT_TOTAL_RSS))
        logger.info(f"Total Resources: {self.total_rss}")
        return self.total_rss

    def get_available_rss(self) -> ResourceSet:
        if not self.avail_rss:
            from_item_rss = ResourceSet.from_list(self.get_rss_values(self.RECT_FROM_ITEMS))
            self.avail_rss = self.get_total_rss() - from_item_rss
        logger.info(f"Available Resources: {self.avail_rss}")
        return self.avail_rss

    def save_rss_stats(self):
        # Load existing data
        if os.path.exists(self.RSS_PATH):
            with open(self.RSS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        data[self.char_id] = {
            "total_rss": self.total_rss.to_dict(),
            "avail_rss": self.avail_rss.to_dict(),
        }

        os.makedirs(os.path.dirname(self.RSS_PATH), exist_ok=True)
        with open(self.RSS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def get_rss_values(rect: RectZone):
        return list(
            map(
                ResourceAmount.from_str,
                ocr.extract_multi_text_from_rect(rect, whitelist="0123456789.MB", save=True),
            )
        )
