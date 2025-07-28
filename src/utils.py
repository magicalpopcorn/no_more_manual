import datetime
import functools
import random
from time import sleep

from src import logger


def sleep_random(a: int, b=0):
    """Sleep random (a,b) ms"""
    a, b = (a, b) if b > a else (b, a)
    sleep((random.randint(a, b)) / 1000)


def only_during_periods(periods):
    """
    Decorator that allows function execution only during the given time period(s).
    Supports:
        - A single tuple: (start_time, end_time)
        - A list of tuples: [(start1, end1), (start2, end2), ...]

    Example:
    @only_during_periods([
        (time(6, 0), time(12, 0)),    # Morning
        (time(18, 0), time(23, 0)),   # Evening
    ])

    @only_during_periods((time(6, 0), time(12, 0)))
    """
    # Normalize to a list of tuples
    if isinstance(periods, tuple) and isinstance(periods[0], datetime.time):
        periods = [periods]

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = datetime.datetime.now().time()
            for start, end in periods:
                if start <= now <= end:
                    return func(*args, **kwargs)
            # If current time is not in any period
            period_str = ", ".join(
                f"{s.strftime('%H:%M')}-{e.strftime('%H:%M')}" for s, e in periods
            )
            logger.warning(
                f"[{func.__name__}] skipped: now={now.strftime('%H:%M:%S')}, "
                f"outside allowed period(s): {period_str}"
            )
            return None

        return wrapper

    return decorator
