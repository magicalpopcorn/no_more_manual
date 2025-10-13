from src.lib.const import FARM_THREAD_POSITION
from src.lib.element import Button, Gap, P
from src.lib.utils import sleep_random


class ChatBox:
    _GAP = Gap(105)
    is_expanded = False
    current_thread = 1

    # expand state is not shared between characters/accounts
    BTN_EXPAND = Button("Chat_Expand", P(21, 19), P(45, 39))
    BTN_CLOSE_EXPAND = Button("Close_Chat_Expand", P(361, 19), P(383, 39))
    _BTN_BASE_THREAD = Button("Thread", P(51, 77), P(291, 132))
    BTN_CHAT_ZONE = Button("Chat_Zone", P(374, 1015), P(779, 1035))

    # @classmethod
    # def open(cls):
    #     logger.debug("Open Menu Chatbox")
    #     SC_CHAT_BOX.press()
    #     if not cls.is_expanded:
    #         cls.BTN_EXPAND.click()
    #         cls.is_expanded = True

    # @classmethod
    # def close(cls):
    #     logger.debug("Close Menu Chatbox")
    #     if cls.is_expanded:
    #         cls.BTN_CLOSE_EXPAND.click()
    #         cls.is_expanded = False
    #     SC_CLOSE.press()

    # @classmethod
    # def reset(cls):
    #     cls.is_expanded = False

    # @classmethod
    # def get_thread_chat(cls, thread_num=1) -> Button:
    #     if thread_num < 1 or thread_num > 9:
    #         raise ValueError(f"Invalid thread number: {thread_num}")

    #     y_offset = (thread_num - 1) * cls._GAP
    #     p1 = P(cls._BTN_BASE_THREAD.p1.x, cls._BTN_BASE_THREAD.p1.y + y_offset)
    #     p2 = P(cls._BTN_BASE_THREAD.p2.x, cls._BTN_BASE_THREAD.p2.y + y_offset)
    #     return Button(f"Thread_{thread_num}", p1, p2)

    # @classmethod
    # def choose_thread_chat(cls, thread_num=1):
    #     logger.debug(f"Choose thread {thread_num}")
    #     if thread_num != cls.current_thread:
    #         cls.current_thread = thread_num
    #         cls.get_thread_chat(thread_num).click()

    # @classmethod
    # def send_text(cls, text: str):
    #     logger.debug(f"Sending: {text}")
    #     cls.BTN_CHAT_ZONE.click()
    #     keyboard.SendText(text)
    #     sleep_random(0.1, 0.2)

    #     SC_ENTER.press()
    #     sleep_random(0.1, 0.2)


# def confirm_done(text="Done"):
#     ChatBox.open()
#     sleep_random(0.5, 0.7)
#     ChatBox.choose_thread_chat(FARM_THREAD_POSITION)
#     ChatBox.send_text(text)
#     sleep_random(0.5, 0.7)
#     ChatBox.close()
