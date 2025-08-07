"""
Swipe Menu Mixin

This module provides a mixin class that adds swipe functionality to menu classes.
It can be used by any menu class that needs scrolling or swipe gestures.
"""

from abc import ABC
from typing import Optional

from src import logger
from src.element import (
    CenterSwipeStrategy,
    EdgeSwipeStrategy,
    RectZone,
    SwipeController,
    SwipeDirection,
    SwipeStrategyType,
)


class SwipeMixin(ABC):
    """
    Mixin class that provides swipe functionality to menu classes.

    Classes that inherit from this mixin should define:
    - SWIPE_AREA: RectZone defining the area where swipes should occur
    - _swipe_controller: SwipeController instance (optional, defaults to EdgeSwipeStrategy)
    """

    # These should be defined by the inheriting class
    SWIPE_AREA: Optional[RectZone] = None
    _swipe_controller: Optional[SwipeController] = None

    @classmethod
    def _get_swipe_controller(cls) -> SwipeController:
        """Get the swipe controller, creating a default one if not defined"""
        if cls._swipe_controller is None:
            cls._swipe_controller = SwipeController(EdgeSwipeStrategy())
        return cls._swipe_controller

    @classmethod
    def _get_swipe_area(cls) -> RectZone:
        """Get the swipe area, raising an error if not defined"""
        if cls.SWIPE_AREA is None:
            raise NotImplementedError(
                f"{cls.__name__} must define SWIPE_AREA to use swipe functionality"
            )
        return cls.SWIPE_AREA

    @classmethod
    def set_swipe_strategy(
        cls, strategy_type: SwipeStrategyType = SwipeStrategyType.EDGE, **kwargs
    ):
        """
        Set the swipe strategy for this menu.

        Args:
            strategy_type: Type of strategy (SwipeStrategyType enum or string "edge"/"center")
            **kwargs: Additional arguments for the strategy constructor
        """
        if strategy_type == SwipeStrategyType.EDGE:
            strategy = EdgeSwipeStrategy(**kwargs)
        elif strategy_type == SwipeStrategyType.CENTER:
            strategy = CenterSwipeStrategy(**kwargs)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

        cls._swipe_controller = SwipeController(strategy)
        logger.debug(f"{cls.__name__} swipe strategy set to {strategy_type.value}")

    @classmethod
    def swipe_screen(cls, direction: SwipeDirection, duration: int = 400):
        """
        Swipe the screen in the specified direction.

        Args:
            direction: SwipeDirection enum (LEFT, RIGHT, UP, DOWN)
            duration: Duration of the swipe gesture in milliseconds
        """
        swipe_area = cls._get_swipe_area()
        swipe_controller = cls._get_swipe_controller()

        logger.info(f"{cls.__name__}: Swiping {direction.value}")
        swipe_controller.swipe(swipe_area, direction, duration)

    @classmethod
    def swipe_left(cls, duration: int = 400):
        """Convenience method to swipe left"""
        cls.swipe_screen(SwipeDirection.LEFT, duration)

    @classmethod
    def swipe_right(cls, duration: int = 400):
        """Convenience method to swipe right"""
        cls.swipe_screen(SwipeDirection.RIGHT, duration)

    @classmethod
    def swipe_up(cls, duration: int = 400):
        """Convenience method to swipe up"""
        cls.swipe_screen(SwipeDirection.UP, duration)

    @classmethod
    def swipe_down(cls, duration: int = 400):
        """Convenience method to swipe down"""
        cls.swipe_screen(SwipeDirection.DOWN, duration)

    @classmethod
    def scroll_to_find_element(
        cls,
        target_check_func,
        direction: SwipeDirection,
        max_attempts: int = 5,
        duration: int = 400,
    ) -> bool:
        """
        Scroll in the specified direction until the target element is found.

        Args:
            target_check_func: Function that returns True when target element is found
            direction: Direction to scroll
            max_attempts: Maximum number of scroll attempts
            duration: Duration of each swipe

        Returns:
            True if element was found, False otherwise
        """
        for attempt in range(max_attempts):
            if target_check_func():
                logger.info(f"{cls.__name__}: Target element found after {attempt} swipes")
                return True

            logger.debug(f"{cls.__name__}: Attempt {attempt + 1}: Swiping {direction.value}")
            cls.swipe_screen(direction, duration)

        logger.warning(f"{cls.__name__}: Target element not found after {max_attempts} attempts")
        return False
