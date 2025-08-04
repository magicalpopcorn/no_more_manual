#!python
# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import time

FARM_INSTANCE = "farm1"
MAIN_INSTANCE = "main"
instance = FARM_INSTANCE
# instance = MAIN_INSTANCE

ROK_PACKAGE = "com.rok.gp.vn"


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
    # utils.reallocate_and_resize(instance_name, ldc.list().splitlines().index(instance_name))


def init_adb(instance_name):
    @utils.retry(max_attempts=2, info="Verify adb connection")
    def init_and_verify_connection():
        try:
            adb.init_instance(instance_name)
            adb.shell("true")
            return True
        except (RuntimeError, TimeoutError) as err:
            logger.warning(f"adb error: {err}. Try rebooting LDplayer...")
            ldc.reboot(instance_name)
            adb._device = None
            time.sleep(10)
            subprocess.check_call("adb disconnect")
            time.sleep(5)
            return False

    init_and_verify_connection()


def init_rok(instance_name):
    logger.info("Init Rise of Kingdoms")
    ldp.runapp(packagename=ROK_PACKAGE)
    ui.MenuMain.wait_for_ingame_ready()


def init_process(instance_name):
    sys.stdout.reconfigure(encoding="utf-8")
    logger.setup_logger()
    logger.action("Init start", f"Instance name: '{instance_name}'")

    if instance_name not in (instances := ldc.list()):
        raise RuntimeError(f"Instance {instance_name} not exists\nInstances: {instances}")

    subprocess.check_call("adb start-server")
    subprocess.check_call("adb disconnect")
    time.sleep(5)
    adb._pre_running_devices = {device.serial for device in adb._client.devices()}
    ldp._running_instances = set(ldc.runninglist().splitlines())

    init_ldp(instance_name)
    init_adb(instance_name)
    init_rok(instance_name)

    logger.info("-----------------INIT DONE-----------------\n")


def test():
    # ui.MenuMain.open_city_screen()
    # text = ui.MenuItems._get_item_name()
    # print(text)
    # ui.MenuMain.wait_for_ingame_ready()
    # vision.image.get_image_from_rect(ui.MenuMain.BTN_HOME, save=True)
    vision.image.screenshot()
    with ui.MenuItems("dei 2f1"):
        time.sleep(1)
    # print(
    #     vision.cv.match_region_with_template(
    #         ui.MenuItems.BTN_RESOURCES, vision.image.TemplateImage("picked_res.png"), verbose=True
    #     )
    # )
    sys.exit(0)


def capture():
    # capture button
    # btn = ui.MenuSearch._BTN_BASE_DEPOSITE
    btn = ui.MenuItems.BTN_RESOURCES
    vision.image.get_image_from_rect(btn, save=True)
    sys.exit(0)


if __name__ == "__main__":
    try:
        from src import action, const, element, logger, ui, utils, vision
        from src.api import adb, ldc, ldp
        from src.const import ActionMode
        from src.rok_profile import RokProfile

        DIR_PATH = os.path.dirname(os.path.realpath(__file__))

        init_process(instance)

        if len(sys.argv) > 1:
            if sys.argv[1] == "test":
                test()
            elif sys.argv[1] == "cap":
                capture()

        profile = RokProfile()
        walker = action.Walker()

        # Declare and register actions to walker
        gatherer = action.Gather()
        use_item = action.UseItems()
        collector = action.Collect()

        for action in [
            use_item.use_24h_gather_boost,
            gatherer.gather,
            # collector.collect_all,
        ]:
            walker.register_action(action)

        # Run with action mode
        match profile.action_mode:
            case ActionMode.CHARACTER:
                walker.walk_character()
            case ActionMode.ACCOUNT:
                walker.walk_account()
            case ActionMode.ALL_ACCOUNTS:
                walker.walk_all()
            case _:
                raise RuntimeError(f"Weird action mode {profile.action_mode}")

        logger.info("Finished !!!")
    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt")
        sys.exit(1)
    except Exception:
        logger.exception("Exception", stack_info=True)
        time.sleep(10)
        sys.exit(1)
