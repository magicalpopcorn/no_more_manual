import sys
import time

from . import api, logger, ui, utils
from .api import adb, ldc, ldp


def init_ldp(instance_name):
    ldp.init_instance(instance_name)
    if ldp.isrunning() != "running":
        ldp.launch()
        logger.debug(f"Start instance '{instance_name}', wait for 15s")
        while ldp.isrunning() != "running":
            time.sleep(1)
        logger.debug(f"Instance '{instance_name}' started")
    else:
        logger.debug(f"Instance '{instance_name}' already started")


def init_adb(instance_name):
    @utils.retry(max_attempts=3, info="Verify adb connection")
    def init_and_verify_connection():
        try:
            adb.init_instance(instance_name)
            time.sleep(1)
            adb.shell("true")
            return True
        except (RuntimeError, TimeoutError) as err:
            logger.warning(f"adb error: {err}. Try rebooting ADB server...")
            # ldc.reboot(instance_name)
            adb._device = None
            api.adb_utils.refresh_adb_server(brutal=True)
            return False

    init_and_verify_connection()


def init_rok(instance_name):
    logger.info("Init Rise of Kingdoms")
    ldp.runapp()
    ui.MenuMain.wait_for_ingame_ready()


def init_instance(instance_name, rok_ready: bool = False):
    sys.stdout.reconfigure(encoding="utf-8")
    logger.setup_logger()
    logger.action("Init start", f"Instance name: '{instance_name}'")

    if instance_name not in (instances := ldc.list()):
        raise RuntimeError(f"Instance {instance_name} not exists\nInstances: {instances}")

    api.adb_utils.refresh_adb_server()
    adb.collect_pre_running_devices()
    ldp.collect_pre_running_instances()

    init_ldp(instance_name)
    init_adb(instance_name)
    if not rok_ready:
        init_rok(instance_name)

    logger.info("-----------------INIT DONE-----------------\n")
