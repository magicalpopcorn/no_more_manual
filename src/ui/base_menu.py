from src import logger
from src.api import adb
from src.element import RectZone
from src.vision import ocr


class _Menu:
    """Base Menu, suitable for menus that require manual closing.
    NOT all menus should inherit this

    Closing Menu is default by pressing Esc shortcut
    """

    MENU_WINDOW: RectZone = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    def open(cls):
        logger.info(f"Open {cls.__name__}")
        # child classes should inherit

    @classmethod
    def close(cls):
        logger.info(f"Close {cls.__name__}")
        adb.send_escape()

    @classmethod
    def capture(cls):
        if cls.MENU_WINDOW:
            img_obj = ocr._crop_image_to_rect(adb.screenshot(), cls.MENU_WINDOW)
            ocr.save_image(img_obj, cls.MENU_WINDOW.name)
        else:
            logger.warning(f"RectZone not defined for {cls.__name__}")
