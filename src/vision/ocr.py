import pytesseract
from PIL import Image, ImageFilter, ImageOps

from src import logger
from src.element import Button, RectZone

from .image import crop_image_to_rect, get_image_from_rect, save_image

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(img, lang="eng", psm=6) -> str:
    """img is Image object or image path
    psm = 6 - multiple lines - default
    psm = 7 - single line
    """
    if isinstance(img, str):
        img = Image.open(img)
    img = img.convert("L")
    img = img.resize((img.width * 2, img.height * 2))
    img = img.filter(ImageFilter.SHARPEN)
    config = f"--psm {psm}"
    text = pytesseract.image_to_string(img, lang=lang, config=config).strip()
    return text


def extract_text_from_rect(rect: RectZone | Button, lang="eng", save=False) -> str:
    """Extract single line of text from RectZone object"""
    img_obj = get_image_from_rect(rect, save)
    text = extract_text(img_obj, lang, psm=7)
    logger.debug(f"Text extracted from {rect.name}: {repr(text)}")
    return text


def extract_multi_text_from_rect(rect: RectZone | Button, lang="eng", save=False) -> str:
    """Extract multiple lines of text from RectZone object"""
    img_obj = get_image_from_rect(rect)
    text = extract_text(img_obj, lang, psm=6)
    res = text.splitlines()
    logger.debug(f"Text extracted from {rect.name}: {res}")
    return res


def extract_number_from_rect(rect: RectZone | Button, crop_rate=95, save=False) -> str:
    """Extract number from RectZone object

    crop_rate: desired size to capture. E.g 95 (%)
    """
    assert 0 < crop_rate < 100

    img_obj = crop_image_to_rect(rect, crop_rate)

    if save:
        save_image(img_obj, rect.name)

    # Convert to grayscale and resize for better OCR accuracy
    gray = ImageOps.grayscale(img_obj)
    resized = gray.resize((gray.width * 2, gray.height * 2))

    # Use pytesseract to extract numbers with commas
    custom_config = r"--psm 6 -c tessedit_char_whitelist=0123456789,"
    text = pytesseract.image_to_string(resized, config=custom_config)

    return text.strip()
