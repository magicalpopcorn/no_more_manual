import cv2
import numpy as np
from PIL import Image

from src import const, logger
from src.api import adb
from src.element import CENTER_POINT, Button, P
from src.ui import MenuMain
from src.vision import image


class GatherGem:
    from ultralytics import YOLO

    model = YOLO(const.PROJECT_ROOT / "assests" / "yolo_models" / "2000_17.pt")

    def __init__(self):
        pass

    def gather(self):
        # MenuMain.open_home_resources()
        img = Image.open(adb.screencap()).convert("RGB")
        # Convert to numpy array (OpenCV format)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # YOLO and OpenCV expect BGR

        gem_locations = []  # Will store all bounding boxes
        results = self.model(img)
        # Parse results and draw boxes
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box
                conf = float(box.conf[0])  # Confidence score
                cls_id = int(box.cls[0])  # Class index
                label = self.model.names[cls_id]  # Class label (e.g., 'gem')
                gem_locations.append({"label": label, "confidence": conf, "box": (x1, y1, x2, y2)})
                # Draw box and label
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    img,
                    f"{label} {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
        image.save_image(img, "detected_gems.png")
        if gem_locations:
            first_gem = gem_locations[0]
            x1, y1, x2, y2 = first_gem["box"]
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            logger.debug(
                f"Gem center at ({center_x}, {center_y}) with confidence {first_gem['confidence']:.2f}"
            )
            # Use adb or your macro to click at (center_x, center_y)
            P(center_x, center_y).click()
            CENTER_POINT.click()
            btn_gather = GatherGem.find_gather_button()
            if btn_gather:
                btn_gather.click()
        else:
            logger.debug("No gems detected!")

    @staticmethod
    def find_gather_button(threshold: float = 0.7):
        """
        Find the bounding rectangle of btn_img template in screen_img.
        Returns (x1, y1, x2, y2) if found, else None.
        """
        screen_img = Image.open(adb.screencap()).convert("RGB")
        screen_gray = cv2.cvtColor(np.array(screen_img), cv2.COLOR_BGR2GRAY)
        btn_gray = image.RokImages.BTN_GATHER.as_array()

        result = cv2.matchTemplate(screen_gray, btn_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = btn_gray.shape
            x1, y1 = max_loc
            x2, y2 = x1 + w, y1 + h
            return Button("GATHER", P(x1, y1), P(x2, y2))
        else:
            return None
