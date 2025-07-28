import os

from pyldplayer import LDAppAttr, LDConsole

from src import logger
from src.const import PROJECT_ROOT

_INSTANCE_NAME = "farm1"  # Set by main1.py, or "main" for main2.py

_app_attr = LDAppAttr(r"D:\LDPlayer\LDPlayer9")
_ldc = LDConsole(_app_attr)
_INSTANCE_NAME: str = None

__all__ = ["init_instance", "LDInstance"]


def init_instance(name: str):
    global _INSTANCE_NAME
    _INSTANCE_NAME = name


class LDInstance:
    @staticmethod
    def launch():
        return _ldc.launch(name=_INSTANCE_NAME)

    @staticmethod
    def quit():
        return _ldc.quit(name=_INSTANCE_NAME)

    @staticmethod
    def isrunning():
        return _ldc.isrunning(name=_INSTANCE_NAME)

    @staticmethod
    def adb(command):
        _ldc.adb(name=_INSTANCE_NAME, command=command)

    @staticmethod
    def tap(x, y):
        LDInstance.adb(f"shell input tap {x} {y}")

    @staticmethod
    def runapp(packagename):
        _ldc.runapp(name=_INSTANCE_NAME, packagename=packagename)

    @staticmethod
    def long_press(x, y, ms):
        # logger.debug(f"shell input swipe {x} {y} {x} {y} {ms}")
        LDInstance.adb(f"shell input swipe {x} {y} {x} {y} {ms}")

    @staticmethod
    def screenshot(
        remote="/sdcard/screen.png",
        local=os.path.join(PROJECT_ROOT, "tmp", "ldp", "screen.png"),
    ):
        LDInstance.adb(f"screencap -p {remote}")
        _ldc.pull(name=_INSTANCE_NAME, remote=remote, local=local)
