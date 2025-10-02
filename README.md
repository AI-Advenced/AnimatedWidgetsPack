# AnimatedWidgetsPack 🎨

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)

<img width="894" height="724" alt="image" src="https://github.com/user-attachments/assets/1f01ab2c-9f72-4cb9-8586-f2fdd3fe8aa7" />


A modern Python library for creating animated GUI widgets with smooth transitions and interactive effects, compatible with Tkinter, PyQt5/PyQt6 and other GUI frameworks.

## ✨ Features

- 🎬 **Smooth Animations** - Fluid transitions between widget states with customizable easing functions
- 🎨 **Full Customization** - Colors, sizes, shapes, and animation timing fully customizable  
- 🔧 **Multi-Framework Support** - Works with Tkinter, PyQt5, PyQt6 out of the box
- 📦 **Modular Architecture** - Independent components that can be used separately
- 🚀 **Optimized Performance** - 60 FPS animations with efficient threading
- 🎯 **Simple API** - Intuitive interface with method chaining support
- 🧪 **Well Tested** - Comprehensive test suite with 90%+ coverage

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install animated-widgets-pack

# With PyQt5 support
pip install animated-widgets-pack[gui]

# Full installation for development
pip install animated-widgets-pack[dev,gui,examples]
```

### Simple Example

```python
import tkinter as tk
from animated_widgets_pack import AnimatedButton, WidgetConfig, ButtonStyle

# Create main window
root = tk.Tk()
root.title("Animated Button Demo")
root.geometry("300x200")

# Configure animated button
config = WidgetConfig(
    width=180, 
    height=50,
    border_radius=10,
    animation_duration=0.3
)

style = ButtonStyle(
    normal_color="#3498db",
    hover_color="#2980b9", 
    pressed_color="#21618c",
    hover_lift=4.0
)

# Create and render button
button = AnimatedButton("Click Me! 🚀", config=config, style=style)
button_widget = button.render(root, "tkinter")
button_widget.pack(expand=True)

# Add click handler
button.on_click(lambda: print("Button clicked with smooth animation!"))

root.mainloop()
```

## 📚 Available Widgets

| Widget | Description | Key Animations |
|--------|-------------|----------------|
| `AnimatedButton` | Interactive buttons with hover/click effects | Color transitions, scale effects, elevation |
| `AnimatedSlider` | Smooth sliders with fluid dragging | Position interpolation, value transitions |  
| `AnimatedToggle` | On/off switches with state animations | Color morphing, position sliding |
| `AnimatedProgressBar` | Progress indicators with fill effects | Fill animation, pulsing effects |
| `AnimatedCheckbox` | Stylized checkboxes with check animations | Check mark drawing, color changes |

*Note: This release includes `AnimatedButton`. Additional widgets are in development.*

## 🎨 Customization Examples

### Multiple Button Styles

```python
from animated_widgets_pack import AnimatedButton, ButtonStyle, WidgetConfig

# Button configuration
config = WidgetConfig(width=160, height=50, border_radius=8)

# Primary button
primary_btn = AnimatedButton(
    "Primary",
    config=config,
    style=ButtonStyle(
        normal_color="#3498db",
        hover_color="#2980b9",
        pressed_color="#21618c"
    )
)

# Success button
success_btn = AnimatedButton(
    "Success",
    config=config,
    style=ButtonStyle(
        normal_color="#27ae60",
        hover_color="#229954", 
        pressed_color="#1e8449"
    )
)

# Danger button with enhanced effects
danger_btn = AnimatedButton(
    "Danger",
    config=config,
    style=ButtonStyle(
        normal_color="#e74c3c",
        hover_color="#c0392b",
        pressed_color="#a93226",
        hover_lift=6.0,      # More elevation on hover
        click_scale=0.9      # More shrink on click
    )
)
```

### Advanced Animation Effects

```python
# Pulse animation
button.pulse_animation(duration=1.0, scale_factor=1.3)

