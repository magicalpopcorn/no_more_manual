import os
import time

import pytesseract
from PIL import Image, ImageOps

from src import logger
from src.api import adb
from src.element import Button, RectZone

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
IMAGES_FOLDER = logger.LOG_FOLDER / "images"


def extract_text(img, lang="eng") -> str:
    """img is Image object or image path"""
    if isinstance(img, str):
        img = Image.open(img)
    text = pytesseract.image_to_string(img, lang=lang).strip()
    return text


def save_image(img_obj: Image, name):
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(IMAGES_FOLDER, f"{name}_{timestamp}.png")
    logger.debug(f"Saved screenshot: {filename} ")
    img_obj.save(filename)


def _crop_image_to_rect(image_path: str, rect: RectZone | Button, crop_rate: int = 100) -> Image:
    """
    Crop image at image_path to the RectZone,
    and further crop by crop_rate% (centered).

    crop_rate: desired size to capture. E.g 95 (%)
    """
    assert 0 < crop_rate <= 100

    img = Image.open(image_path)
    left, top = rect.p1._xy
    right, bottom = rect.p2._xy

    # Rectangle crop dimensions
    width = right - left
    height = bottom - top

    # Calculate margins for inner crop
    crop_ratio = round((1 - crop_rate / 100) / 2, 3)
    crop_margin_x = int(width * crop_ratio)
    crop_margin_y = int(height * crop_ratio)

    img_obj = img.crop(
        (left + crop_margin_x, top + crop_margin_y, right - crop_margin_x, bottom - crop_margin_y)
    )
    return img_obj


def extract_text_from_rect(rect: RectZone | Button, lang="eng", save=False) -> str:
    """Extract text from RectZone object"""
    img_obj = _crop_image_to_rect(adb.screenshot(), rect)
    if save:
        save_image(img_obj, rect.name)
    text = extract_text(img_obj, lang)
    logger.debug(f"Text extracted from {rect.name}: {repr(text)}")
    return text


def extract_number_from_rect(rect: RectZone | Button, crop_rate=95, save=False) -> str:
    """Extract number from RectZone object

    crop_rate: desired size to capture. E.g 95 (%)
    """
    assert 0 < crop_rate < 100

    img_obj = _crop_image_to_rect(adb.screenshot(), rect, crop_rate)

    if save:
        save_image(img_obj, rect.name)

    # Convert to grayscale and resize for better OCR accuracy
    gray = ImageOps.grayscale(img_obj)
    resized = gray.resize((gray.width * 2, gray.height * 2))

    # Use pytesseract to extract numbers with commas
    custom_config = r"--psm 6 -c tessedit_char_whitelist=0123456789,"
    text = pytesseract.image_to_string(resized, config=custom_config)

    return text.strip()
