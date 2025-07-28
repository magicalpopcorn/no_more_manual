import os
import subprocess

from src.ahk import AHK_API, AHK_DIR, AHK_PATH


def Send(key: str):
    subprocess.run([AHK_PATH, os.path.join(AHK_DIR, "send.ahk"), key])


def SendText(text: str):
    subprocess.run([AHK_PATH, os.path.join(AHK_DIR, "send_text.ahk"), text])


def SendAHK(key: str):
    AHK_API.send(key)
