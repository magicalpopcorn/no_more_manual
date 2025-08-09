import random
import time
from dataclasses import dataclass

from src import logger, utils

from .pixel import P


@dataclass(frozen=True)
class RectZone:
    name: str
    p1: P
    p2: P
    padding_ratio: float = 0.2

    def _get_corners(self):
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        return [
            P(x1, y1),
            P(x2, y1),
            P(x2, y2),
            P(x1, y2),
        ]

    def locate(self):
        for corner in self._get_corners():
            logger.debug(corner)
            time.sleep(1)

    def get_random_P(self):
        """Return random P inside the rectangle"""
        width = self.p2.x - self.p1.x
        height = self.p2.y - self.p1.y

        pad_x = int(width * self.padding_ratio)
        pad_y = int(height * self.padding_ratio)

        x = random.randint(self.p1.x + pad_x, self.p2.x - pad_x)
        y = random.randint(self.p1.y + pad_y, self.p2.y - pad_y)
        return P(x, y)

    def get_center_P(self):
        """Return the center P of the rectangle"""
        center_x = (self.p1.x + self.p2.x) // 2
        center_y = (self.p1.y + self.p2.y) // 2
        return P(center_x, center_y)

    def drag(self, offset_x=(0,), offset_y=(0,), duration=1000):
        """
        Fixed vertical drag	 |  offset_y=(-200,)
        Random scroll right	 |  offset_x=(100, 150)
        Diagonal flick	     |  offset_x=(30, 50), offset_y=(-150,)
        No drag	             |  offset_x=(0,), offset_y=(0,)
        """
        start = self.get_random_P()

        # Resolve offset_x
        if len(offset_x) == 1:
            dx = offset_x[0]
        else:
            dx = random.randint(*offset_x)

        # Resolve offset_y
        if len(offset_y) == 1:
            dy = offset_y[0]
        else:
            dy = random.randint(*offset_y)

        target = P(start.x + dx, start.y + dy)
        # Duration can also be randomized or fixed
        start.swipe(target, duration)
        start.hold(1500)

    def swipe(self, other: "RectZone"):
        """
        Swipe from one rectangle to another.
        This is useful for navigating between UI elements.
        """
        start = self.get_random_P()
        target = other.get_center_P()
        start.swipe(target)

    def shift(self, offset_x=0, offset_y=0):
        """
        Shift the rectangle by the given offsets.
        This is useful for adjusting the rectangle position dynamically.
        """
        new_p1 = P(self.p1.x + offset_x, self.p1.y + offset_y)
        new_p2 = P(self.p2.x + offset_x, self.p2.y + offset_y)
        return self.__class__(self.name, new_p1, new_p2, self.padding_ratio)

    def __str__(self):
        return f"{self.name}: [{self.p1} - {self.p2}]"

    def to_tuple(self):
        return (*self.p1.xy, *self.p2.xy)


@dataclass(frozen=True)
class Button(RectZone):
    """
    Represents an interactive button in the game UI, defined by a rectangular zone.

    This class is a higher-level interface built on top of `P` and `RectZone`,
    specifically designed for game elements that the Rise of Kingdoms (RoK) system
    can easily detect or react to (e.g., visual buttons).

    Init:
        Button(name, p1, p2)
        - p1: Top-left corner (instance of P)
        - p2: Bottom-right corner (instance of P)

    Behavior:
        - Provides random points within the rectangular area.
        - Supports precise click, and hold actions.
        - Can be visually located by corner highlights for debugging or mapping.

    This class assumes the defined rectangle corresponds to a visible and clickable
    region in the RoK UI, such as a confirm button, VIP icon, or chat bubble.
    """

    @utils.retry(max_attempts=3)
    def click(self, delay=1200, verify=None):
        """
        Click a random P inside Button with defined padding
        If verify is provided, use verify to check if the button is clicked successfully
        """
        p = self.get_random_P()
        logger.debug(f"Click {self.name}{p}")
        p.click(delay)

        if verify is not None:
            return verify()
        return True

    @utils.retry(max_attempts=3)
    def hold(self, duration=1200, verify=None):
        """
        Hold a random P inside Button with defined padding
        If verify is provided, use verify to check if the button is held successfully
        """
        p = self.get_random_P()
        logger.debug(f"Hold {self.name}{p} - {duration} ms")
        p.hold(duration)

        if verify is not None:
            return verify()
        return True


@dataclass(frozen=True)
class TextButton(Button):
    """
    This is still button, but with text inside
    We can capture the text and verify

    TODO: Implement TextButton
    """


# Captured with 1920x1080, LDPlayer

# USER INTERFACE
CENTER_POINT = Button("Central_Point", P(920, 486), P(1035, 559))  # d
BTN_ASSIST = Button("Assist", P(1121, 637), P(1216, 662))

# ASSIST INTERFACE
FOOD_SLIDER = P(911, 397)
WOOD_SLIDER = P(911, 487)
STONE_SLIDER = P(911, 577)
GOLD_SLIDER = P(911, 667)

BTN_TRANSPORT = TextButton("Transport", P(1051, 762), P(1166, 797))

# BOOKMARK BUTTONS
BTN_BM = Button("Bookmark", P(493, 16), P(502, 23))
BTN_BM_TYPE_FRIEND = Button("Marker_Friend", P(916, 305), P(991, 322))
BTN_BM_GO_F1 = Button("Pos 1", P(1311, 382), P(1386, 397))

# FARMING INTERFACE
BTN_SEARCH_NODE = Button("Search_Button", P(50, 780), P(120, 840))  # d
BTN_GATHER = TextButton("Gather", P(1328, 693), P(1535, 760))  # d

# BUTTON ISSUE
BTN_ISSUE_CONFIRM = TextButton("Confirm", P(861, 672), P(1066, 717))
