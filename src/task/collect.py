import re
import time

from src import const, logger
from src.ui import MenuCity, MenuMerchant
from src.utils import only_during_periods
from src.vision import ocr


class Collect:
    def __init__(self):
        pass

    def collect_all(self, char_id: str):
        """Open menu City to collect some rewards
        + Purchase items from Merchant boutique
        + Claim resources from deposite
        + TODO: Claim VIP
        + TODO: Claim expedition chests
        + TODO: Claim alliance chests
        """
        with MenuCity():
            self.purchase_items()
            # self.claim_vip()
            # self.claim_rss_in_city()

    @only_during_periods([const.TIME_EARLY_MORNING, const.TIME_NIGHT])
    def claim_rss_in_city(self):
        for btn in MenuCity.get_deposite_buttons():
            btn.click()

    @only_during_periods(const.TIME_EARLY_MORNING)
    def claim_vip(self):
        logger.debug("This should only triggered in the morning")

    def purchase_items(self):
        try:
            with MenuMerchant() as mm:
                if not mm.is_open_for_sell():
                    logger.info("Merchant closes, not today")
                    return
                logger.action("Purchase Item", "Merchant opens, let's buy some")
                for _ in range(2):
                    # 2 times scroll + 3 times buy
                    for i in range(3):
                        for price in mm.ITEM_PRICES:
                            raw_price = ocr.extract_number_from_rect(price, save=True)
                            logger.debug(f"{price.name} Raw price: {raw_price}")
                            if obj := re.search(r"\d+,\d+", raw_price):
                                try:
                                    if int(obj.group().replace(",", "")) > 100000:
                                        logger.debug(f"Found item, price: {obj.group()}")
                                        price.click()
                                except Exception as err:
                                    logger.error(f"Something is WRONG with purchasing: {err}")
                            else:
                                time.sleep(0.1)
                        logger.debug("After buying items")
                        mm.capture()

                        if i != 2:
                            logger.debug("Scroll up for next item type")
                            mm.scrollup(extra=10 * (i - 1))
                            mm.capture()
                    # Free refresh
                    if mm.is_free_refresh_available():
                        mm.BTN_REFRESH.click(verify=lambda: not mm.is_free_refresh_available())
                    else:
                        break
        except RuntimeError as err:
            logger.error(err)
            return
