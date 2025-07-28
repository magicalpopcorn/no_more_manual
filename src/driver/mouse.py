import ctypes

import win32api
import win32gui

from src.const import INPUT_MOUSE, MouseEventFlag
from src.window import ROKWindow

from .ctypes_input import INPUT, MOUSEINPUT


def MouseMove(x_client, y_client):
    hwnd = ROKWindow.get()
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (x_client, y_client))
    ctypes.windll.user32.SetCursorPos(screen_x, screen_y)


def Click(x_client, y_client):
    MouseMove(x_client, y_client)
    inputs = (INPUT * 2)()
    inputs[0].type = INPUT_MOUSE
    inputs[0].mi = MOUSEINPUT(0, 0, 0, MouseEventFlag.LEFTDOWN, 0, None)
    inputs[1].type = INPUT_MOUSE
    inputs[1].mi = MOUSEINPUT(0, 0, 0, MouseEventFlag.LEFTUP, 0, None)
    ctypes.windll.user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))


def MouseLeftDown():
    win32api.mouse_event(MouseEventFlag.LEFTDOWN, 0, 0, 0, 0)


def MouseLeftUp():
    win32api.mouse_event(MouseEventFlag.LEFTUP, 0, 0, 0, 0)
