from dataclasses import dataclass
import re


class ResourceAmount:
    """
    Stores resource values in millions (float).
    Supports parsing from strings like '100.0M' or '1.4B',
    conversion to int, and arithmetic operations.
    """

    MULTIPLIERS = {"M": 1, "B": 1000}

    def __init__(self, value: float | str):
        if isinstance(value, str):
            value = self.from_str(value).value
        elif not isinstance(value, (int, float)):
            raise TypeError(
                f"ResourceAmount must be initialized with a number or string, got {type(value)}"
            )
        self.value = value  # always in millions

    @classmethod
    def from_str(cls, s: str):
        """
        Parse a resource string like '100.0M' or '1.4B' to ResourceAmount.
        """
        match = re.match(r"([\d.,]+)\s*([MB])", s.strip().upper())
        if not match:
            raise ValueError(f"Invalid resource format: {s}")
        num, unit = match.groups()
        num = float(num.replace(",", ""))
        return cls(num * cls.MULTIPLIERS[unit])

    def to_int(self):
        """
        Convert to integer (units).
        """
        return int(self.value * 1_000_000)

    def __add__(self, other):
        if not isinstance(other, ResourceAmount):
            return NotImplemented
        return ResourceAmount(self.value + other.value)

    def __sub__(self, other):
        if not isinstance(other, ResourceAmount):
            return NotImplemented
        result = self.value - other.value
        # OCR bug: if result < 0 and self.value starts with 1, it's likely a misread 7
        if result < 0 and str(int(self.value))[0] == "1":
            # Replace first digit with 7 and recalculate
            corrected_str = "7" + str(int(self.value))[1:]
            try:
                corrected_value = float(corrected_str + str(self.value)[len(corrected_str) :])
                self.value = corrected_value  # update self.value
            except Exception:
                pass  # fallback to original result if conversion fails
        return ResourceAmount(self.value - other.value)

    def after_tax(self, tax_percent: float) -> "ResourceAmount":
        """
        Returns a new ResourceAmount after tax reduction.
        Args:
            tax_percent (float): Tax percentage (e.g., 10 for 10%).
        Returns:
            ResourceAmount: Value after tax reduction.
        """
        return ResourceAmount(self.value * (1 - tax_percent / 100))

    def __str__(self):
        if self.value >= 1000:
            return f"{self.value / 1000:.1f}B"
        return f"{self.value:.1f}M"

    def __repr__(self):
        return f"ResourceAmount({self.value:.1f}M)"


@dataclass
class ResourceSet:
    food: ResourceAmount
    wood: ResourceAmount
    stone: ResourceAmount
    gold: ResourceAmount

    @classmethod
    def zero(cls):
        """Create a ResourceSet with all zero values."""
        return cls(
            ResourceAmount(0),
            ResourceAmount(0),
            ResourceAmount(0),
            ResourceAmount(0)
        )

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
            self.food + other.food,
            self.wood + other.wood,
            self.stone + other.stone,
            self.gold + other.gold,
        )

    def __sub__(self, other: "ResourceSet") -> "ResourceSet":
        return ResourceSet(
            self.food - other.food,
            self.wood - other.wood,
            self.stone - other.stone,
            self.gold - other.gold,
        )

    def after_tax(self, tax_percent: float) -> "ResourceSet":
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
