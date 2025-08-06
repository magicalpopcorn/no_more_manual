import os
import time
from pathlib import Path
from typing import Union

import cv2
import numpy as np
from PIL import Image

from src import const, logger
from src.api import adb
from src.element import Button, RectZone

IMAGES_FOLDER = logger.LOG_FOLDER / "images"


def save_image(img_obj: Image, name):
    os.makedirs(IMAGES_FOLDER, exist_ok=True)

    timestamp = time.strftime("%H%M%S")
    filename = os.path.join(IMAGES_FOLDER, f"{name}_{timestamp}.png")
    logger.debug(f"Saved screenshot: {filename} ")
    img_obj.save(filename)


def crop_image_to_rect(rect: RectZone | Button, crop_rate: int = 100) -> Image:
    """
    Crop image at image_path to the RectZone,
    and further crop by crop_rate% (centered).

    crop_rate: desired size to capture. E.g 95 (%)
    """
    assert 0 < crop_rate <= 100

    fullscreen = Image.open(adb.screencap())
    left, top = rect.p1.xy
    right, bottom = rect.p2.xy

    # Rectangle crop dimensions
    width = right - left
    height = bottom - top

    # Calculate margins for inner crop
    crop_ratio = round((1 - crop_rate / 100) / 2, 3)
    crop_margin_x = int(width * crop_ratio)
    crop_margin_y = int(height * crop_ratio)

    img_obj = fullscreen.crop(
        (
            left + crop_margin_x,
            top + crop_margin_y,
            right - crop_margin_x,
            bottom - crop_margin_y,
        )
    )

    return img_obj


def screenshot(name="screen"):
    fullscreen = Image.open(adb.screencap())
    save_image(fullscreen, name)


def get_image_from_rect(rect: RectZone | Button, crop_rate=100, save=False) -> Image:
    img = crop_image_to_rect(rect, crop_rate)
    if save:
        save_image(img, rect.name)
    return img


class TemplateImage:
    IMAGE_DIR = const.PROJECT_ROOT / "src" / "vision" / "images"

    def __init__(self, image_name: Union[str, Path], to_grayscale: bool = True):
        self.path = self.IMAGE_DIR / image_name
        self._to_grayscale = to_grayscale
        self._image = None  # Not loaded yet

        if not os.path.exists(self.path):
            raise FileNotFoundError(f"image {image_name} not found")

    def as_array(self) -> np.ndarray:
        """Returns the image as a NumPy array. Loads it if not already loaded."""
        if self._image is None:
            self._image = cv2.imread(str(self.path))
            if self._image is None:
                raise FileNotFoundError(f"Template not found: {self.path}")
            if self._to_grayscale:
                self._image = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)
        return self._image

    def __repr__(self):
        return f"TemplateImage(path='{self.path}', shape={self._image.shape})"


class RokImages:
    # Sub folders
    _DISPATCH = Path("dispatch")

    # Menu Main
    CASTLE_ICON = TemplateImage("castle_icon.png")
    MAP_ICON = TemplateImage("map_icon.png")
    SWORD_ICON = TemplateImage("sword_of_power.png")

    # Menu Search
    CROPLAND = TemplateImage("cropland.png")

    # Menu Main - Expanded
    BTN_ITEMS = TemplateImage("btn_items.png")

    # Menu Items
    BTN_ITEMS_RESOURCES = TemplateImage("btn_items_resources.png")
    BTN_ITEMS_BOOSTS = TemplateImage("btn_items_boosts.png")

    # Menu Dispatch
    RECT_DISPATCH_TITLE = TemplateImage("dispatch_title.png")

    # Menu City
    BTN_COURIER_STATION = TemplateImage("Courier_Station.png")
    BTN_COURIER_MERCHANT = TemplateImage("Courier_Merchant.png")

    # Menu Merchant
    BTN_REFRESH = TemplateImage("free_refresh.png")

    # Menu Dispatch
    BTN_MULTI_CHECKED = TemplateImage(_DISPATCH / "btn_multi_checked.png")
    BTN_M1_CHECKED = TemplateImage(_DISPATCH / "m1_checked.png")
    BTN_M2_CHECKED = TemplateImage(_DISPATCH / "m2_checked.png")
    BTN_M3_CHECKED = TemplateImage(_DISPATCH / "m3_checked.png")
    BTN_M4_CHECKED = TemplateImage(_DISPATCH / "m4_checked.png")
    BTN_M5_CHECKED = TemplateImage(_DISPATCH / "m5_checked.png")

    @staticmethod
    def get_march_image(march_number: int) -> TemplateImage:
        march_images = {
            1: RokImages.BTN_M1_CHECKED,
            2: RokImages.BTN_M2_CHECKED,
            3: RokImages.BTN_M3_CHECKED,
            4: RokImages.BTN_M4_CHECKED,
            5: RokImages.BTN_M5_CHECKED,
        }
        return march_images.get(march_number)
