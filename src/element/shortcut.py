from src import logger
from src.driver import keyboard
from src.utils import sleep_random


class Shortcut:
    def __init__(self, name, shortcut):
        self.name = name
        self.shortcut = shortcut

    def press(self, delay=800):
        logger.debug(f"Press shortcut: {self.name} ({self.shortcut})")
        keyboard.SendAHK(self.shortcut)
        sleep_random(delay, delay + 200)


SC_SEARCH = Shortcut("Search Gathering", "f")
SC_CAMPAIGN = Shortcut("Campaign_Menu", "u")
SC_ALLIANCE = Shortcut("Alliance_Menu", "o")
SC_CHAT_BOX = Shortcut("Chat_Box", "{Enter}")
SC_VIP = Shortcut("VIP_Menu", "v")
SC_ITEMS = Shortcut("Items_Menu", "i")
SC_MAIL = Shortcut("Mail_Box", "z")
SC_QUESTS = Shortcut("Quests_Menu", "l")
SC_USER_PROFILE = Shortcut("User_Profile", "{Esc}")


# Common behaviors
SC_CANCEL = Shortcut("Cancel", "{Esc}")
SC_CLOSE = Shortcut("Close", "{Esc}")
SC_ENTER = Shortcut("Enter", "{Enter}")
SC_SPACE = Shortcut("Space", "{Space}")
