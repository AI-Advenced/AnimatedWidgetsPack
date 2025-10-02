# API Reference

## Core Classes

### AnimatedWidget

Abstract base class for all animated widgets.

```python
class AnimatedWidget(ABC):
    def __init__(self, config: Optional[WidgetConfig] = None)
```

#### Methods

- `render(parent_widget)` - Abstract method for widget rendering
- `update_appearance()` - Abstract method for updating widget appearance
- `bind_callback(event_type: str, callback: Callable)` - Bind event callback
- `trigger_callback(event_type: str, *args, **kwargs)` - Trigger event callbacks
- `animate_property(property_name, start_value, end_value, duration, easing_function)` - Animate property
- `set_state(new_state: str)` - Change widget state
- `get_state() -> str` - Get current widget state
- `enable()` - Enable the widget
- `disable()` - Disable the widget
- `stop_all_animations()` - Stop all running animations
- `is_animating() -> bool` - Check if animations are running

#### Events

- `click` - Widget was clicked
- `hover_enter` - Mouse entered widget
- `hover_leave` - Mouse left widget
- `value_changed` - Widget value changed
- `state_changed` - Widget state changed

### WidgetConfig

Configuration dataclass for widget appearance and behavior.

```python
@dataclass
class WidgetConfig:
    width: int = 120
    height: int = 40
    background_color: str = "#3498db"
    text_color: str = "#ffffff"
    border_radius: int = 8
    border_width: int = 0
    border_color: str = "#2c3e50"
    font_family: str = "Arial"
    font_size: int = 12
    animation_duration: float = 0.3
    enable_animations: bool = True
```

## Button Classes

### AnimatedButton

Interactive button with hover, click and animation effects.

```python
class AnimatedButton(AnimatedWidget):
    def __init__(self, text: str = "Button", 
                 config: Optional[WidgetConfig] = None,
                 style: Optional[ButtonStyle] = None)
```

#### Methods

- `render(parent_widget, framework: str = "tkinter")` - Render button in GUI framework
- `on_click(callback: Callable)` - Set click callback (returns self for chaining)
- `set_text(text: str)` - Change button text
- `set_colors(normal=None, hover=None, pressed=None)` - Update button colors
- `pulse_animation(duration=1.0, scale_factor=1.1)` - Create pulse effect
- `flash_animation(flash_color="#ffffff", duration=0.3)` - Create flash effect
- `bounce_animation(duration=0.6)` - Create bounce effect

### ButtonStyle

Styling configuration for buttons.

```python
@dataclass
class ButtonStyle:
    normal_color: str = "#3498db"
    hover_color: str = "#2980b9"
    pressed_color: str = "#21618c" 
    disabled_color: str = "#95a5a6"
    text: str = "Button"
    icon: Optional[str] = None
    shadow_enabled: bool = True
    shadow_color: str = "#2c3e50"
    shadow_offset: tuple = (0, 2)
    hover_lift: float = 2.0
    click_scale: float = 0.95
```

## Animation Classes

### AnimationManager

Central manager for widget animations.

```python
class AnimationManager:
    def __init__(self)
```

#### Methods

- `animate(animation_id, start_value, end_value, update_callback, config, completion_callback)` - Start animation
- `stop_animation(animation_id: str)` - Stop specific animation
- `stop_all_animations()` - Stop all animations
- `is_animating(animation_id: str) -> bool` - Check if animation is running
- `get_active_count() -> int` - Get number of active animations

### AnimationConfig

Configuration for animations.

```python
@dataclass
class AnimationConfig:
    duration: float = 0.3
    easing: EasingType = EasingType.EASE_OUT_CUBIC
    fps: int = 60
    auto_reverse: bool = False
    repeat_count: int = 1
    delay: float = 0.0
```

### EasingType

Enumeration of available easing functions.

```python
class EasingType(Enum):
    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    BOUNCE_OUT = "bounce_out"
    ELASTIC_OUT = "elastic_out"
```

## Utility Classes

