import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from src import logger
from src.element import Button, RectZone

from .image import crop_image_to_rect, get_image_from_rect, save_image

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text(img, lang="eng", psm=6, whitelist="") -> str:
    """img is Image object or image path
    psm = 6 - multiple lines - default
    psm = 7 - single line
    """
    if isinstance(img, str):
        img = Image.open(img)
    img = img.convert("L")
    img = img.resize((img.width * 2, img.height * 2))
    img = img.filter(ImageFilter.SHARPEN)
    # img = ImageEnhance.Contrast(img).enhance(2.0)
    config = f"--psm {psm}"
    if whitelist:
        config += f" -c tessedit_char_whitelist={whitelist}"
    text = pytesseract.image_to_string(img, lang=lang, config=config).strip()
    return text


def extract_text_from_rect(rect: RectZone | Button, lang="eng", whitelist="", save=False) -> str:
    """Extract single line of text from RectZone object"""
    img_obj = get_image_from_rect(rect, save=save)
    text = extract_text(img_obj, lang, psm=7, whitelist=whitelist)
    logger.debug(f"Text extracted from {rect.name}: {repr(text)}")
    return text.strip()


def extract_multi_text_from_rect(
    rect: RectZone | Button, lang="eng", whitelist="", save=False
) -> str:
    """Extract multiple lines of text from RectZone object"""
    img_obj = get_image_from_rect(rect, save=save)
    text = extract_text(img_obj, lang, psm=6, whitelist=whitelist)
    res = [s for s in text.splitlines() if s]
    logger.debug(f"Text extracted from {rect.name}: {res}")
    return res


def extract_number_from_rect(rect: RectZone | Button, crop_rate=95, save=False) -> str:
    """Extract number from RectZone object

    crop_rate: desired size to capture. E.g 95 (%)
    """
    img_obj = get_image_from_rect(rect, crop_rate=crop_rate, save=save)
    text = extract_text(img_obj, psm=6, whitelist=r"0123456789,")
    return text.strip()
