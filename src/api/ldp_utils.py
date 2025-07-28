import os
import time
from typing import List

from pyldplayer import LDAppAttr, LDConsole

from src import logger
from src.const import PROJECT_ROOT

_app_attr = LDAppAttr(r"D:\LDPlayer\LDPlayer9")
ldc = LDConsole(_app_attr)


class LDInstance:
    _instance_name: str = None

    @classmethod
    def init_instance(cls, name: str):
        if cls._instance_name is None:
            logger.debug("Init LDInstance")
            cls._instance_name = name
        else:
            logger.warning(f"Failed to init LDInstance: {cls._instance_name}")

    @staticmethod
    def list() -> List[str]:
        return ldc.list().splitlines()

    @staticmethod
    def launch():
        return ldc.launch(name=LDInstance._instance_name)

    @staticmethod
    def quit():
        return ldc.quit(name=LDInstance._instance_name)

    @staticmethod
    def isrunning():
        return ldc.isrunning(name=LDInstance._instance_name)

    @staticmethod
    def adb(command):
        return ldc.adb(name=LDInstance._instance_name, command=command)

    @staticmethod
    def tap(x, y):
        LDInstance.adb(f"shell input tap {x} {y}")

    @staticmethod
    def runapp(packagename):
        ldc.runapp(name=LDInstance._instance_name, packagename=packagename)

    @staticmethod
    def long_press(x, y, ms):
        LDInstance.adb(f"shell input swipe {x} {y} {x} {y} {ms}")
