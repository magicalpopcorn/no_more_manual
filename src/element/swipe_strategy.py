"""
Swipe Strategy Pattern Implementation

This module provides different swipe strategies that can be used across various UI screens.
The Strategy pattern allows for flexible swipe behavior that can be easily extended.
"""

import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple

from src import logger

from .button import RectZone
from .pixel import P


class Direction(Enum):
    """Enumeration of movement directions"""

    LEFT = "L"
    RIGHT = "R"
    UP = "U"
    DOWN = "D"


class SwipeStrategyType(Enum):
    """Enumeration of available swipe strategy types"""

    EDGE = "edge"
    CENTER = "center"
    ZONE = "zone"


class SwipeStrategy(ABC):
    """Abstract base class for swipe strategies"""

    @abstractmethod
    def swipe(self, screen_area: RectZone, direction: Direction) -> None:
        """
        Perform a swipe gesture within the given screen area.

        Args:
            screen_area: The rectangular area where the swipe should occur
            direction: The direction to swipe
        """
        pass


class EdgeSwipeStrategy(SwipeStrategy):
    """
    Swipe strategy that performs swipes from edge to edge of the screen area.
    This is useful for scrolling through lists or switching between screens.
    """

    def __init__(self, margin_ratio: float = 0.1):
        """
        Initialize edge swipe strategy.

        Args:
            margin_ratio: Ratio of the screen area to use as margin from edges (0.0 to 0.5)
        """
        self.margin_ratio = max(0.0, min(0.5, margin_ratio))

    def swipe(self, screen_area: RectZone, direction: Direction) -> None:
        """Perform edge-to-edge swipe within the screen area"""
        start_point, end_point = self._calculate_swipe_points(screen_area, direction)

        logger.debug(f"Edge swipe {direction.value}: {start_point} -> {end_point}")
        start_point.swipe(end_point)

    def _calculate_swipe_points(self, screen_area: RectZone, direction: Direction) -> Tuple[P, P]:
        """Calculate start and end points for the swipe based on direction"""
        x1, y1 = screen_area.p1.x, screen_area.p1.y
        x2, y2 = screen_area.p2.x, screen_area.p2.y

        # Calculate margins
        width = x2 - x1
        height = y2 - y1
        x_margin = int(width * self.margin_ratio)
        y_margin = int(height * self.margin_ratio)

        # Calculate center coordinates
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        if direction == Direction.LEFT:
            # Swipe from right to left
            start = P(x2 - x_margin, center_y)
            end = P(x1 + x_margin, center_y)
        elif direction == Direction.RIGHT:
            # Swipe from left to right
            start = P(x1 + x_margin, center_y)
            end = P(x2 - x_margin, center_y)
        elif direction == Direction.UP:
            # Swipe from bottom to top
            start = P(center_x, y2 - y_margin)
            end = P(center_x, y1 + y_margin)
        elif direction == Direction.DOWN:
            # Swipe from top to bottom
            start = P(center_x, y1 + y_margin)
            end = P(center_x, y2 - y_margin)
        else:
            raise ValueError(f"Unsupported swipe direction: {direction}")

        return start, end


class CenterSwipeStrategy(SwipeStrategy):
    """
    Swipe strategy that performs shorter swipes from the center area.
    This is useful for fine-grained scrolling or when you need more controlled movement.
    """

    def __init__(self, swipe_distance_ratio: float = 0.3):
        """
        Initialize center swipe strategy.

        Args:
            swipe_distance_ratio: Ratio of the screen area to use as swipe distance (0.1 to 0.8)
        """
        self.swipe_distance_ratio = max(0.1, min(0.8, swipe_distance_ratio))

    def swipe(self, screen_area: RectZone, direction: Direction) -> None:
        """Perform center-based swipe within the screen area"""
        start_point, end_point = self._calculate_swipe_points(screen_area, direction)

        logger.debug(f"Center swipe {direction.value}: {start_point} -> {end_point}")
        start_point.swipe(end_point)

    def _calculate_swipe_points(self, screen_area: RectZone, direction: Direction) -> Tuple[P, P]:
        """Calculate start and end points for the swipe based on direction"""
        center = screen_area.get_center_P()

        # Calculate swipe distance
        width = screen_area.p2.x - screen_area.p1.x
        height = screen_area.p2.y - screen_area.p1.y

        if direction in (Direction.LEFT, Direction.RIGHT):
            distance = int(width * self.swipe_distance_ratio / 2)
            if direction == Direction.LEFT:
                start = P(center.x + distance, center.y)
                end = P(center.x - distance, center.y)
            else:  # RIGHT
                start = P(center.x - distance, center.y)
                end = P(center.x + distance, center.y)
        else:  # UP or DOWN
            distance = int(height * self.swipe_distance_ratio / 2)
            if direction == Direction.UP:
                start = P(center.x, center.y + distance)
                end = P(center.x, center.y - distance)
            else:  # DOWN
                start = P(center.x, center.y - distance)
                end = P(center.x, center.y + distance)

        return start, end


