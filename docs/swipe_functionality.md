# Swipe Functionality Documentation

## Overview

The swipe functionality in ROK Macro Automation is implemented using the Strategy pattern, making it flexible and reusable across different UI screens. This allows for consistent swipe behavior while supporting different swipe strategies based on the specific needs of each screen.

## Architecture

### Strategy Pattern Components

1. **SwipeStrategy (Abstract Base Class)**: Defines the interface for swipe strategies
2. **EdgeSwipeStrategy**: Performs edge-to-edge swipes across the screen area
3. **CenterSwipeStrategy**: Performs shorter swipes from the center area
4. **SwipeController**: Manages and executes swipe strategies
5. **SwipeMixin**: Provides swipe functionality to menu classes

### Key Classes

#### Direction Enum
```python
from src.element import Direction

# Available directions
Direction.LEFT    # Swipe from right to left
Direction.RIGHT   # Swipe from left to right
Direction.UP      # Swipe from bottom to top
Direction.DOWN    # Swipe from top to bottom
```

#### SwipeStrategyType Enum
```python
from src.element import SwipeStrategyType

# Available strategy types
SwipeStrategyType.EDGE     # Edge-to-edge swipe strategy
SwipeStrategyType.CENTER   # Center-based swipe strategy
```

#### EdgeSwipeStrategy
Best for: Scrolling through lists, navigating between screens
- Swipes from one edge of the screen area to the opposite edge
- Configurable margin ratio (default: 0.1 = 10% margin from edges)

#### CenterSwipeStrategy
Best for: Fine-grained scrolling, precise navigation
- Performs shorter swipes starting from the center
- Configurable swipe distance ratio (default: 0.3 = 30% of screen area)

## Automatic Duration Calculation

The swipe system automatically calculates the optimal duration for each swipe gesture based on the distance between start and end points. This happens transparently at the `P` (pixel) level, so you don't need to worry about duration parameters in the high-level swipe methods.

**Benefits:**
- **Longer swipes** get proportionally longer durations for smooth movement
- **Shorter swipes** complete quickly for responsive UI interactions
- **Consistent speed** across different swipe distances
- **Simplified API** - no duration parameters needed at the strategy level

The calculation uses the formula implemented in `P.swipe()`:
```python
distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
actual_duration = base_duration * (distance / 500) + base_duration
final_duration = max(base_duration, actual_duration)  # Ensure minimum duration
```

Where `base_duration` defaults to 500ms and is handled internally.

## Usage

### Basic Usage with Existing Menu Classes

```python
from src.ui.menu_main import MenuHomeResources
from src.element import Direction, SwipeStrategyType

# Open the home resources screen first
MenuMain.open_home_resources()

# Setup swipe strategy using enum (recommended)
MenuHomeResources.set_swipe_strategy(SwipeStrategyType.EDGE, margin_ratio=0.15)

# Or using string for backward compatibility
MenuHomeResources.set_swipe_strategy("center", swipe_distance_ratio=0.3)

# Use built-in convenience methods
MenuHomeResources.swipe_left()
MenuHomeResources.swipe_right()
MenuHomeResources.swipe_up()
MenuHomeResources.swipe_down()

# Or use the general swipe method
# Duration is automatically calculated based on swipe distance
MenuHomeResources.swipe_screen(Direction.LEFT)
```

### Creating a New Swipeable Menu Class

```python
from src.element import Button, P, RectZone, SwipeStrategyType
from src.ui.swipeable_mixin import SwipeMixin
from src.ui.base_menu import _Menu

class MyNewMenu(_Menu, SwipeMixin):
    # Define UI elements
    BTN_SOME_BUTTON = Button("Some_Button", P(100, 100), P(200, 150))

    # REQUIRED: Define the swipeable area
    SWIPE_AREA = RectZone("My_Menu_Swipe_Area", P(50, 100), P(1850, 950))

    @classmethod
    def setup_swipe_strategy(cls):
        """Optional: Setup custom swipe strategy"""
        # Use edge strategy with custom margin (recommended enum usage)
        cls.set_swipe_strategy(SwipeStrategyType.EDGE, margin_ratio=0.2)

        # Or use center strategy
        # cls.set_swipe_strategy(SwipeStrategyType.CENTER, swipe_distance_ratio=0.4)

        # String usage still supported for backward compatibility
        # cls.set_swipe_strategy("edge", margin_ratio=0.2)

    @classmethod
    def is_open(cls):
        # Implement your menu detection logic
        return True
```

