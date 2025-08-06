import ctypes
import datetime
import functools
import random
import time
from time import sleep
from typing import Callable

import pygetwindow as gw

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
            time_fmt = lambda s, e: f"{s.strftime('%H:%M')}-{e.strftime('%H:%M')}"
            for start, end in periods:
                if start <= now <= end:
                    logger.info(f"Schedule action: {time_fmt(start, end)}")
                    return func(*args, **kwargs)
            # If current time is not in any period
            period_str = ", ".join(f"{time_fmt(s, e)}" for s, e in periods)
            logger.warning(
                f"[{func.__name__}] skipped: now={now.strftime('%H:%M:%S')}, "
                f"outside allowed period(s): {period_str}"
            )
            return None

        return wrapper

    return decorator


def get_scaling_factor():
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    hdc = user32.GetDC(0)
    logical_screen = user32.GetSystemMetrics(0)
    physical_screen = gdi32.GetDeviceCaps(hdc, 118)
    user32.ReleaseDC(0, hdc)
    scaling_factor = physical_screen / logical_screen
    logger.info(f"Scale ratio: {scaling_factor}")
    return scaling_factor


def get_taskbar_height():
    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    SPI_GETWORKAREA = 0x0030
    rect = RECT()
    ctypes.windll.user32.SystemParametersInfoA(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    work_height = rect.bottom - rect.top
    physical_height = ctypes.windll.user32.GetSystemMetrics(1)
    return physical_height - work_height


def reallocate_and_resize(window_title, slot_index=0, total_slots=2):
    """
    Place the specified window (by unique title) in the correct 'slot' (top=0),
    based on screen size, aspect ratio, and DPI.
    """
    # scaling = get_scaling_factor()
    scaling = 1
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    taskbar_height = get_taskbar_height()
    usable_height = screen_height - taskbar_height

    aspect_width = 1920
    aspect_height = 1080
    ASPECT_RATIO = aspect_width / aspect_height

    window_height = int(usable_height / total_slots)
    window_width = int(window_height * ASPECT_RATIO)

    logical_width = int(window_width / scaling)
    logical_height = int(window_height / scaling)

    # Position calculation
    x = screen_width - logical_width
    y = logical_height * slot_index

    # Get the target window
    windows = [w for w in gw.getWindowsWithTitle(window_title) if w.visible]
    if not windows:
        logger.error(f"No window with title '{window_title}' found.")
        return

    win = windows[0]
    win.moveTo(x, y)
    win.resizeTo(logical_width, logical_height)
    logger.info(
        f"Window '{window_title}' placed at slot {slot_index} "
        f"({x},{y}), size {logical_width}x{logical_height}"
    )


def timed_polling(timeout=30, interval=1.0, info=""):
    """
    Decorator to wrap a polling function with timeout logic.

    The wrapped function should return True when the desired condition is met,
    otherwise return False or None to keep polling.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            deadline = time.monotonic() + timeout
            if info:
                logger.info(info)
            while time.monotonic() < deadline:
                if func(*args, **kwargs):
                    duration = time.perf_counter() - start_time
                    logger.info(f"Completed in {duration:.2f} seconds.")
                    return
                logger.debug(f"Not ready, retry checking after {interval} second(s)")
                time.sleep(interval)
            duration = time.perf_counter() - start_time
            logger.error(f"Timeout after {duration:.2f} seconds.")
            raise TimeoutError("Timeout exceeded")

        return wrapper

    return decorator


def retry(max_attempts=3, delay=1.0, info="", action_if_fail: Callable = None):
    """
    Retry decorator.

    Args:
        max_attempts (int): Max number of attempts before giving up.
        delay (float): Delay (seconds) between attempts.
    """

    def decorator(func: Callable[[], bool]):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if info:
                logger.debug(info)
            for attempt in range(1, max_attempts + 1):
                result = func(*args, **kwargs)
                if result:
                    return result
                if action_if_fail:
                    action_if_fail()
                logger.warning(f"[retry] Attempt {attempt} failed, retrying in {delay}s...")
                time.sleep(delay)
            raise TimeoutError(f"Failed to proceed action with {max_attempts} retries")

        return wrapper

    return decorator