class ZoneSwipeStrategy(SwipeStrategy):
    """
    Swipe strategy that creates zones at edges and swipes from random points
    in one zone to random points in another zone for more human-like behavior.
    """

    def __init__(self, zone_width: int = 40, variation_range: int = 15):
        """
        Initialize zone swipe strategy.

        Args:
            zone_width: Width of the zones in pixels (10-50 recommended)
            variation_range: Pixel variation range for natural movement (5-25 recommended)
        """
        self.zone_width = max(10, min(50, zone_width))
        self.variation_range = max(5, min(25, variation_range))

    def swipe(self, screen_area: RectZone, direction: Direction) -> None:
        """Perform zone-to-zone swipe within the screen area"""
        start_point, end_point = self._calculate_swipe_points(screen_area, direction)

        logger.debug(f"Zone swipe {direction.value}: {start_point} -> {end_point}")
        start_point.swipe(end_point)

    def _calculate_swipe_points(self, screen_area: RectZone, direction: Direction) -> Tuple[P, P]:
        """Calculate start and end points with target based on start position for natural swipe"""
        x1, y1 = screen_area.p1.x, screen_area.p1.y
        x2, y2 = screen_area.p2.x, screen_area.p2.y

        if direction == Direction.LEFT:
            # Start from right zone, end in left zone
            start_zone = self._create_right_zone(x1, y1, x2, y2)
            start_point = self._get_random_point_in_zone(start_zone)

            # End point: x in left zone, y based on start with variation
            end_x = random.randint(x1, x1 + self.zone_width)
            end_y = max(
                y1,
                min(
                    y2, start_point.y + random.randint(-self.variation_range, self.variation_range)
                ),
            )
            end_point = P(end_x, end_y)

        elif direction == Direction.RIGHT:
            # Start from left zone, end in right zone
            start_zone = self._create_left_zone(x1, y1, x2, y2)
            start_point = self._get_random_point_in_zone(start_zone)

            # End point: x in right zone, y based on start with variation
            end_x = random.randint(x2 - self.zone_width, x2)
            end_y = max(
                y1,
                min(
                    y2, start_point.y + random.randint(-self.variation_range, self.variation_range)
                ),
            )
            end_point = P(end_x, end_y)

        elif direction == Direction.UP:
            # Start from bottom zone, end in top zone
            start_zone = self._create_bottom_zone(x1, y1, x2, y2)
            start_point = self._get_random_point_in_zone(start_zone)

            # End point: y in top zone, x based on start with variation
            end_y = random.randint(y1, y1 + self.zone_width)
            end_x = max(
                x1,
                min(
                    x2, start_point.x + random.randint(-self.variation_range, self.variation_range)
                ),
            )
            end_point = P(end_x, end_y)

        elif direction == Direction.DOWN:
            # Start from top zone, end in bottom zone
            start_zone = self._create_top_zone(x1, y1, x2, y2)
            start_point = self._get_random_point_in_zone(start_zone)

            # End point: y in bottom zone, x based on start with variation
            end_y = random.randint(y2 - self.zone_width, y2)
            end_x = max(
                x1,
                min(
                    x2, start_point.x + random.randint(-self.variation_range, self.variation_range)
                ),
            )
            end_point = P(end_x, end_y)

        else:
            raise ValueError(f"Unsupported swipe direction: {direction}")

        return start_point, end_point

    def _create_left_zone(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int, int, int]:
        """Create left edge zone"""
        return (x1, y1, x1 + self.zone_width, y2)

    def _create_right_zone(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int, int, int]:
        """Create right edge zone"""
        return (x2 - self.zone_width, y1, x2, y2)

    def _create_top_zone(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int, int, int]:
        """Create top edge zone"""
        return (x1, y1, x2, y1 + self.zone_width)

    def _create_bottom_zone(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int, int, int]:
        """Create bottom edge zone"""
        return (x1, y2 - self.zone_width, x2, y2)

    def _get_random_point_in_zone(self, zone: Tuple[int, int, int, int]) -> P:
        """Get a random point within the specified zone"""
        x1, y1, x2, y2 = zone
        random_x = random.randint(x1, x2)
        random_y = random.randint(y1, y2)
        return P(random_x, random_y)


class SwipeController:
    """
    Controller class that manages swipe strategies.
    This provides a unified interface for performing swipes with different strategies.
    """

    def __init__(self, strategy: Optional[SwipeStrategy] = None):
        """
        Initialize swipe controller with a strategy.

        Args:
            strategy: The swipe strategy to use. Defaults to EdgeSwipeStrategy.
        """
        self.strategy = strategy or EdgeSwipeStrategy()

    def set_strategy(self, strategy: SwipeStrategy) -> None:
        """Change the swipe strategy"""
        self.strategy = strategy

    def swipe(self, screen_area: RectZone, direction: Direction) -> None:
        """Perform swipe using the current strategy"""
        self.strategy.swipe(screen_area, direction)

    def swipe_left(self, screen_area: RectZone) -> None:
        """Convenience method for swiping left"""
        self.swipe(screen_area, Direction.LEFT)

    def swipe_right(self, screen_area: RectZone) -> None:
        """Convenience method for swiping right"""
        self.swipe(screen_area, Direction.RIGHT)

    def swipe_up(self, screen_area: RectZone) -> None:
        """Convenience method for swiping up"""
        self.swipe(screen_area, Direction.UP)

    def swipe_down(self, screen_area: RectZone) -> None:
        """Convenience method for swiping down"""
        self.swipe(screen_area, Direction.DOWN)