### Advanced Usage: Custom Swipe Strategies

```python
from src.element import EdgeSwipeStrategy, CenterSwipeStrategy, SwipeController

# Create custom strategies
edge_strategy = EdgeSwipeStrategy(margin_ratio=0.05)  # Very small margins
center_strategy = CenterSwipeStrategy(swipe_distance_ratio=0.5)  # Longer swipes

# Apply to a menu class
MenuHomeResources.set_swipe_strategy("edge", margin_ratio=0.05)
MenuHomeResources.set_swipe_strategy("center", swipe_distance_ratio=0.5)
```

### Scroll to Find Elements

```python
def find_specific_resource():
    # Your logic to check if the target resource is visible
    return cv.match_region_with_template(target_button, target_image)

# Scroll until the resource is found
found = MenuHomeResources.scroll_to_find_element(
    target_check_func=find_specific_resource,
    direction=SwipeDirection.DOWN,
    max_attempts=5,
    duration=400
)

if found:
    print("Resource found!")
else:
    print("Resource not found after scrolling")
```

## Implementation Examples

### Home Resources Screen
```python
# Already implemented in menu_main.py
class MenuHomeResources(SwipeMixin):
    SWIPE_AREA = RectZone("Home_Resources_Swipe_Area", P(100, 150), P(1800, 900))

    @classmethod
    def setup_swipe_strategy(cls):
        cls.set_swipe_strategy("edge", margin_ratio=0.15)
```

### Items Menu (Example)
```python
class MenuItems(_Menu, SwipeMixin):
    # Define the grid area where items are displayed
    SWIPE_AREA = RectZone("Items_Grid_Area", P(280, 240), P(1200, 800))

    @classmethod
    def setup_swipe_strategy(cls):
        # Use center strategy for precise item navigation
        cls.set_swipe_strategy("center", swipe_distance_ratio=0.3)

    @classmethod
    def scroll_to_item(cls, item_name):
        def check_item():
            return cls.find_item_by_name(item_name) is not None

        return cls.scroll_to_find_element(
            target_check_func=check_item,
            direction=SwipeDirection.DOWN
        )
```

## Best Practices

1. **Define Appropriate Swipe Areas**: Make sure `SWIPE_AREA` covers the scrollable content but avoids UI elements like buttons or headers.

2. **Choose the Right Strategy**:
   - Use `EdgeSwipeStrategy` for general scrolling and navigation
   - Use `CenterSwipeStrategy` for precise, controlled movements

3. **Adjust Parameters**:
   - Increase `margin_ratio` for EdgeSwipeStrategy if swipes are too close to screen edges
   - Adjust `swipe_distance_ratio` for CenterSwipeStrategy to control swipe length

4. **Handle Timing**: Add appropriate delays between swipes to allow UI animations to complete

5. **Error Handling**: Use `scroll_to_find_element` for robust element searching with automatic retries

## Testing

Use the provided test script to verify swipe functionality:

```bash
python tools/test_swipe.py
```

Make sure the game is running and the Home Resources screen is open before running the test.

## Troubleshooting

1. **Swipes not working**: Check that ADB connection is established and the emulator is responsive
2. **Swipes too fast/slow**: Adjust the `duration` parameter
3. **Swipes not reaching target**: Adjust the strategy parameters (margin_ratio, swipe_distance_ratio)
4. **Element not found**: Ensure the `SWIPE_AREA` covers the correct screen region
