import time

from src.api import adb, ldp
from src.utils import sleep_random


class P:
    """Pixel Oxy"""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @property
    def xy(self) -> tuple[int, int]:
        return (self.x, self.y)

    def click(self, delay=1200):
        adb.tap(*self.xy)
        sleep_random(delay, delay + 200)

    def hold(self, duration=1000):
        ldp.long_press(*self.xy, duration)
        time.sleep(duration / 1000)

    def swipe(self, other: "P", duration=300):
        adb.swipe(*self.xy, *other.xy, duration)
        self.hold(1500)

    def __str__(self):
        return f"({self.x},{self.y})"

    def __repr__(self):
        return f"P(x={self.x}, y={self.y})"
