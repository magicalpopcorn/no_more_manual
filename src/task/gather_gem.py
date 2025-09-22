import random
import threading
import time
from dataclasses import dataclass
from pprint import pformat

import cv2
import numpy as np
from PIL import Image

from src import const, logger, utils
from src.action import Switch
from src.action.reload import reload_game
from src.api import adb
from src.element import CENTER_POINT, Button, Direction, P, RectZone
from src.ui import (
    MenuCity,
    MenuDispatch,
    MenuHomeResources,
    MenuMain,
    MenuNetWorkDisconnect,
    MenuNotice,
    MenuProfile,
    MenuQueue,
)
from src.ui.sub_menu import MenuItems, MenuStatistics
from src.vision import cv, image, ocr, yolo
from src.vision.yolo import YoloClass


@dataclass
class DetectedObject:
    label: str
    confidence: float
    btn: Button


class GatherConfig:
    SESSION_DURATION = (3600, 5400)  # 60-90 min sessions
    SESSION_BREAK = (300, 600)  # 5-10 min breaks
    MAX_CONSECUTIVE_ERRORS = 3

    # roulette
    RANDOM_EVENT_CHANCE = 0.75  # 75%

    PREPARE_CHANCE = 0.15  # 15%
    CLICKHOME_CHANCE = 0.1  # 10%
    OPENPROFILE_CHANCE = 0.1  # 10%
    OPENITEMS_CHANCE = 0.1  # 10%
    OPENSTATISTICS_CHANCE = 0.1  # 10%


