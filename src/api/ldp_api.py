from pyldplayer import LDAppAttr, LDConsole

from src import const, logger

_app_attr = LDAppAttr(r"D:\LDPlayer\LDPlayer9")
ldc = LDConsole(_app_attr)


class LDInstance:
    _instance_name: str = ""
    _pre_running_instances: set = set()

    @classmethod
    def collect_pre_running_instances(cls):
        """Collect the pre-running instances for the LDPlayer."""
        cls._pre_running_instances = set(ldc.runninglist().splitlines())

    @classmethod
    def get_pre_running_instances(cls) -> set:
        return cls._pre_running_instances

    @classmethod
    def init_instance(cls, name: str):
        if not cls._instance_name:
            logger.debug("Init LDInstance")
            cls._instance_name = name
        else:
            logger.warning(f"Failed to init LDInstance: {cls._instance_name}")

    @staticmethod
    def launch():
        return ldc.launch(name=LDInstance._instance_name)

    @staticmethod
    def killapp():
        return ldc.killapp(name=LDInstance._instance_name, packagename=const.ROK_PACKAGE)

    @staticmethod
    def reload_app():
        LDInstance.killapp()
        LDInstance.runapp()

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
    def runapp():
        ldc.runapp(name=LDInstance._instance_name, packagename=const.ROK_PACKAGE)

    @staticmethod
    def long_press(x, y, ms: int):
        LDInstance.adb(f"shell input swipe {x} {y} {x} {y} {int(ms)}")
