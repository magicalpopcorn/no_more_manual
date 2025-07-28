import os
import time

import pytesseract
from PIL import Image, ImageOps

from src import logger
from src.element import Button, RectZone

from .screenshot import IMAGES_FOLDER, capture

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(img, lang="eng") -> str:
    """img is Image object or image path"""
    if isinstance(img, str):
        img = Image.open(img)
    text = pytesseract.image_to_string(img, lang=lang).strip()
    return text


def extract_text_from_rect(obj: RectZone | Button, lang="eng", save=False) -> str:
    """obj must be either RectZone or Button"""
    img_obj = capture(obj, save=save)
    text = extract_text(img_obj, lang)
    logger.debug(f"Text extracted from {obj.name}: {repr(text)}")
    return text


def extract_number_from_image(obj: RectZone | Button, crop_ratio=0.025, save=False) -> str:
    img = capture(obj)

    # Get image dimensions and compute crop margins (5% total, 2.5% per side)
    width, height = img.size
    crop_margin_x = int(width * crop_ratio)
    crop_margin_y = int(height * crop_ratio)

    # Crop to 95% center region
    cropped = img.crop(
        (crop_margin_x, crop_margin_y, width - crop_margin_x, height - crop_margin_y)
    )
    if save:
        os.makedirs(IMAGES_FOLDER, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        prefix = obj.name if obj else "fullscreen"
        filename = os.path.join(IMAGES_FOLDER, f"{prefix}_{timestamp}.png")
        logger.debug(f"Saved screenshot: {filename} ")
        cropped.save(filename)

    # Convert to grayscale and resize for better OCR accuracy
    gray = ImageOps.grayscale(cropped)
    resized = gray.resize((gray.width * 2, gray.height * 2))

    # Use pytesseract to extract numbers with commas
    custom_config = r"--psm 6 -c tessedit_char_whitelist=0123456789,"
    text = pytesseract.image_to_string(resized, config=custom_config)

    return text.strip()
