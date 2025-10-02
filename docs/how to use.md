# AnimatedWidgetsPack Documentation

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Widget Classes](#widget-classes)
5. [Animation System](#animation-system)
6. [Utility Functions](#utility-functions)
7. [Framework Integration](#framework-integration)
8. [API Reference](#api-reference)
9. [Examples](#examples)
10. [Best Practices](#best-practices)

## Installation

### Basic Installation

```bash
pip install animated-widgets-pack
```

### With GUI Framework Support

```bash
# With PyQt5 support
pip install animated-widgets-pack[gui]

# Development installation
pip install animated-widgets-pack[dev,gui]
```

### From Source

```bash
git clone https://github.com/yourusername/animated-widgets-pack.git
cd AnimatedWidgetsPack
pip install -e .
```

## Quick Start

### Basic Animated Button

```python
import tkinter as tk
from animated_widgets_pack import AnimatedButton, WidgetConfig, ButtonStyle

# Create main window
root = tk.Tk()
root.title("Animated Button Demo")
root.geometry("300x200")

# Configure button
config = WidgetConfig(
    width=180, 
    height=50,
    border_radius=10,
    animation_duration=0.3
)

style = ButtonStyle(
    normal_color="#3498db",
    hover_color="#2980b9", 
    pressed_color="#21618c"
)

# Create and render button
button = AnimatedButton("Click Me! 🚀", config=config, style=style)
button_widget = button.render(root, "tkinter")
button_widget.pack(expand=True)

# Add click handler
def on_click():
    print("Button clicked with animation!")
    button.pulse_animation(duration=0.8, scale_factor=1.3)

button.on_click(on_click)

root.mainloop()
```

## Core Components

### AnimatedWidget Base Class

All animated widgets inherit from `AnimatedWidget`, which provides:

- **State Management**: normal, hover, pressed, disabled states
- **Animation Framework**: Property animations with easing functions
- **Event System**: Callback binding and triggering
- **Framework Integration**: Support for Tkinter, PyQt5/PyQt6

```python
from animated_widgets_pack import AnimatedWidget, WidgetConfig

class CustomWidget(AnimatedWidget):
    def __init__(self, config=None):
        super().__init__(config)
        self.custom_property = 0
    
    def render(self, parent_widget):
        # Implementation specific to GUI framework
        pass
    
    def update_appearance(self):
        # Update widget visual appearance
        pass
```

### WidgetConfig

Configuration class for widget appearance and behavior:

```python
from animated_widgets_pack import WidgetConfig

config = WidgetConfig(
    width=120,                    # Widget width in pixels
    height=40,                    # Widget height in pixels
    background_color="#3498db",   # Background color
    text_color="#ffffff",         # Text color
    border_radius=8,              # Border radius
    border_width=0,               # Border width
    border_color="#2c3e50",       # Border color
    font_family="Arial",          # Font family
    font_size=12,                 # Font size
    animation_duration=0.3,       # Default animation duration
    enable_animations=True        # Enable/disable animations
)
```

## Widget Classes

### AnimatedButton

Interactive button with hover, click and animation effects.

#### Basic Usage

```python
from animated_widgets_pack import AnimatedButton, ButtonStyle

# Create button with custom styling
style = ButtonStyle(
    normal_color="#e74c3c",
    hover_color="#c0392b",
    pressed_color="#a93226",
    hover_lift=5.0,      # Elevation on hover
    click_scale=0.9      # Scale factor when clicked
)

button = AnimatedButton("My Button", style=style)
```

#### Button Methods

```python
# Event handling
button.on_click(callback_function)

# Text and colors
button.set_text("New Text")
button.set_colors(normal="#e74c3c", hover="#c0392b")

# Animation effects
button.pulse_animation(duration=1.0, scale_factor=1.2)
button.flash_animation(flash_color="#ffffff", duration=0.3)
button.bounce_animation(duration=0.6)

# State management
button.disable()
button.enable()
button.set_state("hover")
```

### AnimatedToggle

Animated toggle switch with smooth state transitions.

```python
from animated_widgets_pack import AnimatedToggle, ToggleStyle

# Create toggle switch
style = ToggleStyle(
    track_color_off="#95a5a6",
    track_color_on="#27ae60",
    thumb_color_off="#ecf0f1",
    thumb_color_on="#ffffff",
    transition_duration=0.3,
    bounce_effect=True
)

toggle = AnimatedToggle(initial_state=False, style=style)

# Event handling
toggle.on_toggle(lambda state: print(f"Toggle: {state}"))
toggle.on_value_changed(lambda state: print(f"Value changed: {state}"))

# Control methods
toggle.set_value(True, animate=True)
current_state = toggle.get_value()
toggle.toggle()  # Flip state

# Styling
toggle.set_colors(track_off="#bdc3c7", track_on="#2ecc71")
toggle.set_labels(label_on="ON", label_off="OFF", show=True)
toggle.enable_glow(enabled=True, color="#3498db", size=8)
```

### AnimatedProgressBar

Progress indicators with customizable styling and effects.

```python
from animated_widgets_pack import AnimatedProgressBar, ProgressBarStyle

# Create progress bar
style = ProgressBarStyle(
    background_color="#ecf0f1",
    fill_color="#3498db",
    fill_gradient_enabled=True,
    fill_gradient_colors=["#3498db", "#2980b9"],
    show_text=True,
    text_format="{value}%",
    pulse_enabled=True,
    stripes_enabled=True
)

progress = AnimatedProgressBar(
    initial_value=0,
    min_value=0,
    max_value=100,
    style=style
)

# Progress control
progress.set_value(75, animate=True)
progress.increment(10)
progress.decrement(5)
progress.reset()
progress.complete()

# Indeterminate mode
progress.set_indeterminate(True)

# Visual effects
progress.enable_pulse(enabled=True, color="#ffffff", opacity=0.3)
progress.enable_stripes(enabled=True, color="#ffffff", speed=2.0)
progress.flash_animation(color="#ffffff", duration=0.4)

# Segments for multi-colored progress
progress.add_segment(0, 30, "#e74c3c", "Critical")
progress.add_segment(30, 70, "#f39c12", "Warning")
progress.add_segment(70, 100, "#27ae60", "Good")
```

### AnimatedScrollView

Scrollable container with smooth scrolling and custom scroll bars.

```python
from animated_widgets_pack import AnimatedScrollView, ScrollViewStyle, ScrollBarStyle

# Create scroll view
scroll_style = ScrollViewStyle(
    background_color="#ffffff",
    horizontal_scroll_enabled=True,
    vertical_scroll_enabled=True,
    momentum_enabled=True,
    elastic_enabled=True
)

scrollbar_style = ScrollBarStyle(
    auto_hide=True,
    smooth_scrolling=True,
    thumb_color="#adb5bd"
)

scroll_view = AnimatedScrollView(
    style=scroll_style,
    scrollbar_style=scrollbar_style
)

# Add content
import tkinter as tk
label1 = tk.Label(scroll_view._content_frame, text="Content 1")
label2 = tk.Label(scroll_view._content_frame, text="Content 2")

scroll_view.add_widget(label1, pady=10)
scroll_view.add_widget(label2, pady=10)

# Scroll control
scroll_view.scroll_to(0, 100, animate=True)
scroll_view.scroll_by(0, 50, animate=True)
scroll_view.scroll_to_widget(label2, animate=True)

# Configuration
scroll_view.set_scroll_sensitivity(1.5)
scroll_view.enable_momentum(enabled=True, friction=0.95)
scroll_view.enable_elastic(enabled=True, distance=50)
```

## Animation System

### Animation Manager

Central animation manager handles all widget animations:

```python
from animated_widgets_pack import AnimationManager, AnimationConfig, EasingType

manager = AnimationManager()

# Create animation
config = AnimationConfig(
    duration=0.5,
    easing=EasingType.EASE_OUT_CUBIC,
    fps=60,
    auto_reverse=False,
    repeat_count=1,
    delay=0.0
)

# Start animation
def update_callback(value):
    # Update property with animated value
    widget.property = value
    widget.update_appearance()

def completion_callback():
    print("Animation completed!")

manager.animate(
    animation_id="my_animation",
    start_value=0.0,
    end_value=100.0,
    update_callback=update_callback,
    config=config,
    completion_callback=completion_callback
)

# Control animations
manager.stop_animation("my_animation")
manager.stop_all_animations()
is_running = manager.is_animating("my_animation")
```

### Easing Functions

Available easing types for smooth animations:

```python
from animated_widgets_pack import EasingType

# Linear
EasingType.LINEAR

# Quadratic
EasingType.EASE_IN_QUAD
EasingType.EASE_OUT_QUAD
EasingType.EASE_IN_OUT_QUAD

# Cubic
EasingType.EASE_IN_CUBIC
EasingType.EASE_OUT_CUBIC
EasingType.EASE_IN_OUT_CUBIC

# Special effects
EasingType.BOUNCE_OUT
EasingType.ELASTIC_OUT
EasingType.EASE_IN_BACK
EasingType.EASE_OUT_BACK
EasingType.EASE_IN_CIRC
EasingType.EASE_OUT_CIRC
```

### Animation Configurations

Pre-built animation configurations:

```python
from animated_widgets_pack.animations import (
    create_fade_animation,
    create_scale_animation,
    create_slide_animation,
    create_bounce_animation,
    create_elastic_animation
)

# Fade animation
fade_config = create_fade_animation(
    start_opacity=0.0,
    end_opacity=1.0,
    duration=0.3
)

# Scale animation with bounce
scale_config = create_scale_animation(
    duration=0.4,
    easing=EasingType.BOUNCE_OUT
)

# Slide animation
slide_config = create_slide_animation(
    duration=0.5,
    easing=EasingType.EASE_OUT_CUBIC
)
```

## Utility Functions

### Color Utilities

Comprehensive color manipulation tools:

```python
from animated_widgets_pack import ColorUtils, Color

# Parse different color formats
color1 = ColorUtils.parse_color("#3498db")           # Hex
color2 = ColorUtils.parse_color("rgb(52, 152, 219)") # RGB string
color3 = ColorUtils.parse_color((52, 152, 219))     # RGB tuple
color4 = ColorUtils.parse_color("blue")             # Named color

# Color manipulation
lighter = ColorUtils.lighten_color("#3498db", 0.2)   # 20% lighter
darker = ColorUtils.darken_color("#3498db", 0.2)     # 20% darker
contrast = ColorUtils.get_contrast_color("#3498db")  # Black or white

# Color interpolation
mid_color = ColorUtils.interpolate_colors(color1, color2, 0.5)

# Color conversion
hex_color = color1.to_hex()              # "#3498db"
rgba_string = color1.to_rgba_string()    # "rgba(52, 152, 219, 1.0)"
rgb_tuple = color1.to_rgb_tuple()        # (52, 152, 219)
```

### Geometry Utilities

Mathematical utilities for shapes and positioning:

```python
from animated_widgets_pack import GeometryUtils, Point, Rectangle

# Distance calculation
p1 = Point(0, 0)
p2 = Point(3, 4)
distance = GeometryUtils.distance(p1, p2)  # 5.0

# Value manipulation
clamped = GeometryUtils.clamp(15, 0, 10)  # 10
lerped = GeometryUtils.lerp(0, 10, 0.5)   # 5.0
mapped = GeometryUtils.map_range(5, 0, 10, 0, 100)  # 50

# Rectangle operations
rect = Rectangle(10, 20, 100, 50)
center = rect.center()          # Point(60, 45)
area = rect.area()              # 5000
contains = rect.contains_point(Point(50, 40))  # True

# Rounded rectangle path
points = GeometryUtils.round_rectangle_path(rect, radius=10)

# Bezier curves
bezier_point = GeometryUtils.calculate_bezier_point(
    t=0.5, 
    p0=Point(0, 0), 
    p1=Point(0, 10), 
    p2=Point(10, 10), 
    p3=Point(10, 0)
)
```

### Color Palettes

Pre-defined color palettes for quick styling:

```python
from animated_widgets_pack.utils import ColorPalettes

# Material Design colors
material_blue = ColorPalettes.MATERIAL_DESIGN['blue']    # #2196F3
material_red = ColorPalettes.MATERIAL_DESIGN['red']      # #F44336

# Flat UI colors
flat_turquoise = ColorPalettes.FLAT_UI['turquoise']      # #1ABC9C
flat_emerald = ColorPalettes.FLAT_UI['emerland']         # #2ECC71

# Bootstrap colors
bootstrap_primary = ColorPalettes.BOOTSTRAP['primary']   # #007bff
bootstrap_success = ColorPalettes.BOOTSTRAP['success']   # #28a745

# Modern dark theme
dark_background = ColorPalettes.MODERN_DARK['background'] # #1a1a1a
dark_primary = ColorPalettes.MODERN_DARK['primary']       # #bb86fc
```

## Framework Integration

### Tkinter Integration

```python
import tkinter as tk
from animated_widgets_pack import AnimatedButton

root = tk.Tk()
button = AnimatedButton("Tkinter Button")
widget = button.render(root, "tkinter")  # Returns tk.Button
widget.pack(pady=10)

# The returned widget is a native Tkinter widget
# with all animation capabilities added
```

### PyQt5 Integration

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from animated_widgets_pack import AnimatedButton

app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
layout = QVBoxLayout(central_widget)

button = AnimatedButton("PyQt5 Button")
widget = button.render(central_widget, "pyqt5")  # Returns QPushButton
layout.addWidget(widget)

window.setCentralWidget(central_widget)
window.show()
sys.exit(app.exec_())
```

### Framework-Specific Features

#### Tkinter
- Returns native `tk.Button`, `tk.Canvas` objects
- Automatic event binding with `bind()` methods
- Color updates via `configure()`
- Canvas-based custom drawing for complex widgets

#### PyQt5/PyQt6
- Returns native `QPushButton`, `QWidget` objects
- CSS-based styling with `setStyleSheet()`
- Signal/slot event system
- `QPainter` for custom graphics


## API Reference (continued)

### Core Classes (continued)

#### AnimatedWidget (continued)

**Methods:**
- `render(parent_widget, framework="tkinter")` - Render widget
- `update_appearance()` - Update visual appearance
- `bind_callback(event_type, callback)` - Bind event callback
- `trigger_callback(event_type, *args, **kwargs)` - Trigger event callbacks
- `animate_property(property_name, start_value, end_value, duration, easing_function)` - Animate property
- `set_state(new_state)` - Change widget state
- `get_state()` - Get current widget state
- `enable()` / `disable()` - Enable/disable widget
- `stop_all_animations()` - Stop all running animations
- `is_animating()` - Check if animations are running

**Events:**
- `click` - Widget was clicked
- `hover_enter` - Mouse entered widget
- `hover_leave` - Mouse left widget
- `value_changed` - Widget value changed
- `state_changed` - Widget state changed

#### AnimatedButton

**Constructor:**
```python
AnimatedButton(text="Button", config=None, style=None)
```

**Methods:**
- `on_click(callback)` - Set click callback (chainable)
- `set_text(text)` - Change button text
- `set_colors(normal=None, hover=None, pressed=None)` - Update colors
- `pulse_animation(duration=1.0, scale_factor=1.1)` - Pulse effect
- `flash_animation(flash_color="#ffffff", duration=0.3)` - Flash effect
- `bounce_animation(duration=0.6)` - Bounce effect

**ButtonStyle Properties:**
```python
ButtonStyle(
    normal_color="#3498db",
    hover_color="#2980b9",
    pressed_color="#21618c",
    disabled_color="#95a5a6",
    text="Button",
    icon=None,
    shadow_enabled=True,
    shadow_color="#2c3e50",
    shadow_offset=(0, 2),
    hover_lift=2.0,
    click_scale=0.95
)
```

#### AnimatedToggle

**Constructor:**
```python
AnimatedToggle(initial_state=False, config=None, style=None)
```

**Methods:**
- `toggle()` - Toggle state
- `set_value(value, animate=True)` - Set toggle value
- `get_value()` - Get current value
- `on_toggle(callback)` - Set toggle callback (chainable)
- `on_value_changed(callback)` - Set value change callback (chainable)
- `set_colors(track_off=None, track_on=None, thumb_off=None, thumb_on=None)` - Update colors
- `set_labels(label_on=None, label_off=None, show=None)` - Set labels
- `enable_glow(enabled=True, color=None, size=None)` - Enable glow effect

#### AnimatedProgressBar

**Constructor:**
```python
AnimatedProgressBar(initial_value=0.0, min_value=0.0, max_value=100.0, 
                   config=None, style=None, circular=False)
```

**Methods:**
- `set_value(value, animate=True)` - Set progress value
- `get_value()` - Get current value
- `set_range(min_value, max_value)` - Set value range
- `get_range()` - Get current range
- `increment(amount=1.0, animate=True)` - Increment value
- `decrement(amount=1.0, animate=True)` - Decrement value
- `reset(animate=True)` - Reset to minimum
- `complete(animate=True)` - Set to maximum
- `set_indeterminate(enabled=True)` - Enable indeterminate mode
- `add_segment(start_value, end_value, color, label="")` - Add colored segment
- `clear_segments()` - Clear all segments
- `enable_pulse(enabled=True, color=None, opacity=None)` - Enable pulse effect
- `enable_stripes(enabled=True, color=None, width=None, speed=None)` - Enable stripes

#### AnimatedScrollView

**Constructor:**
```python
AnimatedScrollView(config=None, style=None, scrollbar_style=None)
```

**Methods:**
- `scroll_to(x, y, animate=True)` - Scroll to position
- `scroll_by(dx, dy, animate=True)` - Scroll by amount
- `get_scroll_position()` - Get current scroll position
- `get_content_size()` - Get content dimensions
- `add_widget(widget, **pack_options)` - Add widget to content
- `remove_widget(widget)` - Remove widget from content
- `clear_widgets()` - Remove all widgets
- `scroll_to_widget(widget, animate=True)` - Scroll to widget
- `set_scroll_sensitivity(sensitivity)` - Set scroll sensitivity
- `enable_momentum(enabled=True, friction=None)` - Enable momentum scrolling
- `enable_elastic(enabled=True, distance=None, resistance=None)` - Enable elastic scrolling

### Animation Classes

#### AnimationManager

**Methods:**
- `animate(animation_id, start_value, end_value, update_callback, config=None, completion_callback=None)` - Start animation
- `stop_animation(animation_id)` - Stop specific animation
- `stop_all_animations()` - Stop all animations
- `is_animating(animation_id)` - Check if animation is running
- `get_active_count()` - Get number of active animations

#### AnimationConfig

**Properties:**
```python
AnimationConfig(
    duration=0.3,                     # Animation duration in seconds
    easing=EasingType.EASE_OUT_CUBIC, # Easing function
    fps=60,                           # Frames per second
    auto_reverse=False,               # Auto-reverse animation
    repeat_count=1,                   # Number of repetitions
    delay=0.0                         # Delay before starting
)
```

### Utility Classes

#### ColorUtils

**Static Methods:**
- `hex_to_rgb(hex_color)` - Convert hex to RGB tuple
- `rgb_to_hex(r, g, b)` - Convert RGB to hex string
- `parse_color(color_input)` - Parse various color formats
- `lighten_color(color, factor=0.2)` - Lighten color
- `darken_color(color, factor=0.2)` - Darken color
- `interpolate_colors(color1, color2, factor)` - Interpolate between colors
- `get_contrast_color(color)` - Get contrasting color (black/white)

#### GeometryUtils

**Static Methods:**
- `distance(p1, p2)` - Distance between points
- `clamp(value, min_value, max_value)` - Clamp value to range
- `lerp(start, end, factor)` - Linear interpolation
- `map_range(value, from_min, from_max, to_min, to_max)` - Map value between ranges
- `round_rectangle_path(rect, radius)` - Generate rounded rectangle points
- `calculate_bezier_point(t, p0, p1, p2, p3)` - Calculate Bezier curve point
- `normalize_angle(angle)` - Normalize angle to [0, 2π)
- `degrees_to_radians(degrees)` - Convert degrees to radians
- `radians_to_degrees(radians)` - Convert radians to degrees

## Examples

### Complex Button Example

```python
import tkinter as tk
from animated_widgets_pack import *

root = tk.Tk()
root.title("Advanced Button Demo")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Create multiple buttons with different styles
buttons = []

# Primary button
primary_config = WidgetConfig(width=160, height=50, border_radius=8)
primary_style = ButtonStyle(
    normal_color="#3498db",
    hover_color="#2980b9",
    pressed_color="#21618c",
    hover_lift=3.0,
    click_scale=0.92
)

primary_btn = AnimatedButton("Primary", primary_config, primary_style)
primary_widget = primary_btn.render(root, "tkinter")
primary_widget.pack(pady=10)

# Success button with glow effect
success_style = ButtonStyle(
    normal_color="#27ae60",
    hover_color="#229954",
    pressed_color="#1e8449"
)

success_btn = AnimatedButton("Success", primary_config, success_style)
success_widget = success_btn.render(root, "tkinter")
success_widget.pack(pady=10)

# Animated interactions
def on_primary_click():
    primary_btn.pulse_animation(duration=0.8, scale_factor=1.2)
    success_btn.flash_animation("#ffffff", 0.3)

def on_success_click():
    success_btn.bounce_animation(0.6)

primary_btn.on_click(on_primary_click)
success_btn.on_click(lambda: success_btn.bounce_animation(0.6))

root.mainloop()
```

### Progress Bar with Segments

```python
import tkinter as tk
from animated_widgets_pack import *
import threading
import time

root = tk.Tk()
root.title("Progress Bar Demo")
root.geometry("500x200")

# Create progress bar
progress_config = WidgetConfig(width=400, height=30)
progress_style = ProgressBarStyle(
    background_color="#ecf0f1",
    fill_gradient_enabled=True,
    fill_gradient_colors=["#e74c3c", "#f39c12", "#27ae60"],
    show_text=True,
    text_format="{value}%",
    pulse_enabled=True,
    stripes_enabled=True
)

progress = AnimatedProgressBar(0, 0, 100, progress_config, progress_style)
progress_widget = progress.render(root, "tkinter")
progress_widget.pack(pady=50)

# Add segments
progress.add_segment(0, 30, "#e74c3c", "Critical")
progress.add_segment(30, 70, "#f39c12", "Warning")
progress.add_segment(70, 100, "#27ae60", "Good")

# Simulate progress
def simulate_progress():
    for i in range(101):
        progress.set_value(i, animate=True)
        time.sleep(0.05)
    
    # Flash when complete
    progress.flash_animation("#ffffff", 0.5)

def start_simulation():
    thread = threading.Thread(target=simulate_progress, daemon=True)
    thread.start()

# Control button
btn = AnimatedButton("Start Progress")
btn_widget = btn.render(root, "tkinter")
btn_widget.pack(pady=20)
btn.on_click(start_simulation)

root.mainloop()
```

### Scrollable Content Example

```python
import tkinter as tk
from animated_widgets_pack import *

root = tk.Tk()
root.title("Scroll View Demo")
root.geometry("400x300")

# Create scroll view
scroll_config = WidgetConfig(width=350, height=250)
scroll_style = ScrollViewStyle(
    background_color="#ffffff",
    border_color="#dee2e6",
    border_width=1,
    momentum_enabled=True,
    elastic_enabled=True
)

scrollbar_style = ScrollBarStyle(
    auto_hide=True,
    smooth_scrolling=True,
    thumb_color="#6c757d"
)

scroll_view = AnimatedScrollView(scroll_config, scroll_style, scrollbar_style)
scroll_widget = scroll_view.render(root, "tkinter")
scroll_widget.pack(pady=20)

# Add content
for i in range(20):
    label = tk.Label(
        scroll_view._content_frame,
        text=f"Scrollable Item {i+1}",
        bg="#f8f9fa",
        relief="solid",
        bd=1,
        height=2
    )
    scroll_view.add_widget(label, fill="x", padx=10, pady=5)

# Add scroll callbacks
scroll_view.on_scroll(lambda x, y: print(f"Scrolled to: {x}, {y}"))

root.mainloop()
```

### Theme Management Example

```python
import tkinter as tk
from animated_widgets_pack import *
from animated_widgets_pack.utils import ThemeManager

root = tk.Tk()
root.title("Theme Demo")
root.geometry("300x200")

# Initialize theme manager
theme_manager = ThemeManager()
theme_manager.add_theme("custom", {
    "background": "#2c3e50",
    "text": "#ecf0f1",
    "primary": "#e74c3c",
    "secondary": "#95a5a6"
})

# Function to apply theme
def apply_theme(theme_name):
    theme_manager.set_theme(theme_name)
    
    # Update root background
    root.configure(bg=theme_manager.get_color("background"))
    
    # Update button colors
    primary_color = theme_manager.get_color("primary")
    secondary_color = theme_manager.get_color("secondary")
    
    button.set_colors(
        normal=primary_color,
        hover=ColorUtils.darken_color(primary_color, 0.1).to_hex()
    )

# Create themed button
button_config = WidgetConfig(
    background_color=theme_manager.get_color("primary"),
    text_color=theme_manager.get_color("text")
)

button = AnimatedButton("Themed Button", button_config)
button_widget = button.render(root, "tkinter")
button_widget.pack(pady=30)

# Theme toggle button
def toggle_theme():
    current = theme_manager.current_theme
    new_theme = "dark" if current == "light" else "light"
    apply_theme(new_theme)

toggle_btn = AnimatedButton("Toggle Theme")
toggle_widget = toggle_btn.render(root, "tkinter")
toggle_widget.pack(pady=10)
toggle_btn.on_click(toggle_theme)

# Apply initial theme
apply_theme("light")

root.mainloop()
```

## Best Practices

### Performance Optimization

1. **Stop Animations When Not Needed**
```python
# Stop animations when widget is destroyed or hidden
widget.stop_all_animations()

# Use shorter animation durations for better responsiveness
config = WidgetConfig(animation_duration=0.2)
```

2. **Reuse Animation Configurations**
```python
# Create reusable configs
fast_config = AnimationConfig(duration=0.2, easing=EasingType.EASE_OUT_QUAD)
slow_config = AnimationConfig(duration=0.8, easing=EasingType.EASE_OUT_CUBIC)
```

3. **Batch Updates**
```python
# Update multiple properties together
widget.set_colors(normal="#e74c3c", hover="#c0392b", pressed="#a93226")
```

### Memory Management

1. **Proper Cleanup**
```python
# In your application's cleanup code
for widget in animated_widgets:
    widget.stop_all_animations()

# For long-running applications
animation_manager.stop_all_animations()
```

2. **Avoid Circular References**
```python
# Use weak references for callbacks when needed
import weakref

def create_callback(widget_ref):
    def callback():
        widget = widget_ref()
        if widget:
            widget.update_appearance()
    return callback

widget_ref = weakref.ref(widget)
widget.bind_callback('click', create_callback(widget_ref))
```

### Animation Guidelines

1. **Choose Appropriate Easing**
```python
# Use EASE_OUT for UI interactions (feels responsive)
button_hover = EasingType.EASE_OUT_QUAD

# Use BOUNCE for playful effects
celebration = EasingType.BOUNCE_OUT

# Use ELASTIC for attention-grabbing animations
notification = EasingType.ELASTIC_OUT
```

2. **Timing Recommendations**
```python
# Quick interactions (hover, click)
quick_duration = 0.2

# State changes
medium_duration = 0.3

# Major transitions
slow_duration = 0.5

# Special effects
effect_duration = 0.8
```

3. **Accessibility Considerations**
```python
# Allow users to disable animations
config = WidgetConfig(enable_animations=user_preference_animations)

# Provide alternative feedback for disabled animations
if not config.enable_animations:
    # Use immediate visual changes instead
    widget.update_appearance()
```

### Error Handling

1. **Graceful Framework Detection**
```python
def safe_render(widget, parent):
    try:
        return widget.render(parent, "tkinter")
    except ImportError:
        print("GUI framework not available")
        return None
    except Exception as e:
        print(f"Rendering error: {e}")
        return None
```

2. **Animation Error Recovery**
```python
# Widgets should handle animation failures gracefully
try:
    widget.pulse_animation()
except Exception as e:
    print(f"Animation failed: {e}")
    # Fall back to immediate state change
    widget.update_appearance()
```

### Code Organization

1. **Separate Configuration**
```python
# config.py
from animated_widgets_pack import WidgetConfig, ButtonStyle

BUTTON_CONFIG = WidgetConfig(
    width=120,
    height=40,
    animation_duration=0.3
)

BUTTON_STYLES = {
    'primary': ButtonStyle(normal_color="#3498db"),
    'success': ButtonStyle(normal_color="#27ae60"),
    'danger': ButtonStyle(normal_color="#e74c3c")
}
```

2. **Widget Factories**
```python
def create_themed_button(text, style_name="primary"):
    config = BUTTON_CONFIG
    style = BUTTON_STYLES.get(style_name, BUTTON_STYLES['primary'])
    return AnimatedButton(text, config, style)

# Usage
button = create_themed_button("Save", "success")
```

3. **Event Handler Organization**
```python
class ButtonHandlers:
    @staticmethod
    def on_save_click():
        # Save logic
        pass
    
    @staticmethod
    def on_cancel_click():
        # Cancel logic
        pass

# Bind handlers
save_button.on_click(ButtonHandlers.on_save_click)
cancel_button.on_click(ButtonHandlers.on_cancel_click)
```

