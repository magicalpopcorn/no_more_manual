import io
import json
import os
import time

from ppadb.client import Client as AdbClient
from ppadb.device import Device

from src import logger
from src.const import PROJECT_ROOT

from .ldp_utils import LDInstance as ldp

MAPPING_FILE = PROJECT_ROOT / "adb_ldp_mapping.json"


class ADBInstance:
    _client = AdbClient(host="127.0.0.1", port=5037)
    _device: Device = None
    _pre_running_devices: set = None

    @classmethod
    def init_instance(cls, instance_name):
        """FIXME: Spagetti code, pls refactor

        Raise: ConnectionError
        """
        if cls._device is None:
            logger.debug(f"Init ADBInstance with LDPInstance {instance_name}")
            logger.debug(f"_pre_running_devices: {cls._pre_running_devices}")
            timeout = 30  # seconds
            start_time = time.time()

            if instance_name not in ldp._running_instances:
                logger.debug("Fresh init. Wait for device up")
                # At this point ldpinstance should be already started
                # wait for new element in cls._client.devices()
                while len(cls._client.devices()) == len(cls._pre_running_devices):
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Timeout: No new device appeared within the given time.")
                    logger.warning(f"Device not ready, wait for more... {cls._client.devices()}")
                    time.sleep(5)
                # adb devices will have new device
                devices = {device.serial for device in cls._client.devices()}
                logger.debug(f"Device ready: {devices}")
                device_serial = devices - cls._pre_running_devices
                if len(device_serial) != 1:
                    raise ConnectionError(
                        f"How TF device_serial more than 2: {device_serial}. Recheck pls"
                    )
                device_serial = device_serial.pop()
                logger.info(f"Desired device to connect {device_serial}")
                for device in cls._client.devices():
                    if device_serial == device.serial:
                        cls._device = device
                        logger.info(f"Connected adb {device.serial} with instance {instance_name}")
                        with open(MAPPING_FILE, "r+", encoding="utf-8") as f:
                            data = json.load(f)
                            data[instance_name] = device.serial
                            f.seek(0)
                            json.dump(data, f, indent=4)
                            f.truncate()
                        break
                else:
                    raise ConnectionError(f"Device for LDPInstance {instance_name} not found")
            else:
                # In case instance already started, but just get the instance
                logger.debug("Instance already initiated")
                with open(MAPPING_FILE, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                device_serial = data[instance_name]
                for device in cls._client.devices():
                    if device_serial == device.serial:
                        cls._device = device
                        logger.info(f"Connected adb {device.serial} with instance {instance_name}")
                        break
                else:
                    raise ConnectionError(f"Device for LDPInstance {instance_name} not found")
        else:
            logger.warning(f"ADBInstance already initiated: {cls._device}")

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