# Flash effect
button.flash_animation(flash_color="#ffffff", duration=0.4)

# Bounce effect  
button.bounce_animation(duration=0.8)

# Custom color transition
button.set_colors(normal="#9b59b6")  # Animate to new color
```

### Custom Easing Functions

```python
from animated_widgets_pack import AnimationConfig, EasingType

# Bouncy button press
config = AnimationConfig(
    duration=0.6,
    easing=EasingType.BOUNCE_OUT
)

button.animate_property("scale", 1.0, 1.2, config)

# Elastic hover effect
elastic_config = AnimationConfig(
    duration=0.8,
    easing=EasingType.ELASTIC_OUT  
)
```

## 🎛️ Configuration Options

### WidgetConfig

```python
config = WidgetConfig(
    width=120,                    # Widget width in pixels
    height=40,                    # Widget height in pixels
    background_color="#3498db",   # Background color (hex/rgb/named)
    text_color="#ffffff",         # Text color
    border_radius=8,              # Border radius for rounded corners
    border_width=0,               # Border width
    border_color="#2c3e50",       # Border color
    font_family="Arial",          # Font family
    font_size=12,                 # Font size
    animation_duration=0.3,       # Default animation duration
    enable_animations=True        # Enable/disable animations globally
)
```

### ButtonStyle

```python
style = ButtonStyle(
    normal_color="#3498db",       # Normal state color
    hover_color="#2980b9",        # Hover state color  
    pressed_color="#21618c",      # Pressed state color
    disabled_color="#95a5a6",     # Disabled state color
    text="Button",                # Button text
    icon=None,                    # Icon path (future feature)
    shadow_enabled=True,          # Enable drop shadow
    shadow_color="#2c3e50",       # Shadow color
    shadow_offset=(0, 2),         # Shadow offset (x, y)
    hover_lift=2.0,               # Elevation on hover (pixels)
    click_scale=0.95              # Scale factor when clicked
)
```

## 🎪 Animation System

### Available Easing Types

```python
from animated_widgets_pack import EasingType

# Linear and quadratic
EasingType.LINEAR
EasingType.EASE_IN_QUAD
EasingType.EASE_OUT_QUAD  
EasingType.EASE_IN_OUT_QUAD

# Cubic easing
EasingType.EASE_IN_CUBIC
EasingType.EASE_OUT_CUBIC
EasingType.EASE_IN_OUT_CUBIC

# Special effects
EasingType.BOUNCE_OUT
EasingType.ELASTIC_OUT
```

### Animation Configuration

```python
from animated_widgets_pack import AnimationConfig

config = AnimationConfig(
    duration=0.3,                 # Animation duration in seconds
    easing=EasingType.EASE_OUT_CUBIC,  # Easing function
    fps=60,                       # Frames per second
    auto_reverse=False,           # Auto-reverse animation
    repeat_count=1,               # Number of repetitions
    delay=0.0                     # Delay before starting
)
```

## 🎨 Color System

### Color Utilities

```python
from animated_widgets_pack import ColorUtils

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
```

### Predefined Color Palettes

```python
from animated_widgets_pack.utils import ColorPalettes

# Material Design colors
material_blue = ColorPalettes.MATERIAL_DESIGN['blue']  # #2196F3

# Flat UI colors  
flat_turquoise = ColorPalettes.FLAT_UI['turquoise']    # #1ABC9C

# Bootstrap colors
bootstrap_primary = ColorPalettes.BOOTSTRAP['primary'] # #007bff
```

## 🔧 Framework Integration

### Tkinter Integration

```python
import tkinter as tk
from animated_widgets_pack import AnimatedButton

root = tk.Tk()
button = AnimatedButton("Tkinter Button")
widget = button.render(root, "tkinter")  # Returns tk.Button
widget.pack(pady=10)
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

## 📊 Event Handling

### Basic Event Callbacks

