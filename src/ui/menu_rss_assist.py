from functools import cache

from src.element import Button, P, RectZone, ResourceType

from .base_menu import _Menu


class MenuRssAssist(_Menu):
    RECT_TITLE = RectZone("RESOURCE ASSISTANCE", P(690, 100), P(1225, 150))

    # sliders
    _BTN_SLIDER = Button("Slider", P(880, 320), P(900, 350))
    SLIDER_LENGTH = 510  # pixel
    GAP = 135

    BTN_TRANSPORT = Button("Transport", P(1070, 850), P(1287, 920))

    @classmethod
    @cache
    def get_slider(cls, rss_type: ResourceType) -> Button:
        i = ResourceType.index(rss_type)
        offset_y = i * cls.GAP
        return Button(
            f"{rss_type} Slider",
            P(cls._BTN_SLIDER.p1.x, cls._BTN_SLIDER.p1.y + offset_y),
            P(cls._BTN_SLIDER.p2.x, cls._BTN_SLIDER.p2.y + offset_y),
        )

    @classmethod
    def transport(cls):
        cls.BTN_TRANSPORT.click(verify=cls.is_closed)