### ColorUtils

Utilities for color manipulation.

#### Static Methods

- `hex_to_rgb(hex_color: str) -> Tuple[int, int, int]` - Convert hex to RGB
- `rgb_to_hex(r: int, g: int, b: int) -> str` - Convert RGB to hex
- `parse_color(color_input) -> Color` - Parse various color formats
- `lighten_color(color, factor=0.2) -> Color` - Lighten a color
- `darken_color(color, factor=0.2) -> Color` - Darken a color
- `interpolate_colors(color1, color2, factor) -> Color` - Interpolate between colors
- `get_contrast_color(color) -> Color` - Get contrasting color (black/white)

### Color

Color representation with RGBA values.

```python
@dataclass
class Color:
    r: int
    g: int
    b: int
    a: float = 1.0
```

#### Methods

- `to_hex() -> str` - Convert to hex format
- `to_rgba_string() -> str` - Convert to rgba() string
- `to_rgb_tuple() -> Tuple[int, int, int]` - Convert to RGB tuple
- `to_rgba_tuple() -> Tuple[int, int, int, float]` - Convert to RGBA tuple

### GeometryUtils

Utilities for geometric calculations.

#### Static Methods

- `distance(p1: Point, p2: Point) -> float` - Distance between points
- `clamp(value, min_value, max_value) -> float` - Clamp value to range
- `lerp(start, end, factor) -> float` - Linear interpolation
- `map_range(value, from_min, from_max, to_min, to_max) -> float` - Map value between ranges
- `round_rectangle_path(rect, radius) -> List[Point]` - Generate rounded rectangle points
- `calculate_bezier_point(t, p0, p1, p2, p3) -> Point` - Calculate Bezier curve point
- `normalize_angle(angle) -> float` - Normalize angle to [0, 2π)
- `degrees_to_radians(degrees) -> float` - Convert degrees to radians
- `radians_to_degrees(radians) -> float` - Convert radians to degrees

### Point

2D point representation.

```python
@dataclass
class Point:
    x: float
    y: float
```

#### Methods

- `distance_to(other: Point) -> float` - Distance to another point
- `translate(dx: float, dy: float) -> Point` - Create translated point

### Rectangle

Rectangle representation.

```python
@dataclass  
class Rectangle:
    x: float
    y: float
    width: float
    height: float
```

#### Methods

- `contains_point(point: Point) -> bool` - Check if point is inside
- `center() -> Point` - Get center point
- `area() -> float` - Calculate area
- `intersects(other: Rectangle) -> bool` - Check intersection with another rectangle

## Color Palettes

### ColorPalettes

Predefined color palettes for quick styling.

```python
class ColorPalettes:
    MATERIAL_DESIGN = {
        'blue': '#2196F3',
        'red': '#F44336',
        'green': '#4CAF50',
        # ... more colors
    }
    
    FLAT_UI = {
        'turquoise': '#1ABC9C',
        'emerland': '#2ECC71',
        # ... more colors
    }
    
    BOOTSTRAP = {
        'primary': '#007bff',
        'secondary': '#6c757d',
        # ... more colors  
    }
```

## Framework Integration

### Supported Frameworks

- **tkinter** - Built-in Python GUI toolkit
- **pyqt5** - Cross-platform GUI toolkit (requires PyQt5)
- **pyqt6** - Latest PyQt version (requires PyQt6)

### Framework-Specific Notes

#### Tkinter
- Returns native `tk.Button` objects
- Automatic event binding
- Color updates via `configure()`

#### PyQt5/PyQt6
- Returns native `QPushButton` objects  
- CSS-based styling
- Signal/slot event system

## Error Handling

### Common Exceptions

- `ValueError` - Unsupported framework or invalid parameters
- `ImportError` - Missing GUI framework dependencies
- `AttributeError` - Invalid widget state or property

### Best Practices

- Always check framework availability before rendering
- Use try/except blocks for GUI operations
- Stop animations before destroying widgets
- Handle callback exceptions gracefully