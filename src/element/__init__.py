import random

from .button import *
from .distance import *
from .pixel import *
from .shortcut import *

_use_shortcuts = random.choice([True, False])


def click_btn_or_press_sc(button: Button, shortcut: Shortcut):
    """
    Perform an action by either clicking the button or pressing the shortcut,
    randomly chosen once per session.
    """
    if _use_shortcuts:
        shortcut.press()
    else:
        button.click()
