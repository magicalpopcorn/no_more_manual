import random
import time
from dataclasses import dataclass
from pprint import pformat

import cv2
import numpy as np
from PIL import Image

from src import const, logger
from src.action import Switch
from src.action.reload import reload_game
from src.api import adb
from src.element import CENTER_POINT, Button, Direction, P, RectZone
from src.ui import MenuCity, MenuDispatch, MenuHomeResources, MenuMain, MenuQueue
from src.vision import cv, image, yolo
from src.vision.yolo import YoloClass


@dataclass
class DetectedObject:
    label: str
    confidence: float
    btn: Button


class GatherGem:

    model = yolo.YOLO_MODEL

    def __init__(self):
        self.avail_marches = []

    def execute(self, char_id: str):
        Switch().switch_character(char_id)

        while True:
            try:
                self.prepare()
                self.get_avail_marches()
                self.gather()
                logger.debug("Wait for next 60s ...")
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error occurred: {e}")
                reload_game()

    def prepare(self):
        MenuCity.open()
        unused_m = MenuMain.get_unused_march_on_screen()
        if unused_m != 0:
            logger.info("There are unused marches available")
            MenuMain.open_map_screen()
            # FIXME: known issue, if the right point is not a empty point (no marches, resources, barbs, etc ...)
            # it would be a mess
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
            # Add timeout of 10 seconds
            start_time = time.time()
            while MenuMain.get_unused_march_on_screen() != 0:
                if time.time() - start_time > 10:
                    logger.warning("Timed out waiting for marches to be deployed")
                    break
                time.sleep(1)

    def get_avail_marches(self):
        img = Image.open(adb.screencap()).convert("RGB")
        # Convert to numpy array (OpenCV format)
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # YOLO and OpenCV expect BGR

        self.avail_marches = self.get_object_locations(
            img, (YoloClass.MARCH_IDLE, YoloClass.MARCH_RETURNING), draw_box=False
        )
        logger.debug(
            f"Found {len(self.avail_marches)} available marches\n{pformat(self.avail_marches)}"
        )
        if not self.avail_marches:
            return
        for march in self.avail_marches:
            if march.label == YoloClass.MARCH_RETURNING:
                march.btn.shift(-15, -15).click()
                MenuMain.BTN_TROOP_STOP.click()
        self.avail_marches[-1].btn.shift(-15, -15).click()

    def gather(self):
        # step 1: check avail marches in menu main - DONE
        # step 2: if not 5/5, march all - DONE
        # step 3: march is 5/5, detect idle & returning marches
        # step 4: open home resources
        # step 5: detect gems in home resources
        # step 6: for each idle march, drag to gem location until no more idle marches
        # step 7: sleep for 5 minutes and repeat
        if not self.avail_marches:
            return

        logger.info("Gathering gems...")
        MenuHomeResources.open()
        directions = self.spiral_directions()

        while True:
            img = np.array(image.fullscreen_cap().convert("RGB"))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # YOLO and OpenCV expect BGR

            gems = self.get_object_locations(img, yolo.YoloClass.GEM)
            if not gems:
                logger.debug("No gems detected!")

            for gem in gems:
                logger.debug(f"Detected gem at {gem.btn}")
                if self.avail_marches:
                    march = self.avail_marches.pop()
                    print(f"Marching {march.btn.name} to gem at {gem.btn.name}")
                    march.btn.shift(-15, -15).swipe(gem.btn)
                    time.sleep(2)
                else:
                    return
            if not self.avail_marches:
                return
            MenuHomeResources.swipe_screen(Direction(next(directions)))
            time.sleep(1.5)

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
                conf = float(box.conf[0])  # Confidence score
                if label not in target_label or conf < 0.4:
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box
                # Check if the deposite is gathered by me
                if label == YoloClass.GEM:
                    checkzone = RectZone(
                        "gather_icon_zone", P(x1 + 10, y1 - 50), P(x1 + 50, y1 - 20)
                    )
                    threshold = 0.5
                    img_checkzone = image.crop_image_to_rect(checkzone)
                    btn, score = cv.find_template_in_image(
                        img_checkzone, image.RokImages.GATHER_ICON, threshold
                    )
                    if btn:
                        logger.debug(f"Found gather icon in {checkzone} {score:.2f}. Skip this")
                        continue

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
        if draw_box and locations:
            image.save_image(img, f"detect_{"_".join(map(str, target_label))}.png")
        return locations

    @staticmethod
    def spiral_directions():
        dir_map = ["U", "R", "D", "L"]
        valid_pairs = [("U", "R"), ("R", "D"), ("D", "L"), ("L", "U")]

        # Chọn tổ hợp khởi đầu ngẫu nhiên
        start_pair = random.choice(valid_pairs)
        start_idx = dir_map.index(start_pair[0])
        next_idx = dir_map.index(start_pair[1])
        offset = (next_idx - start_idx) % 4

        # Xác định chuỗi hướng spiral từ tổ hợp ban đầu
        spiral_dirs = [dir_map[(start_idx + i * offset) % 4] for i in range(4)]

        step_len = 1
        dir_idx = 0
        while True:
            for _ in range(2):
                current_dir = spiral_dirs[dir_idx % 4]
                for _ in range(step_len):
                    yield current_dir
                dir_idx += 1
            step_len += 1
