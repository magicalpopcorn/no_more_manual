import os

import cv2
import numpy as np
from PIL import Image

from src import logger
from src.element import Button, P, RectZone

from .image import TemplateImage, get_image_from_rect


def match_region_with_template(
    rect: RectZone,
    template_img: np.ndarray | TemplateImage,
    threshold: float = 0.9,
    verbose: bool = False,
    save: bool = False,
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
    img_obj = get_image_from_rect(rect, save=save)
    region_np = np.array(img_obj)
    region_np = cv2.cvtColor(region_np, cv2.COLOR_RGB2GRAY)  # Always grayscale here

    if isinstance(template_img, TemplateImage):
        template_img = template_img.as_array()

    result = cv2.matchTemplate(region_np, template_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    if verbose:
        logger.debug(f"[match] Match score: {max_val:.4f}")

    return max_val >= threshold


def find_template_in_image(
    large_image: Image.Image | TemplateImage | np.ndarray,
    template_img: TemplateImage,
    threshold: float = 0.8,
    use_edges: bool = True,
    method: int = cv2.TM_CCOEFF_NORMED,
) -> tuple[Button, float] | tuple[None, float]:
    """
    Search for template in large image using matchTemplate.

    Returns:
        Button if match is found above threshold.
        None if no good match found.
    """
    # Load images
    if isinstance(large_image, TemplateImage):
        gray_large = large_image.as_array()
    elif isinstance(large_image, Image.Image):
        large_img = np.array(large_image)
        gray_large = cv2.cvtColor(large_img, cv2.COLOR_BGR2GRAY)
    elif isinstance(large_image, np.ndarray):
        gray_large = cv2.cvtColor(large_image, cv2.COLOR_BGR2GRAY)

    # Convert to grayscale
    gray_template = template_img.as_array()

    # Optionally apply edge detection
    if use_edges:
        gray_large = cv2.Canny(gray_large, 50, 150)
        gray_template = cv2.Canny(gray_template, 50, 150)

    # Perform template matching
    result = cv2.matchTemplate(gray_large, gray_template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Choose correct match value based on method
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        match_val = min_val
        match_loc = min_loc
        passed = match_val <= (1.0 - threshold)  # lower is better
    else:
        match_val = max_val
        match_loc = max_loc
        passed = match_val >= threshold  # higher is better

    if passed:
        x1, y1 = match_loc
        h, w = template_img.as_array().shape[:2]
        x2, y2 = x1 + w, y1 + h
        return Button(f"{os.path.basename(template_img.path)}", P(x1, y1), P(x2, y2)), match_val

    return None, match_val
