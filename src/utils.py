import ctypes
import datetime
import functools
import random
import time
from time import sleep

import pygetwindow as gw

from src import logger
from src.api import adb


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


def reallocate_and_resize(window_title, slot_index=0, total_slots=3):
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