class GatherGem:

    model = yolo.YOLO_MODEL

    def __init__(self):
        self.avail_marches = []
        self.char_id = "main"  # Default character ID

    def execute(self, char_id: str):
        """Main execution loop with anti-detection measures"""
        Switch().switch_character(char_id)
        self.char_id = char_id

        consecutive_errors = 0
        max_consecutive_errors = GatherConfig.MAX_CONSECUTIVE_ERRORS
        session_start = time.time()

        while True:
            try:
                # Add session-based breaks (like a human would take breaks)
                session_duration = time.time() - session_start
                if session_duration > random.uniform(*GatherConfig.SESSION_DURATION):
                    self._take_extended_break()
                    session_start = time.time()

                # Human-like preparation with occasional mistakes
                self._prepare_with_human_behavior()

                # Get available marches with variance
                self.get_avail_marches()
                self.scout_n_gather()

                # Execute random events during sleep time using threading
                self._execute_with_random_events()
                consecutive_errors = 0  # Reset on success

            except KeyboardInterrupt:
                logger.info("Manual stop requested")
                break
            except Exception as e:
                if not MenuNetWorkDisconnect.is_open():
                    consecutive_errors += 1
                    logger.error(f"Error occurred (attempt {consecutive_errors}): {e}")

                    if consecutive_errors > max_consecutive_errors:
                        logger.error("Too many consecutive errors, taking extended break")
                        raise RuntimeError("Too many consecutive errors")

                    # Add human-like delay before retrying
                    error_delay = random.uniform(10, 30)
                    logger.info(f"Waiting {error_delay:.1f}s before retry...")
                    utils.sleep_random(int(error_delay), int(error_delay) + 5)
                else:
                    logger.error("Network disconnect detected, reloading game")
                reload_game()

    def prepare(self):
        MenuCity.open()
        unused_m = MenuMain.get_unused_march_on_screen()
        if unused_m != 0:
            logger.info("There are unused marches available")
            MenuMain.open_map_screen()

            click_zones = [
                Button(
                    "left_empty_area",
                    P(255, 240),
                    P(767, 850),
                ),
                Button(
                    "right_empty_area",
                    P(1145, 240),
                    P(1700, 850),
                ),
            ]
            btn_march = None
            while not btn_march:
                for btn in click_zones:
                    btn.click()
                    btn_march, score = cv.find_template_in_image(
                        image.fullscreen_cap(), image.RokImages.BTN_MARCH, threshold=0.6
                    )
                    if btn_march:
                        break
                utils.sleep_random(1, 1.5)

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
        flag_returning = False
        for march in self.avail_marches:
            if march.label == YoloClass.MARCH_RETURNING:
                flag_returning = True
                march.btn.shift(-15, -15).click(delay=1.5)
                MenuMain.BTN_TROOP_STOP.click(delay=1)
        if not flag_returning and random.random() < 0.5:  # 50%
            self.avail_marches[-1].btn.shift(-15, -15).click(delay=1.5)

    def scout_n_gather(self):
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
        directions = self.spiral_directions(50)

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
                    utils.sleep_random(2, 4)
                    if MenuNotice.is_open():
                        logger.info("Notice is open, clicking NO")
                        MenuNotice.BTN_NOTICE_NO.click(verify=lambda: not MenuNotice.is_open())
                        self.avail_marches.append(march)
                        break
                else:
                    return
            if not self.avail_marches:
                return
            next_direction = next(directions)
            if next_direction is None:
                logger.info("No more directions, restarting spiral")
                MenuCity.open()
                utils.sleep_random(3, 5)
                directions = self.spiral_directions(50)
            MenuHomeResources.open()
            MenuHomeResources.swipe_screen(Direction(next_direction))
            utils.sleep_random(2.0, 3.5)

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
                logger.debug(f"Detected {label} with confidence {conf:.2f}")
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
    def spiral_directions(limit: int = 50):
        """
        Generate a spiral pattern of directions for resource exploration.
        Returns a sequence of 'U', 'R', 'D', 'L' directions in a spiral pattern.

        Args:
            limit: Maximum number of directions to yield
        """
        dir_map = ["U", "R", "D", "L"]
        valid_pairs = [("U", "R"), ("R", "D"), ("D", "L"), ("L", "U")]

        # Select random starting pair
        start_pair = random.choice(valid_pairs)
        start_idx = dir_map.index(start_pair[0])
        next_idx = dir_map.index(start_pair[1])
        offset = (next_idx - start_idx) % 4

        # Define spiral direction sequence based on initial pair
        spiral_dirs = [dir_map[(start_idx + i * offset) % 4] for i in range(4)]

        count = 0
        step_len = 1
        dir_idx = 0

        while count < limit:
            for _ in range(2):
                current_dir = spiral_dirs[dir_idx % 4]
                for _ in range(step_len):
                    count += 1
                    logger.debug(f"counter: {count}")
                    yield current_dir
                    if count >= limit:
                        return
                dir_idx += 1
            step_len += 1

    def _take_extended_break(self):
        """Simulate human taking a break - go to safe location and idle"""
        logger.info("Taking extended break (like a human would)")
        break_duration = random.uniform(*GatherConfig.SESSION_BREAK)

        # Go to safe location (city view)
        try:
            MenuCity.open()
            logger.info(f"Extended break: {break_duration:.1f}s")
            utils.sleep_random(int(break_duration), int(break_duration) + 60)
        except Exception as e:
            logger.warning(f"Error during extended break: {e}")
            utils.sleep_random(*GatherConfig.SESSION_BREAK)

    def _prepare_with_human_behavior(self):
        """Enhanced prepare method with human-like behavior"""
        try:
            # Sometimes check different screens first (like a human might)
            if random.random() < GatherConfig.PREPARE_CHANCE:
                MenuMain.BTN_HOME.click()
                with MenuProfile():
                    utils.sleep_random(2, 5)
        except Exception as e:
            logger.warning(f"Error in human behavior preparation: {e}")
        finally:
            # Normal preparation
            self.prepare()

            # Sometimes take a small pause (thinking/checking phone)
            if random.random() < GatherConfig.PREPARE_CHANCE:
                pause_time = random.uniform(2, 8)
                logger.debug(f"Taking thinking pause: {pause_time:.1f}s")
                utils.sleep_random(int(pause_time), int(pause_time) + 2)

    def random_event(self):
        """Simulate random events like a human might do"""
        try:
            MenuCity.open()
            if self.russian_roulette("Click HOME", GatherConfig.CLICKHOME_CHANCE):
                MenuMain.BTN_HOME.click()
            if self.russian_roulette("Open Profile Menu", GatherConfig.OPENPROFILE_CHANCE):
                with MenuProfile():
                    utils.sleep_random(4, 5)
            elif self.russian_roulette("Open Items Menu", GatherConfig.OPENITEMS_CHANCE):
                with MenuItems(self.char_id):
                    utils.sleep_random(4, 5)
                    if self.russian_roulette(
                        "Open Statistics Menu", GatherConfig.OPENSTATISTICS_CHANCE
                    ):
                        with MenuStatistics(self.char_id):
                            utils.sleep_random(5, 6)
        except Exception as e:
            logger.warning(f"Error in random_event: {e}")

    def _execute_with_random_events(self):
        """Execute random events during sleep time using threading"""
        # Calculate sleep duration
        sleep_duration = random.uniform(60, 90)
        logger.debug(f"Sleeping for {sleep_duration:.1f}s with random events")

        # Decide if we should have a random event during this sleep
        if self.russian_roulette("random_event", GatherConfig.RANDOM_EVENT_CHANCE):
            # Schedule when the event should happen during sleep
            event_delay = random.uniform(
                10, sleep_duration - 10
            )  # Event between 10s and sleep_duration-10s
            logger.debug(f"Random event scheduled in {event_delay:.1f}s during sleep")

            # Sleep until event time
            utils.sleep_random(event_delay, event_delay + 0.1)

            # Start the random event thread and track timing
            event_start_time = time.time()
            logger.debug("Starting random event thread")
            event_thread = threading.Thread(target=self.random_event, daemon=True)
            event_thread.start()

            # Calculate remaining sleep time after event starts
            remaining_sleep = sleep_duration - event_delay
            logger.debug(f"Remaining sleep time: {remaining_sleep:.1f}s")

            # Sleep for the remaining time or until event completes, whichever is longer
            if remaining_sleep > 0:
                utils.sleep_random(remaining_sleep, remaining_sleep + 0.1)

            # Check if event is still running after our sleep time
            if event_thread.is_alive():
                event_elapsed = time.time() - event_start_time
                logger.debug(
                    f"Event still running after {event_elapsed:.1f}s, waiting for completion"
                )
                event_thread.join()  # Wait for event to complete
                total_event_time = time.time() - event_start_time
                logger.debug(f"Event completed after {total_event_time:.1f}s total")
            else:
                logger.debug("Random event completed within sleep duration")

        else:
            # No random event, just sleep for the full duration
            logger.debug("No random event scheduled, sleeping full duration")
            utils.sleep_random(sleep_duration, sleep_duration + 0.1)

        logger.debug("Sleep with random events completed")

    @staticmethod
    def russian_roulette(event_name: str, chance: float):
        """Simulate a Russian roulette event"""
        roulette = random.random()
        logger.debug(f"Event {event_name} [{chance*100}%], roulette [{roulette*100:.2f}%]")
        return roulette < chance
