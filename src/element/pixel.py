import time

from src.api import adb, ldp
from src.utils import sleep_random


class P:
    """Pixel Oxy"""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self._xy = (x, y)

    def click(self, delay=1200):
        adb.tap(self.x, self.y)
        sleep_random(delay, delay + 200)

    def hold(self, duration=1000):
        ldp.long_press(self.x, self.y, duration)
        time.sleep(duration / 1000)

    def swipe(self, other: "P", duration=300):
        adb.swipe(self.x, self.y, other.x, other.y, duration)
        self.hold(1500)

    def __str__(self):
        return f"({self.x},{self.y})"
