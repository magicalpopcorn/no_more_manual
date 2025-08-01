from src import const, logger
from src.ui import MenuItems
from src.utils import only_during_periods


class UseItems:
    def __init__(self):
        pass

    def use_8h_gather_boost(self, char_id: str):
        """
        Use 8h gathering boost item for character
        """
        logger.action("Use boost item", MenuItems.BOOST_GATHER_8)
        with MenuItems(char_id) as mi:
            item = mi.get_boost_item_by_name(mi.BOOST_GATHER_8)
            if item is None:
                return
            mi.use_boost_item(force=False)

    @only_during_periods(const.TIME_EARLY_MORNING)
    def use_24h_gather_boost(self, char_id: str):
        """
        Use 24h gathering boost item for character
        """
        logger.action("Use boost item in EARLY_MORNING", MenuItems.BOOST_GATHER_24)
        with MenuItems(char_id) as mi:
            item = mi.get_boost_item_by_name(mi.BOOST_GATHER_24)
            if item is None:
                return
            mi.use_boost_item(force=True)
