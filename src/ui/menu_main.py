from src import logger
from src.element import BTN_HOME, BTN_HOME_BUILDINGS


class MenuMain:

    @staticmethod
    def navigate_to_map_screen():
        logger.debug("Open Map screen")
        BTN_HOME.hold()
        BTN_HOME_BUILDINGS.click(1000)
