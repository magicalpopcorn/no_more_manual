""" """

import math
import time

from src.lib import logger, utils
from src.lib.element import (
    CENTER_POINT,
    P,
    ResourceAmount,
    ResourceSet,
    ResourceType,
    TaxRate,
    TransportCapacity,
)
from src.lib.rok_data import Character
from src.lib.rok_profile import RokProfile
from src.lib.ui import MenuMain, MenuRssAssist, MenuSearchLocation
from src.lib.ui.sub_menu import MenuItems, MenuStatistics
from src.lib.vision import ocr


class Assist:
    MINIMUM_PROTECTED_CAP = ResourceAmount("2M")
    DEFAULT_VELOCITY = 0.5  # tiles per second

    def __init__(self):
        self.profile = RokProfile()
        self.target: P = P(*tuple(self.profile.data["assist"]["target"]))
        self.MAX_CAP = ResourceAmount(self.profile.data.get("assist", {}).get("max_cap", "1B"))
        self.total_transfered = ResourceAmount(0)

    def transport_rss(self, char: Character):

        self.total_transfered = ResourceAmount(0)

        # open menu main buildings
        # MenuCity.open()
        MenuMain.open_map_screen()
        CENTER_POINT.click(verify=MenuMain.is_city_info_visible)
        self.city_loc = self.get_city_loc()
        rss_set = self.get_rss_set(char._id)

        # we can capture tax rate and trans_cap in menu resource assistance
        trans_cap = TransportCapacity.from_ch(char.ch)
        tax = TaxRate.from_ch(char.ch)
        interval = self.calc_interval(avail_marches=5)
        if interval > 30:
            logger.warning(f"Long interval detected: {interval:.2f}s")

        # Info first
        total_time = 0
        for rss_type in ResourceType:
            rss_amount = rss_set.get_rss_amount(rss_type)
            avail_amount, send_amount, actual_tax, times = self.dry_calculation(
                rss_amount, trans_cap, tax
            )

            logger.info(
                f"Assist\n\tType: {rss_type}, amount: {avail_amount}, tax: {tax}\n"
                f"\tSend {send_amount.__str__(explicit=True)}, Receive: {trans_cap} (tax={actual_tax.__str__(explicit=True)})\n"
                f"\tInterval {interval:.2f}s, {times} times, total: {interval * times:.2f}s"
            )
            total_time += interval * times
        logger.info(f"Total assisting time estimated: {total_time:.2f}s")

        logger.info("Start assisting...")
        self.locate_target(self.target)
        for rss_type in ResourceType:
            rss_amount = rss_set.get_rss_amount(rss_type)
            self.assist(rss_type, rss_amount, tax, trans_cap, interval)

    def locate_target(self, target: P):
        """locate target"""
        MenuSearchLocation.locate(*target.xy)

    def dry_calculation(
        self, rss_amount: ResourceAmount, trans_cap: TransportCapacity, tax: TaxRate
    ):
        if rss_amount < self.MINIMUM_PROTECTED_CAP:
            avail_amount = ResourceAmount(0)
        else:
            avail_amount = rss_amount - self.MINIMUM_PROTECTED_CAP
        send_amount = trans_cap.actual_amount(tax)
        actual_tax = send_amount - trans_cap
        times = int(avail_amount // send_amount)
        return avail_amount, send_amount, actual_tax, times

    def assist(
        self,
        rss_type: ResourceType,
        rss_amount: ResourceAmount,
        tax: TaxRate,
        trans_cap: TransportCapacity,
        interval,
    ):
        """trans_cap = actual receive"""
        avail_amount, send_amount, actual_tax, times = self.dry_calculation(
            rss_amount, trans_cap, tax
        )

        logger.action(
            "Assisting",
            f"\n\tType: {rss_type}, amount: {avail_amount}, tax: {tax}\n"
            f"\tSend {send_amount.__str__(explicit=True)}, Receive: {trans_cap} (tax={actual_tax.__str__(explicit=True)})\n"
            f"\tInterval {interval:.2f}s, {times} times, total: {interval * times:.2f}s",
        )

        slider = MenuRssAssist.get_slider(rss_type)
        while avail_amount > 0 and self.total_transfered < self.MAX_CAP:
            # Open menu resource assistance
            CENTER_POINT.click(delay=0.8, verify=MenuMain.is_btn_assist_visible)

            start_time = time.time()
            max_timeout = 30  # 30 seconds timeout

            while True:
                try:
                    MenuMain.BTN_ASSIST.click(delay=0.8, verify=MenuRssAssist.is_open)
                except TimeoutError:
                    pass
                if MenuRssAssist.is_open():
                    break
                if time.time() - start_time > max_timeout:
                    raise TimeoutError("Failed to open resource assistance menu after 30s")
                utils.sleep_random(3, 5)

            offset_x = int(MenuRssAssist.SLIDER_LENGTH * send_amount / avail_amount)
            slider.drag(offset_x=(offset_x + 20, offset_x + 50), offset_y=(-100, -10))

            MenuRssAssist.transport()
            avail_amount -= send_amount
            self.total_transfered += send_amount
            logger.debug(
                f"total_transfer: {self.total_transfered} ,{rss_type} leftover: {avail_amount}"
            )
            utils.sleep_random(interval, interval + 0.5)

    def get_rss_set(self, char_id) -> ResourceSet:
        with MenuItems(char_id):
            with MenuStatistics(char_id) as ms:
                return ms.get_available_rss()

    @staticmethod
    def calc_transport_time(p1: P, p2: P, v=DEFAULT_VELOCITY):
        """Calculate the transport time between two points."""
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        distance = math.hypot(dx, dy)
        if distance <= 5:
            v *= 5  # speed up for short distance
        logger.debug(f"Distance between {p1} and {p2}: {distance:.2f} pixels")
        return distance / v

    @staticmethod
    def get_current_loc():
        return P.from_coord(
            ocr.extract_text_from_rect(MenuMain.BTN_LOCATION, whitelist="1234567890XY:")
        )

    @staticmethod
    def get_city_loc():
        """Get the current city location."""
        rect = MenuMain.RECT_CITY_LOC
        text = ocr.extract_text_from_rect(rect, whitelist="1234567890XY:")
        if not text:
            raise ValueError("Failed to extract city location from OCR")
        return P.from_coord(text)

    def calc_interval(self, avail_marches=5):
        city_loc = self.city_loc
        target_loc = self.target
        return Assist.calc_transport_time(city_loc, target_loc) * 2 / avail_marches  # send and back
