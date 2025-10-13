import re
import time
from dataclasses import dataclass

from src.lib import logger
from src.lib.api import adb, ldp
from src.lib.utils import sleep_random


@dataclass(frozen=True)
class P:
    """Pixel Oxy"""

    x: int
    y: int

    @classmethod
    def from_coord(cls, coord_str: str) -> "P":
        """in form of 'X:388 Y:718'"""
        x, y = map(int, re.findall(r"\d+", coord_str))
        logger.debug(f"Creating P from coord: ({x}, {y})")
        return cls(x, y)

    @property
    def xy(self) -> tuple[int, int]:
        return (self.x, self.y)

    def click(self, delay: float = 1.2):
        ldp.tap(*self.xy)
        sleep_random(delay, delay + 0.2)

    def hold(self, duration: float = 1):
        """Hold the pixel for a duration (s)"""
        ldp.long_press(*self.xy, int(duration * 1000))
        time.sleep(duration)

    def swipe(self, other: "P", base_duration: float = 0.35, delay=0.5):
        base_duration *= 1000
        # Calculate distance between points
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        # Scale duration based on distance (adjust multiplier as needed)
        duration = int(base_duration * (distance / 500) + base_duration)
        # Ensure minimum duration
        duration = max(base_duration, duration)
        adb.swipe(*self.xy, *other.xy, duration)
        sleep_random(delay, delay + 0.3)

    def shift(self, offset_x, offset_y):
        return self.__class__(self.x + offset_x, self.y + offset_y)

    def distance(self, other: "P") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return ((dx**2) + (dy**2)) ** 0.5

    def __str__(self):
        return f"({self.x},{self.y})"

    def __eq__(self, other: "P"):
        if not isinstance(other, P):
            return False
        return self.x == other.x and self.y == other.y
