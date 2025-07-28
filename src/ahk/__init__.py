"""
Alternative solution is that we can use python-ahk

Either use python-AHK or trigger AHK script
"""

import os

from ahk import AHK
from ahk.directives import NoTrayIcon

_directives = [NoTrayIcon(apply_to_hotkeys_process=True)]

AHK_PATH = r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe"
AHK_API = AHK(executable_path=AHK_PATH, directives=_directives)
AHK_DIR = os.path.dirname(os.path.realpath(__file__))
