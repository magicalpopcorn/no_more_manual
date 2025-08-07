import time
from dataclasses import dataclass
from pprint import pformat

import cv2
import numpy as np
from PIL import Image

from src import const, logger
from src.api import adb
from src.element import CENTER_POINT, Button, P
from src.ui import MenuDispatch, MenuHomeResources, MenuMain, MenuQueue
from src.vision import cv, image, ocr, yolo
from src.vision.yolo import YoloClass

from .gather import Gather


@dataclass
class DetectedObject:
    label: str
    confidence: float
    btn: Button


class GatherGem:

    model = yolo.YOLO_MODEL

    def __init__(self):
        self.avail_marches = []

    def prepare(self):
        avail_m = MenuMain.get_avail_march_on_screen()
        if avail_m != 0:
            logger.info("There are marches available")
            MenuMain.open_map_screen()
            right_point = P(CENTER_POINT.p2.x + 100, CENTER_POINT.p1.y + 200)
            right_point.click()
            btn_march = Button(
                "March",
                P(right_point.x - 460, right_point.y + 35),
                P(right_point.x - 170, right_point.y + 130),
            )
            btn_march.click(verify=MenuQueue.is_new_troop_btn_visible)
            MenuQueue.BTN_NEW_TROOP.click(verify=MenuDispatch.is_open)
            MenuDispatch.dispatch_all()

    def get_avail_marches(self):
        img = Image.open(adb.screencap()).convert("RGB")
        # Convert to numpy array (OpenCV format)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # YOLO and OpenCV expect BGR

        self.avail_marches = self.get_object_locations(
            img, (YoloClass.MARCH_IDLE, YoloClass.MARCH_RETURNING)
        )
        logger.debug(
            f"Found {len(self.avail_marches)} available marches\n{pformat(self.avail_marches)}"
        )
        for march in self.avail_marches:
            if march.label == YoloClass.MARCH_RETURNING:
                march.btn.shift(-15, -15).click()
                MenuMain.BTN_TROOP_STOP.click()

    def gather(self):
        # step 1: check avail marches in menu main - DONE
        # step 2: if not 5/5, march all - DONE
        # step 3: march is 5/5, detect idle marches
        # step 4: open home resources
        # step 5: detect gems in home resources
        # step 6: for each idle march, drag to gem location until no more idle marches
        # step 7: sleep for 5 minutes and repeat

        MenuHomeResources.open()
        img = np.array(image.fullscreen_cap().convert("RGB"))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # YOLO and OpenCV expect BGR

        gems = self.get_object_locations(img, yolo.YoloClass.GEM)
        if not gems:
            logger.debug("No gems detected!")
            return

        for gem in gems:
            logger.debug(f"Detected gem at {gem.btn} with confidence {gem.confidence:.2f}")
            march = self.avail_marches.pop()
            print(f"Marching {march.btn.name} to gem at {gem.btn.name}")
            march.btn.shift(-15, -15).swipe(gem.btn, duration=1000)
            time.sleep(1)

    def get_object_locations(
        self, img, target_label: str | tuple, draw_box=True
    ) -> list[DetectedObject]:
        locations = []  # Will store all bounding boxes
        if isinstance(target_label, str):
            target_label = (target_label,)
        # Parse results and draw boxes
        for result in GatherGem.model(img):
            for box in result.boxes:
                cls_id = int(box.cls[0])  # Class index
                label = GatherGem.model.names[cls_id]  # Class label (e.g., 'gem')
                if label not in target_label:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box
                conf = float(box.conf[0])  # Confidence score

                locations.append(
                    DetectedObject(
                        label=label,
                        confidence=conf,
                        btn=Button(f"{label}_{conf:.2f}", P(x1, y1), P(x2, y2)),
                    )
                )
                # Draw box and label
                if draw_box:
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
        return locations
