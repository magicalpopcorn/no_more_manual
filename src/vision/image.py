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
    left, top = rect.p1._xy
    right, bottom = rect.p2._xy

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


def get_image_from_rect(rect: RectZone | Button, save=False) -> Image:
    img = crop_image_to_rect(rect)
    if save:
        save_image(img, rect.name)
    return img


class TemplateImage:
    IMAGE_DIR = const.PROJECT_ROOT / "src" / "vision" / "images"

    def __init__(self, image_name: Union[str, Path], to_grayscale: bool = True):
        self.path = self.IMAGE_DIR / image_name
        self._to_grayscale = to_grayscale
        self._image = None  # Not loaded yet

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
        return f"TemplateImage(path='{self.path}', shape={self.image.shape})"


class RokImages:
    CASTLE_ICON = TemplateImage("castle_icon.png")
    MAP_ICON = TemplateImage("map_icon.png")
    SWORD_ICON = TemplateImage("sword_of_power.png")
    CROPLAND = TemplateImage("cropland.png")
