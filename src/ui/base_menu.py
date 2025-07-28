from src import logger
from src.element import SC_CLOSE, RectZone
from src.vision import screenshot


class _Menu:
    """Base Menu, suitable for menus that require manual closing.
    NOT all menus should inherit this

    Closing Menu is default by pressing SC_CLOSE - Esc shortcut
    """

    MENU_WINDOW: RectZone = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    def open(cls):
        logger.debug(f"Open {cls.__name__}")
        # child classes should inherit

    @classmethod
    def close(cls):
        logger.debug(f"Close {cls.__name__}")
        SC_CLOSE.press(1000)

    @classmethod
    def capture(cls):
        if cls.MENU_WINDOW:
            screenshot.capture(cls.MENU_WINDOW, save=True)
        else:
            logger.warning(f"RectZone not defined for {cls.__name__}")
