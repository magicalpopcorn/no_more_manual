import cv2
import numpy as np

from src import logger
from src.element import RectZone

from .image import TemplateImage, get_image_from_rect


def match_region_with_template(
    rect: RectZone,
    template_img: np.ndarray | TemplateImage,
    threshold: float = 0.9,
    verbose: bool = False,
) -> bool:
    """
    Match a region of the screen with a preloaded template image (np.array).

    Args:
        rect: (x, y, w, h) region.
        template_img: Preprocessed template as np.ndarray.
        threshold: Confidence threshold.
        verbose: Show match score.

    Returns:
        True if match exceeds threshold, False otherwise.
    """
    img_obj = get_image_from_rect(rect)
    region_np = np.array(img_obj)
    region_np = cv2.cvtColor(region_np, cv2.COLOR_RGB2GRAY)  # Always grayscale here

    if isinstance(template_img, TemplateImage):
        template_img = template_img.as_array()

    result = cv2.matchTemplate(region_np, template_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    if verbose:
        logger.debug(f"[match] Match score: {max_val:.4f}")

    return max_val >= threshold
