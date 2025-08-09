import time
from dataclasses import dataclass

from src.api import adb, ldp
from src.utils import sleep_random


@dataclass(frozen=True)
class P:
    """Pixel Oxy"""

    x: int
    y: int

    @property
    def xy(self) -> tuple[int, int]:
        return (self.x, self.y)

    def click(self, delay=1200):
        ldp.tap(*self.xy)
        sleep_random(delay, delay + 200)

    def hold(self, duration=1000):
        ldp.long_press(*self.xy, duration)
        time.sleep(duration / 1000)

    def swipe(self, other: "P", base_duration=350):
        # Calculate distance between points
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        # Scale duration based on distance (adjust multiplier as needed)
        duration = int(base_duration * (distance / 500) + base_duration)
        # Ensure minimum duration
        duration = max(base_duration, duration)
        adb.swipe(*self.xy, *other.xy, duration)

    def __str__(self):
        return f"({self.x},{self.y})"
