from src import logger
from src.element import Button, P


class MenuMain:
    BTN_HOME = Button("Home", P(55, 950), P(130, 1020))  # d
    BTN_HOME_BUILDINGS = Button("Buildings", P(375, 1000), P(440, 1055))  # d
    BTN_USER_PROFILE = Button("User_Profile", P(25, 10), P(105, 95))  # d

    @classmethod
    def navigate_to_map_screen(cls):
        logger.debug("Open Map screen")
        cls.BTN_HOME.hold()
        cls.BTN_HOME_BUILDINGS.click()
