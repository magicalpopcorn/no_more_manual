import io
import json
import os
import subprocess
import time
from typing import Optional

from ppadb.client import Client as AdbClient
from ppadb.device import Device

from src.lib import logger, utils
from src.lib.const import DATA_DIR

from .ldp_api import LDInstance

MAPPING_FILE = DATA_DIR / "adb_ldp_mapping.json"


def refresh_adb_server(brutal: bool = False):
    """Refresh ADB server to ensure it is running and connected to the device."""
    logger.info("Refreshing ADB server...")
    if brutal:
        logger.info("Brutal mode: stopping ADB server")
        subprocess.call("adb kill-server")
    else:
        logger.info("Normal mode: restarting ADB server")
    subprocess.check_call("adb start-server")
    # subprocess.check_call("adb disconnect")
    time.sleep(5)
    logger.info("ADB server refreshed.")


class ADBInstance:
    _client = AdbClient(host="127.0.0.1", port=5037)
    _device: Optional[Device] = None
    _pre_running_devices: set = set()

    @classmethod
    def collect_pre_running_devices(cls):
        """Collect the pre-running devices for the ADB instance."""
        cls._pre_running_devices = cls.get_running_devices()

    @classmethod
    def get_running_devices(cls):
        """Get the currently running devices."""
        return {device.serial for device in cls._client.devices()}

    @classmethod
    def init_instance(cls, instance_name):
        """Initialize the ADBInstance with the given instance name.

        Raise: ConnectionError
        """

        def get_device(device_serial):
            """Get the device by its serial number."""
            for device in cls._client.devices():
                if device.serial == device_serial:
                    return device

        def save_mapping(instance_name):
            """Save the mapping of instance name to device serial."""
            if cls._device is None:
                logger.error("ADB device is not initialized")
                return
            with open(MAPPING_FILE, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data[instance_name] = cls._device.serial
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        if cls._device:
            logger.warning(f"ADBInstance already initiated: {cls._device}")
            return

        logger.debug(f"Init ADBInstance with LDPInstance {instance_name}")
        logger.debug(f"_pre_running_devices: {cls._pre_running_devices}")

        if instance_name in LDInstance.get_pre_running_instances():
            # In case instance already started, but just get the instance
            logger.debug("Instance already initiated")
            with open(MAPPING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            device_serial = data[instance_name]
            cls._device = get_device(device_serial)
        else:
            logger.debug("Fresh ADB initialization. Wait for device up")

            # At this point ldpinstance should be already started
            # wait for new element in cls._client.devices()
            timeout = 30  # seconds
            start_time = time.time()
            while len(cls._client.devices()) == len(cls._pre_running_devices):
                if time.time() - start_time > timeout:
                    raise TimeoutError("Timeout: No new device appeared within the given time.")
                logger.warning(f"Device not ready, wait for 5s ... {cls.get_running_devices()}")
                time.sleep(5)

            # 'adb devices' should have a new device
            devices = cls.get_running_devices()
            logger.debug(f"Device ready: {devices}")
            device_serial = devices - cls._pre_running_devices
            if len(device_serial) != 1:
                raise ConnectionError(
                    f"There should be exactly one device: {device_serial}. Recheck pls"
                )

            device_serial = device_serial.pop()
            logger.info(f"Desired device to connect {device_serial}")
            cls._device = get_device(device_serial)
            save_mapping(instance_name)

        if cls._device is None:
            raise ConnectionError(f"Device with serial {device_serial} not found")
        logger.info(f"Connected adb {cls._device.serial} with instance {instance_name}")

    @classmethod
    def screenshot(cls, image_path=""):
        assert cls._device is not None

        image_dir = os.path.join(logger.LOG_FOLDER, "adb")
        os.makedirs(image_dir, exist_ok=True)

        if not image_path:
            image_path = os.path.join(image_dir, f"screen_{time.strftime('%H%M%S')}.png")
        image_bytes = cls._device.screencap()
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        logger.debug(f"Capture screenshot: {image_path}")
        return image_path

    @classmethod
    def screencap(cls):
        assert cls._device is not None
        return io.BytesIO(cls._device.screencap())

    @classmethod
    def send_escape(cls):
        """Send Esc"""
        assert cls._device is not None
        cls._device.shell("input keyevent 4")
        time.sleep(1.5)

    @classmethod
    def shell(cls, cmd):
        assert cls._device is not None
        cls._device.shell(cmd)

    @classmethod
    def tap(cls, x, y):
        assert cls._device is not None
        cls.shell(f"input tap {x} {y}")

    @classmethod
    def swipe(cls, x1, y1, x2, y2, duration):
        assert cls._device is not None
        cls._device.input_swipe(x1, y1, x2, y2, duration)

    @classmethod
    def input_text(cls, text: str):
        assert cls._device is not None
        for c in text:
            cls._device.shell(f"input text '{c}'")
            utils.sleep_random(0.15, 0.3)
        time.sleep(0.5)  # Wait for input to complete

    @classmethod
    def send_enter(cls, delay=2):
        # adb shell input keyevent 66
        assert cls._device is not None
        cls._device.shell("input keyevent 66")
        utils.sleep_random(delay, delay + 0.2)
