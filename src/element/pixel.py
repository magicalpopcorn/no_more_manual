import time

from src import const, logger
from src.dpi import DPIAwareMixin
from src.driver import mouse
from src.utils import sleep_random


class P(DPIAwareMixin):
    """Pixel Oxy"""

    def __init__(self, x: int, y: int):
        self.x = int(x * self._ratio)
        self.y = int(y * self._ratio)
        self._xy = (x, y)

    def mouse_move(self, delay=0.1):
        mouse.MouseMove(*self._xy)
        time.sleep(delay)

    def click(self, delay=800):
        mouse.Click(*self._xy)
        sleep_random(delay, delay + 200)

    def hold(self, duration=1000):
        self.mouse_move()
        mouse.MouseLeftDown()
        sleep_random(duration, duration + 200)
        mouse.MouseLeftUp()

    def __str__(self):
        return f"({self.x},{self.y})"
