from src.dpi import DPIAwareMixin


class Distance(int, DPIAwareMixin):
    def __new__(cls, length: int):
        l = int(length * cls.get_ratio())
        return super().__new__(cls, l)


class Gap(Distance):
    pass


class Length(Distance):
    pass


class Width(Distance):
    pass


class Height(Distance):
    pass