```python
# Click events
button.on_click(lambda: print("Clicked!"))

# Hover events
button.bind_callback('hover_enter', lambda: print("Mouse entered"))
button.bind_callback('hover_leave', lambda: print("Mouse left"))

# State changes
button.bind_callback('state_changed', 
    lambda old_state, new_state: print(f"State: {old_state} → {new_state}"))
```

### Multiple Callbacks

```python
# Multiple callbacks for the same event
button.on_click(lambda: print("First callback"))
button.on_click(lambda: print("Second callback"))
button.on_click(lambda: send_analytics_event("button_click"))

# All callbacks will be executed in order
```

## 🧪 Testing

Run the test suite to verify installation:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=animated_widgets_pack --cov-report=html

# Run specific test module
python -m pytest tests/test_buttons.py -v

# Run examples
python examples/simple_example.py
python examples/demo_tkinter.py
```

## 📁 Project Structure

```
AnimatedWidgetsPack/
├── animated_widgets_pack/          # Main library package
│   ├── __init__.py                # Package initialization and exports
│   ├── core.py                    # Base AnimatedWidget class
│   ├── animations.py              # Animation manager and easing functions
│   ├── utils.py                   # Color and geometry utilities
│   └── buttons.py                 # Animated button implementation
├── examples/                      # Example applications
│   ├── simple_example.py          # Basic usage example
│   └── demo_tkinter.py           # Complete Tkinter demo
├── tests/                        # Test suite
│   ├── test_core.py              # Core functionality tests
│   ├── test_utils.py             # Utility function tests
│   └── test_buttons.py           # Button widget tests
├── docs/                         # Documentation
├── setup.py                      # Package setup configuration
├── pyproject.toml                # Modern Python project config
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## 🏗️ Architecture

### Core Components

1. **AnimatedWidget** - Abstract base class providing common animation functionality
2. **AnimationManager** - Handles smooth transitions with threading and easing
3. **ColorUtils** - Color parsing, manipulation, and interpolation utilities  
4. **GeometryUtils** - Mathematical utilities for shapes and positioning
5. **Widget Implementations** - Concrete widgets like AnimatedButton

### Design Principles

- **Composition over Inheritance** - Widgets compose animation managers rather than inheriting complex behavior
- **Framework Agnostic Core** - Core animation logic separated from GUI framework specifics
- **Thread Safe** - Animations run in background threads without blocking UI
- **Memory Efficient** - Automatic cleanup of completed animations
- **Extensible** - Easy to add new widgets and animation effects

## 🤝 Contributing

We welcome contributions! Here's how to get started:

```bash
# Clone the repository
git clone https://github.com/yourusername/animated-widgets-pack.git
cd AnimatedWidgetsPack

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev,gui,examples]

# Run tests to ensure everything works
python -m pytest tests/ -v

# Make your changes and add tests

# Format code
black animated_widgets_pack/ tests/ examples/

# Run linting
flake8 animated_widgets_pack/ tests/

# Submit pull request
```

### Development Guidelines

- Add tests for new features
- Follow PEP 8 style guidelines  
- Update documentation for API changes
- Test with multiple GUI frameworks
- Keep animations smooth and responsive

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Python GUI framework communities for excellent foundation libraries
- Animation and easing inspiration from web development and game engines
- Contributors and testers who help improve the library
- Open source projects that inspired this architecture

## 🔮 Roadmap

### Version 1.1 (Coming Soon)
- `AnimatedSlider` with smooth dragging
- `AnimatedToggle` with state transitions
- More easing functions (Back, Circ, etc.)

### Version 1.2
- `AnimatedProgressBar` with fill effects
- `AnimatedCheckbox` with check animations  
- Theme system with predefined styles

### Version 1.3
- Advanced effects (glow, shadow, gradients)
- Animation sequences and timelines
- Performance optimizations

---

**AnimatedWidgetsPack** - Make your GUI applications come alive! ✨

For more information, visit our [documentation](https://animated-widgets-pack.readthedocs.io/) or check out the [examples](examples/) directory.
