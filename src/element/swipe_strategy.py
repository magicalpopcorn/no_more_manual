"""
Swipe Strategy Pattern Implementation

This module provides different swipe strategies that can be used across various UI screens.
The Strategy pattern allows for flexible swipe behavior that can be easily extended.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple

from src import logger

from .button import RectZone
from .pixel import P

SWIPE_DURATION = 800


class SwipeDirection(Enum):
    """Enumeration of swipe directions"""

    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


class SwipeStrategyType(Enum):
    """Enumeration of available swipe strategy types"""

    EDGE = "edge"
    CENTER = "center"


class SwipeStrategy(ABC):
    """Abstract base class for swipe strategies"""

    @abstractmethod
    def swipe(
        self, screen_area: RectZone, direction: SwipeDirection, duration: int = SWIPE_DURATION
    ) -> None:
        """
        Perform a swipe gesture within the given screen area.

        Args:
            screen_area: The rectangular area where the swipe should occur
            direction: The direction to swipe
            duration: Duration of the swipe in milliseconds
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

    def swipe(
        self, screen_area: RectZone, direction: SwipeDirection, duration: int = SWIPE_DURATION
    ) -> None:
        """Perform edge-to-edge swipe within the screen area"""
        start_point, end_point = self._calculate_swipe_points(screen_area, direction)

        logger.debug(f"Edge swipe {direction.value}: {start_point} -> {end_point}")
        start_point.swipe(end_point, duration)

    def _calculate_swipe_points(
        self, screen_area: RectZone, direction: SwipeDirection
    ) -> Tuple[P, P]:
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

        if direction == SwipeDirection.LEFT:
            # Swipe from right to left
            start = P(x2 - x_margin, center_y)
            end = P(x1 + x_margin, center_y)
        elif direction == SwipeDirection.RIGHT:
            # Swipe from left to right
            start = P(x1 + x_margin, center_y)
            end = P(x2 - x_margin, center_y)
        elif direction == SwipeDirection.UP:
            # Swipe from bottom to top
            start = P(center_x, y2 - y_margin)
            end = P(center_x, y1 + y_margin)
        elif direction == SwipeDirection.DOWN:
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

    def swipe(
        self, screen_area: RectZone, direction: SwipeDirection, duration: int = SWIPE_DURATION
    ) -> None:
        """Perform center-based swipe within the screen area"""
        start_point, end_point = self._calculate_swipe_points(screen_area, direction)

        logger.debug(f"Center swipe {direction.value}: {start_point} -> {end_point}")
        start_point.swipe(end_point, duration)

    def _calculate_swipe_points(
        self, screen_area: RectZone, direction: SwipeDirection
    ) -> Tuple[P, P]:
        """Calculate start and end points for the swipe based on direction"""
        center = screen_area.get_center_P()

        # Calculate swipe distance
        width = screen_area.p2.x - screen_area.p1.x
        height = screen_area.p2.y - screen_area.p1.y

        if direction in (SwipeDirection.LEFT, SwipeDirection.RIGHT):
            distance = int(width * self.swipe_distance_ratio / 2)
            if direction == SwipeDirection.LEFT:
                start = P(center.x + distance, center.y)
                end = P(center.x - distance, center.y)
            else:  # RIGHT
                start = P(center.x - distance, center.y)
                end = P(center.x + distance, center.y)
        else:  # UP or DOWN
            distance = int(height * self.swipe_distance_ratio / 2)
            if direction == SwipeDirection.UP:
                start = P(center.x, center.y + distance)
                end = P(center.x, center.y - distance)
            else:  # DOWN
                start = P(center.x, center.y - distance)
                end = P(center.x, center.y + distance)

        return start, end


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

    def swipe(
        self, screen_area: RectZone, direction: SwipeDirection, duration: int = SWIPE_DURATION
    ) -> None:
        """Perform swipe using the current strategy"""
        self.strategy.swipe(screen_area, direction, duration)

    def swipe_left(self, screen_area: RectZone, duration: int = SWIPE_DURATION) -> None:
        """Convenience method for swiping left"""
        self.swipe(screen_area, SwipeDirection.LEFT, duration)

    def swipe_right(self, screen_area: RectZone, duration: int = SWIPE_DURATION) -> None:
        """Convenience method for swiping right"""
        self.swipe(screen_area, SwipeDirection.RIGHT, duration)

    def swipe_up(self, screen_area: RectZone, duration: int = SWIPE_DURATION) -> None:
        """Convenience method for swiping up"""
        self.swipe(screen_area, SwipeDirection.UP, duration)

    def swipe_down(self, screen_area: RectZone, duration: int = SWIPE_DURATION) -> None:
        """Convenience method for swiping down"""
        self.swipe(screen_area, SwipeDirection.DOWN, duration)
