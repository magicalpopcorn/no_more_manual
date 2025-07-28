import math
import random
import time

from src import logger
from src.driver import mouse

from .pixel import P


class RectZone:
    def __init__(self, name: str, p1: P, p2: P, padding_ratio=0.15):
        self.name = name
        self.p1 = p1
        self.p2 = p2
        self.padding = padding_ratio

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
            corner.mouse_move()
            time.sleep(1)

    def get_random_P(self):
        """Return random P inside the rectangle"""
        width = self.p2.x - self.p1.x
        height = self.p2.y - self.p1.y

        pad_x = int(width * self.padding)
        pad_y = int(height * self.padding)

        x = random.randint(self.p1.x + pad_x, self.p2.x - pad_x)
        y = random.randint(self.p1.y + pad_y, self.p2.y - pad_y)
        return P(x, y)

    def __str__(self):
        return f"{self.name}: [{self.p1} - {self.p2}]"

    def to_tuple(self):
        return (self.p1.x, self.p1.y, self.p2.x, self.p2.y)

    def drag(self, offset_x=(0,), offset_y=(0,), step_size=5):
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

        logger.debug(
            f"Drag {self.name} from {start} to {target} " f"(offset=({dx}, {dy}), step={step_size})"
        )

        start.mouse_move()
        time.sleep(0.1)
        mouse.MouseLeftDown()
        time.sleep(0.5)

        steps = max(5, math.ceil(max(abs(dx), abs(dy)) / step_size))
        step_x = dx / steps
        step_y = dy / steps

        for i in range(1, steps + 1):
            x = round(start.x + step_x * i)
            y = round(start.y + step_y * i)
            P(x, y).mouse_move(delay=0.01)

        time.sleep(1)
        mouse.MouseLeftUp()


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
        - Supports precise mouse movement, click, and hold actions.
        - Can be visually located by corner highlights for debugging or mapping.

    This class assumes the defined rectangle corresponds to a visible and clickable
    region in the RoK UI, such as a confirm button, VIP icon, or chat bubble.
    """

    def click(self, delay=800):
        p = self.get_random_P()
        p.mouse_move()
        logger.debug(f"Click {self.name}{p}")
        p.click(delay)

    def hold(self, duration=1000):
        p = self.get_random_P()
        logger.debug(f"Hold {self.name}{p} - {duration} ms")
        p.hold(duration)


class TextButton(Button):
    """
    This is still button, but with text inside
    We can capture the text and verify

    TODO: Implement TextButton
    """


# Captured with 1920x1080, DPI scaling 125%, Client mode
# diff from Window mode and Client mode (-9, -38)
# MAIN BUTTONS
BTN_HOME = Button("Home", P(1808, 978), P(1884, 1044))
BTN_HOME_BUILDINGS = Button("Buildings", P(1572, 994), P(1628, 1036))

# USER INTERFACE
CENTER_POINT = Button("Central_Point", P(910, 483), P(1031, 584))
BTN_ASSIST = Button("Assist", P(1121, 637), P(1216, 662))

# ASSIST INTERFACE
FOOD_SLIDER = P(911, 397)
WOOD_SLIDER = P(911, 487)
STONE_SLIDER = P(911, 577)
GOLD_SLIDER = P(911, 667)

BTN_TRANSPORT = Button("Transport", P(1051, 762), P(1166, 797))

# BOOKMARK BUTTONS
BTN_BM = Button("Bookmark", P(493, 16), P(502, 23))
BTN_BM_TYPE_FRIEND = Button("Marker_Friend", P(916, 305), P(991, 322))
BTN_BM_GO_F1 = Button("Pos 1", P(1311, 382), P(1386, 397))

# FARMING INTERFACE
BTN_SEARCH_NODE = Button("Search_Menu", P(1846, 884), P(1881, 912))
BTN_GATHER = Button("Gather", P(546, 647), P(716, 692))  # LEFT

# BUTTON ISSUE
BTN_ISSUE_CONFIRM = Button("Confirm", P(861, 672), P(1066, 717))
