import os
import signal
import subprocess
import sys
import time

import keyboard

from src import logger, privilege

dir_path = os.path.dirname(os.path.realpath(__file__))


def run_macro():
    privilege.run_as_admin()
    logger.controller("Starting macro...")
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    arg = ""
    if len(sys.argv) >= 2:
        arg = sys.argv[1]
    main_script = os.path.join(dir_path, "main.py")
    proc = subprocess.Popen(["python", main_script, arg], startupinfo=startupinfo)

    logger.controller("Press Ctrl+Q to stop the macro.")
    keyboard.wait("ctrl+q")
    logger.controller("Ctrl+Q pressed. Stopping macro...")
    proc.kill()
    logger.controller("Macro process terminated.")
    time.sleep(0.5)
    if proc.poll() is None:
        logger.controller("ERROR: Process is still alive!")
    else:
        logger.controller("Macro successfully stopped.")


if __name__ == "__main__":
    run_macro()
