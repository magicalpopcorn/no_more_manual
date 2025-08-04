from abc import ABC, abstractmethod
from typing import final

from src import logger
from src.api import adb
from src.element import RectZone
from src.vision import image, ocr


class _Menu(ABC):
    """Base Menu, suitable for menus that require manual closing.
    NOT all menus should inherit this

    Closing Menu is default by pressing Esc shortcut
    """

    RECT_TITLE: RectZone = None
    MENU_WINDOW: RectZone = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    @abstractmethod
    def open(cls):
        """Child classes should override this method"""
        logger.info(f"Open {cls.__name__}")

    @classmethod
    def is_open(cls):
        if cls.RECT_TITLE:
            return ocr.extract_text_from_rect(cls.RECT_TITLE) == cls.RECT_TITLE.name
        logger.warning(f"RECT_TITLE is not defined in {cls.__name__}")
        return True

    @classmethod
    def close(cls):
        logger.info(f"Close {cls.__name__}")
        adb.send_escape()

    @classmethod
    @final
    def capture(cls):
        if cls.MENU_WINDOW:
            image.get_image_from_rect(cls.MENU_WINDOW, save=True)
        else:
            logger.warning(f"RectZone not defined for {cls.__name__}")
