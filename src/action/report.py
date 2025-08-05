import json
import os

from src import const, logger, utils
from src.rok_profile import RokProfile
from src.ui import MenuItems, MenuStatistics
from src.ui.menu_items import ResourceAmount, ResourceSet


class Report:
    def __init__(self):
        self.profile = RokProfile()

    @utils.only_during_periods(const.TIME_EARLY_MORNING)
    def collect_info(self, char_id):
        with MenuItems(char_id):
            with MenuStatistics(char_id) as ms:
                try:
                    ms.get_total_rss()
                    ms.get_available_rss()
                    ms.save_rss_stats()
                except Exception as err:
                    logger.error(f"Failed to get rss info for {char_id}: {err}", exc_info=True)

    def report(self):
        # rss.json is a general file for all char_id
        rss_file = MenuStatistics.RSS_PATH
        if not os.path.exists(rss_file):
            logger.error("rss.json not found")
            return

        with open(rss_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = {}

        # Iterate through each character's data
        for char_id, char_data in data.items():
            for key, key_data in char_data.items():
                if key not in result:
                    result[key] = ResourceSet.from_dict(key_data)
                else:
                    result[key] += ResourceSet.from_dict(key_data)

        return result
