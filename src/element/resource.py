import re
from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
    FOOD = "food"
    WOOD = "wood"
    STONE = "stone"
    GOLD = "gold"

    @classmethod
    def all(cls) -> list[str]:
        return [member.value for member in ResourceType]

    @classmethod
    def index(cls, value) -> int:
        members = list(cls)
        return members.index(value)

    def __str__(self):
        return self.value


@dataclass
class TaxRate:
    _rate: float  # default, unit %

    @classmethod
    def from_ch(cls, ch: int) -> "TaxRate":
        """
        Get the tax rate based on the Trading post level.
        Args:
            ch (int): The Trading post level.
        Returns:
            float: The tax rate.
        """
        match ch:
            case 22:
                return cls(14)
            case 23:
                return cls(12)
            case 24:
                return cls(10)
            case 25:
                return cls(8)
            case _:
                raise NotImplementedError("Tax rate not implemented for this Trading post level")

    def __str__(self):
        return f"{self._rate}%"

    @property
    def value(self) -> float:
        """
        Convert the tax rate to a float representation.
        """
        return self._rate / 100


class ResourceAmount(float):
    """
    Stores resource values in millions (float).
    Supports parsing from strings like '100.0M' or '1.4B',
    conversion to int, and arithmetic operations.
    """

    MULTIPLIERS = {"M": 1, "B": 1000}

    def __new__(cls, value: float | str):
        if isinstance(value, str):
            value = cls._parse_string(value)
        elif not isinstance(value, (int, float)):
            raise TypeError(
                f"ResourceAmount must be initialized with a number or string, got {type(value)}"
            )
        return super().__new__(cls, value)

    @classmethod
    def _parse_string(cls, s: str) -> float:
        """Parse a resource string like '100.0M' or '1.4B' to float value in millions."""
        match = re.match(r"([\d.,]+)\s*([MB])", s.strip().upper())
        if not match:
            raise ValueError(f"Invalid resource format: {s}")
        num, unit = match.groups()
        num = float(num.replace(",", ""))
        return num * cls.MULTIPLIERS[unit]

    @classmethod
    def from_str(cls, s: str):
        """Parse a resource string like '100.0M' or '1.4B' to ResourceAmount."""
        return cls(s)

    def to_int(self):
        """Convert to integer (units)."""
        return int(self * 1_000_000)

    def __sub__(self, other, double_check=False):
        if isinstance(other, ResourceAmount):
            result = float(self) - float(other)
        else:
            result = float(self) - other

        # OCR bug: if result < 0 and self starts with 1, it's likely a misread 7
        if double_check and result < 0 and str(int(self))[0] == "1":
            # Replace first digit with 7 and recalculate
            corrected_str = "7" + str(int(self))[1:]
            try:
                corrected_value = float(corrected_str + str(float(self))[len(corrected_str) :])
                result = corrected_value - (
                    float(other) if isinstance(other, ResourceAmount) else other
                )
            except Exception:
                pass  # fallback to original result if conversion fails

        return ResourceAmount(result)

    def __add__(self, other):
        """Addition that returns ResourceAmount"""
        if isinstance(other, ResourceAmount):
            return ResourceAmount(float(self) + float(other))
        return ResourceAmount(float(self) + other)

    def __radd__(self, other):
        """Reverse addition that returns ResourceAmount"""
        if isinstance(other, ResourceAmount):
            return ResourceAmount(float(other) + float(self))
        return ResourceAmount(other + float(self))

    def __mul__(self, other):
        """Multiplication that returns ResourceAmount"""
        return ResourceAmount(float(self) * other)

    def __rmul__(self, other):
        """Reverse multiplication that returns ResourceAmount"""
        return ResourceAmount(other * float(self))

    def __truediv__(self, other):
        """Division that returns ResourceAmount"""
        return ResourceAmount(float(self) / other)

    def after_tax(self, tax: TaxRate) -> "ResourceAmount":
        """Returns a new ResourceAmount after tax reduction."""
        return ResourceAmount(float(self) * (1 - tax.value))

    def tax(self, tax: TaxRate) -> "ResourceAmount":
        """Returns a new ResourceAmount with tax applied."""
        return ResourceAmount(float(self) * tax.value)

    def __str__(self, explicit=False):
        if explicit:
            return f"{int(self * 1_000_000):,}"
        if self >= 1000:
            return f"{self / 1000:.1f}B"
        return f"{self:.1f}M"

    def __repr__(self):
        return f"ResourceAmount({self:.1f}M)"


