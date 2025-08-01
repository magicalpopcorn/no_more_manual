import io
import os
import time

from ppadb.client import Client as AdbClient
from ppadb.device import Device

from src import logger


class ADBInstance:
    _client = AdbClient(host="127.0.0.1", port=5037)
    _device: Device = None

    @classmethod
    def init_instance(cls, device_index: int):
        """BUG: using device index is wrong, temprarily still working with sole instance
        Use case: start main before farm
        """
        if cls._device is None:
            logger.debug(f"Init ADBInstance with index {device_index}")
            timeout = 30  # seconds
            start_time = time.time()
            while len(cls._client.devices()) < (device_index + 1):
                if time.time() - start_time > timeout:
                    logger.error("Timeout reached, exiting.")
                    raise RuntimeError(f"Failed to init ADBInstance")
                time.sleep(1)
            cls._device = cls._client.devices()[device_index]
        else:
            logger.warning(f"ADBInstance initiated: {cls._device}")

    @classmethod
    def screenshot(cls, image_path=""):
        image_dir = os.path.join(logger.LOG_FOLDER, "adb")
        os.makedirs(image_dir, exist_ok=True)

        timestamp = time.strftime("%H%M%S")
        if not image_path:
            image_path = os.path.join(image_dir, f"screen_{timestamp}.png")
        image_bytes = cls._device.screencap()
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        logger.debug(f"Capture screenshot: {image_path}")
        return image_path

    @classmethod
    def screencap(cls):
        return io.BytesIO(cls._device.screencap())

    @classmethod
    def send_escape(cls):
        """Send Esc"""
        cls._device.shell("input keyevent 4")
        time.sleep(1.5)

    @classmethod
    def shell(cls, cmd):
        cls._device.shell(cmd)

    @classmethod
    def tap(cls, x, y):
        cls.shell(f"input tap {x} {y}")
