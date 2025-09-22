import time

from src import const, logger
from src.ui import MenuCity, MenuMerchant
from src.ui.sub_menu.menu_alliance import MenuAlliance
from src.utils import only_during_periods
from src.vision import ocr


class Collect:
    def __init__(self):
        pass

    def collect_all(self, char_id=None):
        """Open menu City to collect some rewards
        + Purchase items from Merchant boutique
        + Claim resources from deposite
        + TODO: Claim VIP
        + TODO: Claim expedition chests
        + TODO: Claim alliance chests
        """
        self.collect_alliance_rss()
        with MenuCity():
            self.purchase_items()
            # self.claim_vip()
            # self.claim_rss_in_city()

    def collect_alliance_rss(self):
        logger.debug("Collect Alliance RSS")
        with MenuAlliance() as ma:
            with ma.MenuAllianceTerritory() as mat:
                mat.BTN_CLAIM.click()

    @only_during_periods([const.TIME_EARLY_MORNING, const.TIME_NIGHT])
    def claim_rss_in_city(self):
        for btn in MenuCity.get_deposite_buttons():
            btn.click()

    @only_during_periods(const.TIME_EARLY_MORNING)
    def claim_vip(self):
        logger.debug("This should only triggered in the morning")

    def purchase_items(self):
        try:
            if not MenuMerchant.IS_AVAILABLE:
                logger.info("Merchant is not available")
                return
            with MenuMerchant() as mm:
                if not mm.is_open_for_sell():
                    logger.info("Merchant closes, not today")
                    MenuMerchant.IS_AVAILABLE = False
                    return
                logger.action("Purchase Item", "Merchant opens, let's buy some")
                for _ in range(2):
                    mm.swipe_up()
                    time.sleep(2.5)
                    btn_price = mm.search_boost_24_gather()
                    if btn_price:
                        logger.info(f"Found 24h gather boost at {btn_price}")
                        btn_price.click()
                        if ocr.extract_text_from_rect(mm.BTN_NOTICE_NO) == mm.BTN_NOTICE_NO.name:
                            mm.BTN_NOTICE_NO.click(
                                verify=lambda: ocr.extract_text_from_rect(mm.BTN_NOTICE_NO) != "NO"
                            )
                    else:
                        logger.info("No 24h gather boost found")
                    # Free refresh
                    if mm.is_free_refresh_available():
                        mm.BTN_REFRESH.click(verify=lambda: not mm.is_free_refresh_available())
                    else:
                        break
        except (RuntimeError, TimeoutError) as err:
            logger.error(err)
            return
