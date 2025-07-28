# lib/utils/dpi.py
import ctypes

from src import const


def get_system_dpi_scale():
    """
    Returns the system DPI scaling factor (1.0 = 100%, 1.25 = 125%, etc.).
    """
    hdc = ctypes.windll.user32.GetDC(0)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
    ctypes.windll.user32.ReleaseDC(0, hdc)
    return dpi / 96  # 96 = baseline DPI


class DPIAwareMixin:
    _base_scale = const.BASE_SCALE

    @staticmethod
    def get_ratio():
        return get_system_dpi_scale() / DPIAwareMixin._base_scale

    @property
    def _ratio(self):
        return self.get_ratio()