class TransportCapacity(ResourceAmount):

    @classmethod
    def from_ch(cls, ch: int) -> "TransportCapacity":
        """
        Get the transport capacity based on the Trading post level.
        Args:
            ch (int): The Trading post level.
        Returns:
            TransportCapacity: The transport capacity.
        """
        match ch:
            case 22:
                return cls(3.0)
            case 23:
                return cls(3.5)
            case 24:
                return cls(4.0)
            case 25:
                return cls(10.0)
            case _:
                raise NotImplementedError(
                    "Transport capacity not implemented for this Trading post level"
                )

    def __str__(self):
        return super().__str__(explicit=True)

    def actual_amount(self, tax: TaxRate) -> ResourceAmount:
        """Calculate the actual amount of sending resources considering tax
        Receiver receives trans_cap
        Sender sends actual amount
        """
        return ResourceAmount(float(self) / (1 - tax.value))


@dataclass
class ResourceSet:
    food: ResourceAmount
    wood: ResourceAmount
    stone: ResourceAmount
    gold: ResourceAmount

    @classmethod
    def zero(cls):
        """Create a ResourceSet with all zero values."""
        return cls(ResourceAmount(0), ResourceAmount(0), ResourceAmount(0), ResourceAmount(0))

    @classmethod
    def from_list(cls, values):
        if len(values) != 4:
            raise ValueError(f"ResourceSet requires exactly 4 values, got {len(values)}: {values}")
        return cls(*values)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ResourceAmount(data["food"]),
            ResourceAmount(data["wood"]),
            ResourceAmount(data["stone"]),
            ResourceAmount(data["gold"]),
        )

    def __add__(self, other: "ResourceSet") -> "ResourceSet":
        return ResourceSet(
            ResourceAmount(self.food + other.food),
            ResourceAmount(self.wood + other.wood),
            ResourceAmount(self.stone + other.stone),
            ResourceAmount(self.gold + other.gold),
        )

    def __sub__(self, other: "ResourceSet", double_check=False) -> "ResourceSet":
        return ResourceSet(
            ResourceAmount(self.food.__sub__(other.food, double_check=double_check)),
            ResourceAmount(self.wood.__sub__(other.wood, double_check=double_check)),
            ResourceAmount(self.stone.__sub__(other.stone, double_check=double_check)),
            ResourceAmount(self.gold.__sub__(other.gold, double_check=double_check)),
        )

    def after_tax(self, tax_percent: TaxRate) -> "ResourceSet":
        return ResourceSet(
            self.food.after_tax(tax_percent),
            self.wood.after_tax(tax_percent),
            self.stone.after_tax(tax_percent),
            self.gold.after_tax(tax_percent),
        )

    def to_dict(self):
        return {
            "food": str(self.food),
            "wood": str(self.wood),
            "stone": str(self.stone),
            "gold": str(self.gold),
        }

    def __str__(self):
        return self.to_dict().__str__()

    def get_rss_amount(self, rss_type: ResourceType) -> ResourceAmount:
        rss_map = {
            ResourceType.FOOD: self.food,
            ResourceType.WOOD: self.wood,
            ResourceType.STONE: self.stone,
            ResourceType.GOLD: self.gold,
        }
        return rss_map[rss_type]
