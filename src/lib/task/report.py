import json
import os

from src.lib import const, logger, utils
from src.lib.element.resource import ResourceSet
from src.lib.rok_data import Character
from src.lib.ui.sub_menu import MenuItems, MenuStatistics


class Report:
    def __init__(self):
        pass

    @utils.only_during_periods(const.TIME_EARLY_MORNING)
    def collect_info(self, char: Character):
        with MenuItems(char._id):
            with MenuStatistics(char._id) as ms:
                try:
                    ms.get_total_rss()
                    ms.get_available_rss()
                    ms.save_rss_stats()
                except Exception as err:
                    logger.error(f"Failed to get rss info for {char._id}: {err}", exc_info=True)

    def report(self):
        # rss.json is a general file for all char_id
        rss_file = const.RSS_PATH
        if not os.path.exists(rss_file):
            logger.error("rss.json not found")
            return

        with open(rss_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = {}

        # Iterate through each character's data
        for char_data in data.values():
            for key, key_data in char_data.items():
                if key not in result:
                    result[key] = ResourceSet.from_dict(key_data)
                else:
                    result[key] += ResourceSet.from_dict(key_data)

        return result
