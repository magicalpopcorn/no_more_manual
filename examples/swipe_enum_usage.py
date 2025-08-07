#!/usr/bin/env python3
"""
Example showing how to use the SwipeStrategyType enum with the swipeable mixin.
"""

from src.element import SwipeDirection, SwipeStrategyType
from src.ui.menu_main import MenuHomeResources


def demonstrate_enum_usage():
    """Demonstrate different ways to use the SwipeStrategyType enum"""

    # Method 1: Using the enum directly (recommended)
    MenuHomeResources.set_swipe_strategy(SwipeStrategyType.EDGE, margin_ratio=0.15)
    print(f"Strategy set to: {SwipeStrategyType.EDGE.value}")

    # Method 3: Using enum with different parameters
    MenuHomeResources.set_swipe_strategy(SwipeStrategyType.CENTER, swipe_distance_ratio=0.3)
    print(f"Strategy set to: {SwipeStrategyType.CENTER.value}")

    # Demonstrate swipe directions
    print("\nAvailable swipe directions:")
    for direction in SwipeDirection:
        print(f"  - {direction.value}")

    # Demonstrate strategy types
    print("\nAvailable strategy types:")
    for strategy in SwipeStrategyType:
        print(f"  - {strategy.value}")


def demonstrate_swipe_usage():
    """Demonstrate how to use swipe functionality"""

    # Setup the strategy first
    MenuHomeResources.set_swipe_strategy(SwipeStrategyType.EDGE, margin_ratio=0.1)

    # Open the home resources menu (this would be done in actual automation)
    # MenuHomeResources.open()

    # Example swipe operations (commented out to avoid actual execution)
    # MenuHomeResources.swipe_right()  # Swipe to the right
    # MenuHomeResources.swipe_left()   # Swipe to the left
    # MenuHomeResources.swipe_screen(SwipeDirection.UP, duration=500)  # Custom swipe

    print("Swipe operations would be executed here in actual automation")


if __name__ == "__main__":
    print("=== SwipeStrategyType Enum Usage Examples ===\n")

    demonstrate_enum_usage()
    print("\n" + "=" * 50 + "\n")
    demonstrate_swipe_usage()

    print("\n=== Done ===")
