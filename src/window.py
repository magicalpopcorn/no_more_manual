import ctypes
import time

import win32con
import win32gui

from src import const, logger


class ROKWindow:
    _hwnd = None
    _title = "Rise of Kingdoms"
    _res = None

    @classmethod
    def find(cls):
        hwnd = win32gui.FindWindow(None, cls._title)
        if hwnd == 0:
            raise RuntimeError("❌ Rise of Kingdoms window not found")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        cls._hwnd = hwnd
        time.sleep(0.5)
        return hwnd

    @classmethod
    def get(cls):
        return cls._hwnd or cls.find()

    @classmethod
    def get_client_size(cls, reload=False):
        if not reload and cls._res:
            return cls._res
        hwnd = cls.get()
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        return (right - left, bottom - top)

    @classmethod
    def is_correct_resolution(cls):
        """
        Check if the ROK window matches the expected resolution.
        Returns:
            bool
        """
        current = cls.get_client_size()
        time.sleep(0.5)
        return current == const.RESOLUTION

    @classmethod
    def focus(cls):
        hwnd = cls.get()
        if hwnd is None:
            raise RuntimeError("Cannot focus: ROK window not found")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
