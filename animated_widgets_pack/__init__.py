"""
AnimatedWidgetsPack - Animated GUI Widgets Library

A collection of interactive widgets with smooth animations
for PyQt5, Tkinter and other Python GUI frameworks.

Version: 1.0.0
Author: AnimatedWidgetsPack Team
"""

__version__ = "1.0.0"
__author__ = "AnimatedWidgetsPack Team"

# Core imports
from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, EasingType
from .utils import ColorUtils, GeometryUtils, ValidationUtils, InteractionUtils, RenderUtils

# Widget imports
try:
    from .buttons import AnimatedButton, ButtonStyle
except ImportError:
    pass

try:
    from .textinput import AnimatedTextInput, TextInputStyle, TextInputType, TextInputValidator
except ImportError:
    pass

try:
    from .checkbox import AnimatedCheckbox, CheckboxStyle, CheckboxState, CheckboxAnimation
except ImportError:
    pass

try:
    from .switch import AnimatedSwitch, SwitchAppearance, SwitchState, SwitchStyle, SwitchAnimation
except ImportError:
    pass

__all__ = [
    "AnimatedWidget", "WidgetConfig",
    "AnimationManager", "EasingType",
    "ColorUtils", "GeometryUtils", "ValidationUtils", "InteractionUtils", "RenderUtils"
]

# Add widgets to __all__ as they become available
try:
    from .buttons import AnimatedButton, ButtonStyle
    __all__.extend(["AnimatedButton", "ButtonStyle"])
except ImportError:
    pass

try:
    from .textinput import AnimatedTextInput, TextInputStyle, TextInputType, TextInputValidator
    __all__.extend(["AnimatedTextInput", "TextInputStyle", "TextInputType", "TextInputValidator"])
except ImportError:
    pass

try:
    from .checkbox import AnimatedCheckbox, CheckboxStyle, CheckboxState, CheckboxAnimation
    __all__.extend(["AnimatedCheckbox", "CheckboxStyle", "CheckboxState", "CheckboxAnimation"])
except ImportError:
    pass

try:
    from .switch import AnimatedSwitch, SwitchAppearance, SwitchState, SwitchStyle, SwitchAnimation
    __all__.extend(["AnimatedSwitch", "SwitchAppearance", "SwitchState", "SwitchStyle", "SwitchAnimation"])
except ImportError:
    pass
