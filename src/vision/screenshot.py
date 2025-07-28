import os
import time

import mss
import win32gui
from PIL import Image

from src import logger
from src.element import RectZone
from src.window import ROKWindow

IMAGES_FOLDER = logger.LOG_FOLDER / "images"


def capture(rect: RectZone = None, save=False) -> Image:
    """
    Captures a screenshot of the RoK Client area using Client coordinates.

    Args:
        rect (RectZone): Optional (x1, y1, x2, y2) in Client coordinates to crop.
                      If None, captures the full Client area.
    Returns:
        Image: Screenshot image.
    """
    try:
        hwnd = ROKWindow.get()

        # Get client top-left in screen coordinates
        client_left, client_top = win32gui.ClientToScreen(hwnd, (0, 0))
        client_width, client_height = ROKWindow.get_client_size()

        if rect is None:
            region = {
                "left": client_left,
                "top": client_top,
                "width": client_width,
                "height": client_height,
            }
        else:
            x1, y1, x2, y2 = rect.to_tuple()
            region = {
                "left": client_left + x1,
                "top": client_top + y1,
                "width": x2 - x1,
                "height": y2 - y1,
            }

        with mss.mss() as sct:
            img = sct.grab(region)
        pil_img = Image.frombytes("RGB", img.size, img.rgb)

        if save:
            os.makedirs(IMAGES_FOLDER, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            prefix = rect.name if rect else "fullscreen"
            filename = os.path.join(IMAGES_FOLDER, f"{prefix}_{timestamp}.png")
            logger.debug(f"Saved screenshot: {filename} ")
            pil_img.save(filename)

        return pil_img

    except Exception as e:
        raise RuntimeError(f"Failed to capture Client screenshot: {e}")


def capture_fullscreen():
    return capture(None, save=True)
