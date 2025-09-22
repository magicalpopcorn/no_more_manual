from src import const, logger
from src.ui.sub_menu import MenuItems
from src.utils import only_during_periods


class UseItems:
    def __init__(self):
        pass

    def use_item(self, char_id, item_name: str, force=False):
        with MenuItems(char_id) as mi:
            item = mi.get_boost_item_by_name(item_name)
            if item is None:
                return
            mi.use_boost_item(force)

    def use_8h_gather_boost(self, char_id: str):
        """
        Use 8h gathering boost item for character
        """
        item = MenuItems.BOOST_GATHER_8
        logger.action("Use boost item", item)
        self.use_item(char_id, item, force=False)

    @only_during_periods(const.TIME_EARLY_MORNING)
    def use_24h_gather_boost(self, char_id: str):
        """
        Use 24h gathering boost item for character
        """
        item = MenuItems.BOOST_GATHER_24
        logger.action("Use boost item", item)
        self.use_item(char_id, item, force=True)
