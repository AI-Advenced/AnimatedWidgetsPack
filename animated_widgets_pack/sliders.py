"""
Module sliders - Interactive sliders with smooth animations
"""

import math
import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional, Tuple, List, Union
from enum import Enum

from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, AnimationConfig, EasingType
from .utils import ColorUtils, Color, Rectangle, Point, GeometryUtils

class SliderOrientation(Enum):
    """Slider orientation options"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class SliderType(Enum):
    """Types of sliders"""
    SINGLE = "single"           # Single value slider
    RANGE = "range"            # Range slider with two handles
    STEPPED = "stepped"        # Discrete steps
    LOG_SCALE = "log_scale"    # Logarithmic scale

class HandleShape(Enum):
    """Handle shape options"""
    CIRCLE = "circle"
    SQUARE = "square"
    DIAMOND = "diamond"
    OVAL = "oval"
    CUSTOM = "custom"

class TrackStyle(Enum):
    """Track styling options"""
    FLAT = "flat"
    RAISED = "raised"
    INSET = "inset"
    GRADIENT = "gradient"
    GLOW = "glow"

@dataclass
class SliderStyle:
    """Slider-specific styling configuration"""
    # Track styling
    track_color: str = "#e0e0e0"
    track_active_color: str = "#3498db"
    track_inactive_color: str = "#bdc3c7"
    track_height: int = 8
    track_border_radius: int = 4
    track_border_width: int = 0
    track_border_color: str = "#95a5a6"
    track_style: TrackStyle = TrackStyle.FLAT
    
    # Handle styling
    handle_color: str = "#3498db"
    handle_hover_color: str = "#2980b9"
    handle_pressed_color: str = "#21618c"
    handle_disabled_color: str = "#95a5a6"
    handle_size: int = 20
    handle_border_width: int = 2
    handle_border_color: str = "#ffffff"
    handle_shape: HandleShape = HandleShape.CIRCLE
    handle_shadow: bool = True
    handle_shadow_color: str = "#444444"  # Changé de "#00000033" à "#cccccc"
    handle_shadow_offset: Tuple[int, int] = (0, 2)
    handle_shadow_blur: int = 4
    
    # Animation settings
    handle_hover_scale: float = 1.1
    handle_press_scale: float = 0.95
    smooth_dragging: bool = True
    snap_to_steps: bool = False
    
    # Labels and ticks
    show_value_label: bool = True
    show_min_max_labels: bool = True
    show_ticks: bool = False
    tick_count: int = 5
    tick_color: str = "#95a5a6"
    tick_height: int = 4
    label_color: str = "#2c3e50"
    label_font_size: int = 10
    
    # Tooltip
    show_tooltip: bool = True
    tooltip_background: str = "#2c3e50"
    tooltip_text_color: str = "#ffffff"
    tooltip_border_radius: int = 4
    tooltip_padding: int = 6
    
    # Colors for different states
    focus_color: str = "#3498db"
    error_color: str = "#e74c3c"
    warning_color: str = "#f39c12"
    success_color: str = "#27ae60"


@dataclass
class SliderValue:
    """Container for slider value(s)"""
    single: float = 0.0
    range_start: float = 0.0
    range_end: float = 100.0
    
    def get_primary(self) -> float:
        """Get primary value (single or range_start)"""
        return self.single if hasattr(self, 'single') else self.range_start
    
    def get_secondary(self) -> Optional[float]:
        """Get secondary value (for range sliders)"""
        return getattr(self, 'range_end', None)
    
    def set_single(self, value: float):
        """Set single value"""
        self.single = value
    
    def set_range(self, start: float, end: float):
        """Set range values"""
        self.range_start = min(start, end)
        self.range_end = max(start, end)

class SliderHandle:
    """Individual slider handle"""
    
    def __init__(self, slider: 'AnimatedSlider', handle_id: str, initial_value: float = 0.0):
        self.slider = slider
        self.handle_id = handle_id
        self.value = initial_value
        self.position = Point(0, 0)
        self.is_dragging = False
        self.is_hovered = False
        self.is_pressed = False
        self.current_scale = 1.0
        self.animation_manager = AnimationManager()
        
        # Visual properties
        self.current_color = ColorUtils.parse_color(slider.style.handle_color)
        self.target_color = self.current_color
        
    def update_position_from_value(self):
        """Update handle position based on current value"""
        if self.slider.config_slider.orientation == SliderOrientation.HORIZONTAL:
            track_width = self.slider.config.width - self.slider.style.handle_size
            progress = (self.value - self.slider.min_value) / (self.slider.max_value - self.slider.min_value)
            self.position.x = progress * track_width + self.slider.style.handle_size // 2
            self.position.y = self.slider.config.height // 2
        else:
            track_height = self.slider.config.height - self.slider.style.handle_size
            progress = (self.value - self.slider.min_value) / (self.slider.max_value - self.slider.min_value)
            self.position.x = self.slider.config.width // 2
            self.position.y = (1 - progress) * track_height + self.slider.style.handle_size // 2
    
    def update_value_from_position(self):
        """Update value based on current position"""
        if self.slider.config_slider.orientation == SliderOrientation.HORIZONTAL:
            track_width = self.slider.config.width - self.slider.style.handle_size
            progress = (self.position.x - self.slider.style.handle_size // 2) / track_width
        else:
            track_height = self.slider.config.height - self.slider.style.handle_size
            progress = 1 - (self.position.y - self.slider.style.handle_size // 2) / track_height
        
        progress = GeometryUtils.clamp(progress, 0.0, 1.0)
        
        if self.slider.config_slider.slider_type == SliderType.LOG_SCALE:
            # Logarithmic scale
            log_min = math.log10(max(self.slider.min_value, 0.1))
            log_max = math.log10(self.slider.max_value)
            log_value = log_min + progress * (log_max - log_min)
            self.value = math.pow(10, log_value)
        else:
            # Linear scale
            self.value = self.slider.min_value + progress * (self.slider.max_value - self.slider.min_value)
        
        # Apply step constraints
        if self.slider.step_size > 0:
            self.value = round(self.value / self.slider.step_size) * self.slider.step_size
        
        # Clamp to bounds
        self.value = GeometryUtils.clamp(self.value, self.slider.min_value, self.slider.max_value)
    
    def animate_to_value(self, target_value: float, duration: float = None):
        """Animate handle to specific value"""
        duration = duration or self.slider.config.animation_duration
        start_value = self.value
        
        def update_value(progress: float):
            self.value = GeometryUtils.lerp(start_value, target_value, progress)
            self.update_position_from_value()
            self.slider.update_appearance()
            self.slider.trigger_callback('value_changed', self.slider.get_values())
        
        config = AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_OUT_CUBIC
        )
        
        self.animation_manager.animate(
            f"value_{self.handle_id}",
            0.0,
            1.0,
            update_value,
            config
        )
    
    def animate_color_transition(self, target_color: Color, duration: float = None):
        """Animate handle color transition"""
        duration = duration or self.slider.config.animation_duration
        start_color = self.current_color
        
        def update_color(progress: float):
            self.current_color = ColorUtils.interpolate_colors(start_color, target_color, progress)
            self.slider.update_appearance()
        
        config = AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_OUT_CUBIC
        )
        
        self.animation_manager.animate(
            f"color_{self.handle_id}",
            0.0,
            1.0,
            update_color,
            config
        )
    
    def animate_scale(self, target_scale: float, duration: float = 0.2):
        """Animate handle scale"""
        start_scale = self.current_scale
        
        def update_scale(progress: float):
            self.current_scale = GeometryUtils.lerp(start_scale, target_scale, progress)
            self.slider.update_appearance()
        
        config = AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_OUT_CUBIC
        )
        
        self.animation_manager.animate(
            f"scale_{self.handle_id}",
            0.0,
            1.0,
            update_scale,
            config
        )
    
    def on_hover_enter(self):
        """Handle mouse enter"""
        if self.slider.get_state() == "disabled":
            return
        
        self.is_hovered = True
        target_color = ColorUtils.parse_color(self.slider.style.handle_hover_color)
        self.animate_color_transition(target_color)
        
        if self.slider.style.handle_hover_scale != 1.0:
            self.animate_scale(self.slider.style.handle_hover_scale)
        
        self.slider.trigger_callback('handle_hover_enter', self.handle_id)
    
    def on_hover_leave(self):
        """Handle mouse leave"""
        if self.slider.get_state() == "disabled":
            return
        
        self.is_hovered = False
        if not self.is_pressed:
            target_color = ColorUtils.parse_color(self.slider.style.handle_color)
            self.animate_color_transition(target_color)
            self.animate_scale(1.0)
        
        self.slider.trigger_callback('handle_hover_leave', self.handle_id)
    
    def on_press(self):
        """Handle mouse press"""
        if self.slider.get_state() == "disabled":
            return
        
        self.is_pressed = True
        self.is_dragging = True
        
        target_color = ColorUtils.parse_color(self.slider.style.handle_pressed_color)
        self.animate_color_transition(target_color, duration=0.1)
        
        if self.slider.style.handle_press_scale != 1.0:
            self.animate_scale(self.slider.style.handle_press_scale, duration=0.1)
        
        self.slider.trigger_callback('handle_press', self.handle_id)
        self.slider.set_state("active")
    
    def on_release(self):
        """Handle mouse release"""
        if self.slider.get_state() == "disabled":
            return
        
        self.is_pressed = False
        self.is_dragging = False
        
        if self.is_hovered:
            target_color = ColorUtils.parse_color(self.slider.style.handle_hover_color)
        else:
            target_color = ColorUtils.parse_color(self.slider.style.handle_color)
        
        self.animate_color_transition(target_color, duration=0.15)
        
        scale = self.slider.style.handle_hover_scale if self.is_hovered else 1.0
        self.animate_scale(scale, duration=0.15)
        
        self.slider.trigger_callback('handle_release', self.handle_id)
        self.slider.set_state("normal")
        
        # Snap to step if enabled
        if self.slider.style.snap_to_steps and self.slider.step_size > 0:
            snapped_value = round(self.value / self.slider.step_size) * self.slider.step_size
            if abs(snapped_value - self.value) > 0.001:
                self.animate_to_value(snapped_value, duration=0.2)
    
    def on_drag(self, new_position: Point):
        """Handle drag movement"""
        if not self.is_dragging or self.slider.get_state() == "disabled":
            return
        
        # Update position
        old_position = Point(self.position.x, self.position.y)
        
        if self.slider.config_slider.orientation == SliderOrientation.HORIZONTAL:
            self.position.x = GeometryUtils.clamp(
                new_position.x,
                self.slider.style.handle_size // 2,
                self.slider.config.width - self.slider.style.handle_size // 2
            )
        else:
            self.position.y = GeometryUtils.clamp(
                new_position.y,
                self.slider.style.handle_size // 2,
                self.slider.config.height - self.slider.style.handle_size // 2
            )
        
        # Update value
        old_value = self.value
        self.update_value_from_position()
        
        # Handle range constraints for range sliders
        if self.slider.config_slider.slider_type == SliderType.RANGE:
            other_handle = None
            for handle in self.slider.handles:
                if handle.handle_id != self.handle_id:
                    other_handle = handle
                    break
            
            if other_handle:
                if self.handle_id == "start" and self.value > other_handle.value:
                    self.value = other_handle.value
                elif self.handle_id == "end" and self.value < other_handle.value:
                    self.value = other_handle.value
                
                self.update_position_from_value()
        
        # Trigger callbacks if value changed
        if abs(self.value - old_value) > 0.001:
            self.slider.update_appearance()
            self.slider.trigger_callback('value_changed', self.slider.get_values())
            self.slider.trigger_callback('handle_drag', self.handle_id, self.value)

@dataclass
class SliderConfig:
    """Extended configuration for sliders"""
    orientation: SliderOrientation = SliderOrientation.HORIZONTAL
    slider_type: SliderType = SliderType.SINGLE
    min_value: float = 0.0
    max_value: float = 100.0
    initial_value: float = 50.0
    initial_range: Tuple[float, float] = (25.0, 75.0)
    step_size: float = 0.0  # 0 = continuous
    precision: int = 2
    value_formatter: Optional[Callable[[float], str]] = None
    value_parser: Optional[Callable[[str], float]] = None
    
    # Validation
    allow_negative: bool = True
    min_range_distance: float = 0.0  # For range sliders
    
    # Interaction
    keyboard_enabled: bool = True
    mouse_wheel_enabled: bool = True
    double_click_reset: bool = False
    right_click_context: bool = False

class AnimatedSlider(AnimatedWidget):
    """
    Advanced animated slider with multiple handle types, orientations,
    and smooth animations. Supports single value, range, stepped, and logarithmic scales.
    """
    
    def __init__(self, 
                 config: Optional[WidgetConfig] = None,
                 config_slider: Optional[SliderConfig] = None,
                 style: Optional[SliderStyle] = None):
        super().__init__(config)
        
        self.config_slider = config_slider or SliderConfig()
        self.style = style or SliderStyle()
        
        # Slider properties
        self.min_value = self.config_slider.min_value
        self.max_value = self.config_slider.max_value
        self.step_size = self.config_slider.step_size
        
        # Create handles based on slider type
        self.handles: List[SliderHandle] = []
        if self.config_slider.slider_type == SliderType.RANGE:
            start_value, end_value = self.config_slider.initial_range
            self.handles.append(SliderHandle(self, "start", start_value))
            self.handles.append(SliderHandle(self, "end", end_value))
        else:
            self.handles.append(SliderHandle(self, "main", self.config_slider.initial_value))
        
        # Initialize handle positions
        for handle in self.handles:
            handle.update_position_from_value()
        
        # Animation manager
        self._animation_manager = AnimationManager()
        
        # GUI components
        self._gui_widget = None
        self._gui_framework = None
        self._canvas = None
        
        # Interaction state
        self._active_handle = None
        self._last_mouse_position = Point(0, 0)
        self._tooltip_visible = False
        self._tooltip_content = ""
        
        # Keyboard state
        self._keyboard_focused = False
        self._keyboard_step_size = None
        
        # Validation
        self._validation_rules = []
        self._last_valid_values = self.get_values()
        
    def render(self, parent_widget, framework: str = "tkinter"):
        """
        Render the slider in the specified GUI framework
        """
        self._gui_framework = framework
        
        if framework == "tkinter":
            self._render_tkinter(parent_widget)
        elif framework == "pyqt5":
            self._render_pyqt5(parent_widget)
        elif framework == "pyqt6":
            self._render_pyqt6(parent_widget)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
        
        return self._gui_widget
    
    def _render_tkinter(self, parent):
        """Render with Tkinter using Canvas"""
        import tkinter as tk
        
        self._gui_widget = tk.Frame(parent, bg=self.config.background_color)
        
        # Create canvas for custom drawing
        self._canvas = tk.Canvas(
            self._gui_widget,
            width=self.config.width,
            height=self.config.height,
            bg=self.config.background_color,
            highlightthickness=0,
            bd=0
        )
        self._canvas.pack(fill="both", expand=True)
        
        # Bind events
        self._canvas.bind("<Button-1>", self._on_click_tkinter)
        self._canvas.bind("<B1-Motion>", self._on_drag_tkinter)
        self._canvas.bind("<ButtonRelease-1>", self._on_release_tkinter)
        self._canvas.bind("<Motion>", self._on_motion_tkinter)
        self._canvas.bind("<Leave>", self._on_leave_tkinter)
        self._canvas.bind("<Double-Button-1>", self._on_double_click_tkinter)
        
        if self.config_slider.mouse_wheel_enabled:
            self._canvas.bind("<MouseWheel>", self._on_scroll_tkinter)
            self._canvas.bind("<Button-4>", self._on_scroll_tkinter)
            self._canvas.bind("<Button-5>", self._on_scroll_tkinter)
        
        if self.config_slider.keyboard_enabled:
            self._canvas.bind("<KeyPress>", self._on_key_press_tkinter)
            self._canvas.bind("<FocusIn>", self._on_focus_in_tkinter)
            self._canvas.bind("<FocusOut>", self._on_focus_out_tkinter)
            self._canvas.configure(takefocus=1)
        
        # Initial draw
        self.update_appearance()
    
    def _render_pyqt5(self, parent):
        """Render with PyQt5"""
        try:
            from PyQt5.QtWidgets import QWidget, QVBoxLayout
            from PyQt5.QtCore import Qt, QTimer
            from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
        except ImportError:
            raise ImportError("PyQt5 not installed. Install with: pip install PyQt5")
        
        self._gui_widget = SliderWidgetQt5(self, parent)
        self._gui_widget.setFixedSize(self.config.width, self.config.height)
        
        # Update appearance
        self.update_appearance()
    
    def _render_pyqt6(self, parent):
        """Render with PyQt6"""
        try:
            from PyQt6.QtWidgets import QWidget, QVBoxLayout
            from PyQt6.QtCore import Qt, QTimer
            from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
        except ImportError:
            raise ImportError("PyQt6 not installed. Install with: pip install PyQt6")
        
        self._gui_widget = SliderWidgetQt6(self, parent)
        self._gui_widget.setFixedSize(self.config.width, self.config.height)
        
        # Update appearance
        self.update_appearance()
    
    def update_appearance(self):
        """Update slider visual appearance"""
        if not self._canvas and not hasattr(self._gui_widget, 'update'):
            return
        
        if self._gui_framework == "tkinter":
            self._draw_tkinter()
        elif self._gui_framework in ["pyqt5", "pyqt6"]:
            self._gui_widget.update()
    
    def _draw_tkinter(self):
        """Draw slider using Tkinter Canvas"""
        if not self._canvas:
            return
        
        # Clear canvas
        self._canvas.delete("all")
        
        # Draw track
        self._draw_track_tkinter()
        
        # Draw active track section
        self._draw_active_track_tkinter()
        
        # Draw ticks if enabled
        if self.style.show_ticks:
            self._draw_ticks_tkinter()
        
        # Draw handles
        for handle in self.handles:
            self._draw_handle_tkinter(handle)
        
        # Draw labels
        if self.style.show_value_label or self.style.show_min_max_labels:
            self._draw_labels_tkinter()
        
        # Draw tooltip if visible
        if self._tooltip_visible and self._tooltip_content:
            self._draw_tooltip_tkinter()
    
    def _draw_track_tkinter(self):
        """Draw slider track"""
        if self.config_slider.orientation == SliderOrientation.HORIZONTAL:
            x1 = self.style.handle_size // 2
            x2 = self.config.width - self.style.handle_size // 2
            y = self.config.height // 2
            
            # Background track
            self._canvas.create_rectangle(
                x1, y - self.style.track_height // 2,
                x2, y + self.style.track_height // 2,
                fill=self.style.track_color,
                outline=self.style.track_border_color if self.style.track_border_width > 0 else "",
                width=self.style.track_border_width
            )
        else:
            x = self.config.width // 2
            y1 = self.style.handle_size // 2
            y2 = self.config.height - self.style.handle_size // 2
            
            # Background track
            self._canvas.create_rectangle(
                x - self.style.track_height // 2, y1,
                x + self.style.track_height // 2, y2,
                fill=self.style.track_color,
                outline=self.style.track_border_color if self.style.track_border_width > 0 else "",
                width=self.style.track_border_width
            )
    
    def _draw_active_track_tkinter(self):
        """Draw active portion of track"""
        if self.config_slider.slider_type == SliderType.RANGE:
            # Range slider - draw between handles
            start_handle = next(h for h in self.handles if h.handle_id == "start")
            end_handle = next(h for h in self.handles if h.handle_id == "end")
            
            if self.config_slider.orientation == SliderOrientation.HORIZONTAL:
                x1 = start_handle.position.x
                x2 = end_handle.position.x
                y = self.config.height // 2
                
                self._canvas.create_rectangle(
                    x1, y - self.style.track_height // 2,
                    x2, y + self.style.track_height // 2,
                    fill=self.style.track_active_color,
                    outline=""
                )
            else:
                x = self.config.width // 2
                y1 = end_handle.position.y
                y2 = start_handle.position.y
                
                self._canvas.create_rectangle(
                    x - self.style.track_height // 2, y1,
                    x + self.style.track_height // 2, y2,
                    fill=self.style.track_active_color,
                    outline=""
                )
        else:
            # Single handle - draw from start to handle
            handle = self.handles[0]
            
            if self.config_slider.orientation == SliderOrientation.HORIZONTAL:
                x1 = self.style.handle_size // 2
                x2 = handle.position.x
                y = self.config.height // 2
                
                self._canvas.create_rectangle(
                    x1, y - self.style.track_height // 2,
                    x2, y + self.style.track_height // 2,
                    fill=self.style.track_active_color,
                    outline=""
                )
            else:
                x = self.config.width // 2
                y1 = handle.position.y
                y2 = self.config.height - self.style.handle_size // 2
                
                self._canvas.create_rectangle(
                    x - self.style.track_height // 2, y1,
                    x + self.style.track_height // 2, y2,
                    fill=self.style.track_active_color,
                    outline=""
                )
    
    def _draw_ticks_tkinter(self):
        """Draw tick marks"""
        tick_count = self.style.tick_count
        
        for i in range(tick_count + 1):
            progress = i / tick_count
            
            if self.config_slider.orientation == SliderOrientation.HORIZONTAL:
                x = self.style.handle_size // 2 + progress * (self.config.width - self.style.handle_size)
                y_center = self.config.height // 2
                
                self._canvas.create_line(
                    x, y_center - self.style.tick_height // 2,
                    x, y_center + self.style.tick_height // 2,
                    fill=self.style.tick_color,
                    width=1
                )
            else:
                x_center = self.config.width // 2
                y = self.style.handle_size // 2 + (1 - progress) * (self.config.height - self.style.handle_size)
                
                self._canvas.create_line(
                    x_center - self.style.tick_height // 2, y,
                    x_center + self.style.tick_height // 2, y,
                    fill=self.style.tick_color,
                    width=1
                )
    
    def _draw_handle_tkinter(self, handle: SliderHandle):
        """Draw a slider handle"""
        x, y = handle.position.x, handle.position.y
        size = self.style.handle_size * handle.current_scale
        
        # Draw shadow if enabled
        if self.style.handle_shadow:
            shadow_x = x + self.style.handle_shadow_offset[0]
            shadow_y = y + self.style.handle_shadow_offset[1]
            
            # Convert shadow color to supported format for Tkinter
            shadow_color = self.style.handle_shadow_color
            if shadow_color.startswith("#") and len(shadow_color) > 7:
                # Remove alpha channel for Tkinter compatibility
                shadow_color = shadow_color[:7]
            
            # Use a lighter gray for shadow if color is invalid
            try:
                if self.style.handle_shape == HandleShape.CIRCLE:
                    self._canvas.create_oval(
                        shadow_x - size // 2, shadow_y - size // 2,
                        shadow_x + size // 2, shadow_y + size // 2,
                        fill=shadow_color,
                        outline=""
                    )
            except:
                # Fallback to gray shadow
                if self.style.handle_shape == HandleShape.CIRCLE:
                    self._canvas.create_oval(
                        shadow_x - size // 2, shadow_y - size // 2,
                        shadow_x + size // 2, shadow_y + size // 2,
                        fill="#cccccc",
                        outline=""
                    )
        
        # Draw handle
        if self.style.handle_shape == HandleShape.CIRCLE:
            self._canvas.create_oval(
                x - size // 2, y - size // 2,
                x + size // 2, y + size // 2,
                fill=handle.current_color.to_hex(),
                outline=self.style.handle_border_color,
                width=self.style.handle_border_width
            )
        elif self.style.handle_shape == HandleShape.SQUARE:
            self._canvas.create_rectangle(
                x - size // 2, y - size // 2,
                x + size // 2, y + size // 2,
                fill=handle.current_color.to_hex(),
                outline=self.style.handle_border_color,
                width=self.style.handle_border_width
            )
        elif self.style.handle_shape == HandleShape.DIAMOND:
            points = [
                x, y - size // 2,  # top
                x + size // 2, y,  # right
                x, y + size // 2,  # bottom
                x - size // 2, y   # left
            ]
            self._canvas.create_polygon(
                points,
                fill=handle.current_color.to_hex(),
                outline=self.style.handle_border_color,
                width=self.style.handle_border_width
            )
    

    def _draw_labels_tkinter(self):
        """Draw value labels"""
        if self.style.show_min_max_labels:
            # Min label
            min_text = self._format_value(self.min_value)
            if self.config_slider.orientation == SliderOrientation.HORIZONTAL:
                self._canvas.create_text(
                    self.style.handle_size // 2,
                    self.config.height - 15,
                    text=min_text,
                    fill=self.style.label_color,
                    font=("Arial", self.style.label_font_size)
                )
                
                # Max label
                max_text = self._format_value(self.max_value)
                self._canvas.create_text(
                    self.config.width - self.style.handle_size // 2,
                    self.config.height - 15,
                    text=max_text,
                    fill=self.style.label_color,
                    font=("Arial", self.style.label_font_size)
                )
        
        if self.style.show_value_label:
            # Current value label(s)
            for handle in self.handles:
                value_text = self._format_value(handle.value)
                
                if self.config_slider.orientation == SliderOrientation.HORIZONTAL:
                    self._canvas.create_text(
                        handle.position.x,
                        handle.position.y - self.style.handle_size // 2 - 15,
                        text=value_text,
                        fill=self.style.label_color,
                        font=("Arial", self.style.label_font_size)
                    )
                else:
                    self._canvas.create_text(
                        handle.position.x + self.style.handle_size // 2 + 20,
                        handle.position.y,
                        text=value_text,
                        fill=self.style.label_color,
                        font=("Arial", self.style.label_font_size)
                    )
    
    def _draw_tooltip_tkinter(self):
        """Draw tooltip near active handle"""
        if not self._active_handle:
            return
        
        # Calculate tooltip position
        handle = self._active_handle
        tooltip_x = handle.position.x
        tooltip_y = handle.position.y - self.style.handle_size - 25
        
        # Create tooltip background
        text_width = len(self._tooltip_content) * 8
        text_height = 16
        
        self._canvas.create_rectangle(
            tooltip_x - text_width // 2 - self.style.tooltip_padding,
            tooltip_y - text_height // 2 - self.style.tooltip_padding,
            tooltip_x + text_width // 2 + self.style.tooltip_padding,
            tooltip_y + text_height // 2 + self.style.tooltip_padding,
            fill=self.style.tooltip_background,
            outline="",
            tags="tooltip"
        )
        
        # Create tooltip text
        self._canvas.create_text(
            tooltip_x, tooltip_y,
            text=self._tooltip_content,
            fill=self.style.tooltip_text_color,
            font=("Arial", self.style.label_font_size),
            tags="tooltip"
        )
    
    # Event handlers for Tkinter
    def _on_click_tkinter(self, event):
        """Handle mouse click"""
        if self.get_state() == "disabled":
            return
        
        click_point = Point(event.x, event.y)
        self._active_handle = self._find_closest_handle(click_point)
        
        if self._active_handle:
            self._active_handle.on_press()
            self._show_tooltip(self._format_value(self._active_handle.value))
        else:
            # Click on track - move closest handle
            closest_handle = min(self.handles, 
                               key=lambda h: GeometryUtils.distance(h.position, click_point))
            
            # Calculate target value
            if self.config_slider.orientation == SliderOrientation.HORIZONTAL:
                track_width = self.config.width - self.style.handle_size
                progress = (event.x - self.style.handle_size // 2) / track_width
            else:
                track_height = self.config.height - self.style.handle_size
                progress = 1 - (event.y - self.style.handle_size // 2) / track_height
            
            progress = GeometryUtils.clamp(progress, 0.0, 1.0)
            target_value = self.min_value + progress * (self.max_value - self.min_value)
            
            # Animate to target
            closest_handle.animate_to_value(target_value)
    
    def _on_drag_tkinter(self, event):
        """Handle mouse drag"""
        if self._active_handle and self._active_handle.is_dragging:
            new_position = Point(event.x, event.y)
            self._active_handle.on_drag(new_position)
            
            # Update tooltip
            self._show_tooltip(self._format_value(self._active_handle.value))
    
    def _on_release_tkinter(self, event):
        """Handle mouse release"""
        if self._active_handle:
            self._active_handle.on_release()
            self._hide_tooltip()
            self._active_handle = None
    
    def _on_motion_tkinter(self, event):
        """Handle mouse motion"""
        if self._active_handle and self._active_handle.is_dragging:
            return
        
        mouse_point = Point(event.x, event.y)
        
        # Check hover states
        for handle in self.handles:
            distance = GeometryUtils.distance(handle.position, mouse_point)
            
            if distance <= self.style.handle_size:
                if not handle.is_hovered:
                    handle.on_hover_enter()
            else:
                if handle.is_hovered:
                    handle.on_hover_leave()
    
    def _on_leave_tkinter(self, event):
        """Handle mouse leave"""
        for handle in self.handles:
            if handle.is_hovered:
                handle.on_hover_leave()
        
        self._hide_tooltip()
    
    def _on_double_click_tkinter(self, event):
        """Handle double click"""
        if self.config_slider.double_click_reset:
            if self.config_slider.slider_type == SliderType.RANGE:
                start_val, end_val = self.config_slider.initial_range
                self.set_range_values(start_val, end_val, animate=True)
            else:
                self.set_value(self.config_slider.initial_value, animate=True)
    
    def _on_scroll_tkinter(self, event):
        """Handle mouse wheel scroll"""
        if not self.config_slider.mouse_wheel_enabled:
            return
        
        # Determine scroll direction
        if event.delta:
            delta = event.delta / 120  # Windows
        elif event.num == 4:
            delta = 1  # Linux scroll up
        elif event.num == 5:
            delta = -1  # Linux scroll down
        else:
            return
        
        # Calculate step size
        step = self.step_size if self.step_size > 0 else (self.max_value - self.min_value) / 100
        step *= delta
        
        # Find handle to adjust
        mouse_point = Point(event.x, event.y)
        closest_handle = min(self.handles, 
                           key=lambda h: GeometryUtils.distance(h.position, mouse_point))
        
        # Adjust value
        new_value = GeometryUtils.clamp(
            closest_handle.value + step,
            self.min_value,
            self.max_value
        )
        
        closest_handle.animate_to_value(new_value)
    
    def _on_key_press_tkinter(self, event):
        """Handle keyboard input"""
        if not self.config_slider.keyboard_enabled or self.get_state() == "disabled":
            return
        
        # Calculate step size
        step = self.step_size if self.step_size > 0 else (self.max_value - self.min_value) / 100
        
        # Modify step based on modifiers
        if event.state & 0x4:  # Ctrl key
            step *= 10
        elif event.state & 0x1:  # Shift key
            step /= 10
        
        # Determine which handle to move
        active_handle = self.handles[0]  # Default to first handle
        
        # Handle key presses
        if event.keysym in ['Left', 'Down']:
            new_value = GeometryUtils.clamp(
                active_handle.value - step,
                self.min_value,
                self.max_value
            )
            active_handle.animate_to_value(new_value)
        elif event.keysym in ['Right', 'Up']:
            new_value = GeometryUtils.clamp(
                active_handle.value + step,
                self.min_value,
                self.max_value
            )
            active_handle.animate_to_value(new_value)
        elif event.keysym == 'Home':
            active_handle.animate_to_value(self.min_value)
        elif event.keysym == 'End':
            active_handle.animate_to_value(self.max_value)
    
    def _on_focus_in_tkinter(self, event):
        """Handle focus in"""
        self._keyboard_focused = True
        self.trigger_callback('focus_in')
    
    def _on_focus_out_tkinter(self, event):
        """Handle focus out"""
        self._keyboard_focused = False
        self.trigger_callback('focus_out')
    
    # Utility methods
    def _find_closest_handle(self, point: Point) -> Optional[SliderHandle]:
        """Find the handle closest to a point"""
        closest_handle = None
        min_distance = float('inf')
        
        for handle in self.handles:
            distance = GeometryUtils.distance(handle.position, point)
            if distance <= self.style.handle_size and distance < min_distance:
                min_distance = distance
                closest_handle = handle
        
        return closest_handle
    
    def _format_value(self, value: float) -> str:
        """Format value for display"""
        if self.config_slider.value_formatter:
            return self.config_slider.value_formatter(value)
        
        if self.config_slider.precision == 0:
            return str(int(value))
        else:
            return f"{value:.{self.config_slider.precision}f}"
    
    def _show_tooltip(self, content: str):
        """Show tooltip with content"""
        if self.style.show_tooltip:
            self._tooltip_visible = True
            self._tooltip_content = content
    
    def _hide_tooltip(self):
        """Hide tooltip"""
        self._tooltip_visible = False
        self._tooltip_content = ""
        if self._canvas:
            self._canvas.delete("tooltip")
    
    # Public API methods
    def get_value(self) -> float:
        """Get single slider value"""
        return self.handles[0].value
    
    def get_values(self) -> Union[float, Tuple[float, float]]:
        """Get slider value(s)"""
        if self.config_slider.slider_type == SliderType.RANGE:
            start_handle = next(h for h in self.handles if h.handle_id == "start")
            end_handle = next(h for h in self.handles if h.handle_id == "end")
            return (start_handle.value, end_handle.value)
        else:
            return self.handles[0].value
    
    def set_value(self, value: float, animate: bool = False):
        """Set single slider value"""
        if self.config_slider.slider_type == SliderType.RANGE:
            raise ValueError("Use set_range_values() for range sliders")
        
        value = GeometryUtils.clamp(value, self.min_value, self.max_value)
        
        if animate:
            self.handles[0].animate_to_value(value)
        else:
            self.handles[0].value = value
            self.handles[0].update_position_from_value()
            self.update_appearance()
            self.trigger_callback('value_changed', value)
    
    def set_range_values(self, start_value: float, end_value: float, animate: bool = False):
        """Set range slider values"""
        if self.config_slider.slider_type != SliderType.RANGE:
            raise ValueError("This method only works with range sliders")
        
        start_value = GeometryUtils.clamp(start_value, self.min_value, self.max_value)
        end_value = GeometryUtils.clamp(end_value, self.min_value, self.max_value)
        
        # Ensure proper order
        if start_value > end_value:
            start_value, end_value = end_value, start_value
        
        start_handle = next(h for h in self.handles if h.handle_id == "start")
        end_handle = next(h for h in self.handles if h.handle_id == "end")
        
        if animate:
            start_handle.animate_to_value(start_value)
            end_handle.animate_to_value(end_value)
        else:
            start_handle.value = start_value
            end_handle.value = end_value
            start_handle.update_position_from_value()
            end_handle.update_position_from_value()
            self.update_appearance()
            self.trigger_callback('value_changed', (start_value, end_value))
    
    def set_min_max(self, min_value: float, max_value: float):
        """Set minimum and maximum values"""
        if min_value >= max_value:
            raise ValueError("min_value must be less than max_value")
        
        self.min_value = min_value
        self.max_value = max_value
        
        # Clamp current values to new range
        for handle in self.handles:
            handle.value = GeometryUtils.clamp(handle.value, min_value, max_value)
            handle.update_position_from_value()
        
        self.update_appearance()
    
    def add_validation_rule(self, rule: Callable[[Union[float, Tuple[float, float]]], bool]):
        """Add validation rule"""
        self._validation_rules.append(rule)
    
    def validate_values(self) -> bool:
        """Validate current values against rules"""
        current_values = self.get_values()
        
        for rule in self._validation_rules:
            if not rule(current_values):
                return False
        
        return True
    
    def reset_to_defaults(self, animate: bool = True):
        """Reset slider to default values"""
        if self.config_slider.slider_type == SliderType.RANGE:
            start_val, end_val = self.config_slider.initial_range
            self.set_range_values(start_val, end_val, animate)
        else:
            self.set_value(self.config_slider.initial_value, animate)
    
    def enable_discrete_mode(self, steps: List[float]):
        """Enable discrete stepping mode"""
        self._discrete_steps = sorted(steps)
        self.step_size = -1  # Special value indicating discrete mode
    
    def disable_discrete_mode(self):
        """Disable discrete stepping mode"""
        if hasattr(self, '_discrete_steps'):
            delattr(self, '_discrete_steps')
        self.step_size = 0
    
    def get_step_values(self) -> List[float]:
        """Get available step values"""
        if hasattr(self, '_discrete_steps'):
            return self._discrete_steps.copy()
        elif self.step_size > 0:
            steps = []
            current = self.min_value
            while current <= self.max_value:
                steps.append(current)
                current += self.step_size
            return steps
        else:
            return []
    
    def animate_to_percentage(self, percentage: float, duration: float = None):
        """Animate to percentage of range (0-100)"""
        percentage = GeometryUtils.clamp(percentage, 0, 100)
        target_value = self.min_value + (percentage / 100) * (self.max_value - self.min_value)
        
        if self.config_slider.slider_type == SliderType.RANGE:
            # For range sliders, animate both handles proportionally
            current_start, current_end = self.get_values()
            current_range = current_end - current_start
            
            new_start = target_value - current_range / 2
            new_end = target_value + current_range / 2
            
            # Adjust if out of bounds
            if new_start < self.min_value:
                new_start = self.min_value
                new_end = new_start + current_range
            elif new_end > self.max_value:
                new_end = self.max_value
                new_start = new_end - current_range
            
            self.set_range_values(new_start, new_end, animate=True)
        else:
            self.set_value(target_value, animate=True)
    
    def get_percentage(self) -> Union[float, Tuple[float, float]]:
        """Get current value(s) as percentage"""
        if self.config_slider.slider_type == SliderType.RANGE:
            start_val, end_val = self.get_values()
            start_pct = (start_val - self.min_value) / (self.max_value - self.min_value) * 100
            end_pct = (end_val - self.min_value) / (self.max_value - self.min_value) * 100
            return (start_pct, end_pct)
        else:
            value = self.get_value()
            return (value - self.min_value) / (self.max_value - self.min_value) * 100
    
    # Callback binding methods
    def on_value_changed(self, callback: Callable):
        """Bind value changed callback"""
        self.bind_callback('value_changed', callback)
        return self
    
    def on_handle_hover(self, callback: Callable):
        """Bind handle hover callbacks"""
        self.bind_callback('handle_hover_enter', callback)
        self.bind_callback('handle_hover_leave', callback)
        return self
    
    def on_drag_start(self, callback: Callable):
        """Bind drag start callback"""
        self.bind_callback('handle_press', callback)
        return self
    
    def on_drag_end(self, callback: Callable):
        """Bind drag end callback"""
        self.bind_callback('handle_release', callback)
        return self
    
    def stop_all_animations(self):
        """Stop all slider animations"""
        self._animation_manager.stop_all_animations()
        
        for handle in self.handles:
            handle.animation_manager.stop_all_animations()
        
        super().stop_all_animations()
    
    def __del__(self):
        """Cleanup when slider is destroyed"""
        if hasattr(self, '_animation_manager'):
            self._animation_manager.stop_all_animations()
        
        for handle in self.handles:
            if hasattr(handle, 'animation_manager'):
                handle.animation_manager.stop_all_animations()


# PyQt5 Widget Implementation
class SliderWidgetQt5:
    """PyQt5 implementation of slider widget"""
    
    def __init__(self, slider: AnimatedSlider, parent):
        try:
            from PyQt5.QtWidgets import QWidget
            from PyQt5.QtCore import Qt, QTimer, pyqtSignal
            from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
        except ImportError:
            raise ImportError("PyQt5 not installed")
        
        class SliderWidget(QWidget):
            def __init__(self, slider_instance, parent):
                super().__init__(parent)
                self.slider = slider_instance
                self.setMouseTracking(True)
                self.setFocusPolicy(Qt.StrongFocus)
            
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Draw track
                self._draw_track_qt(painter)
                
                # Draw active track
                self._draw_active_track_qt(painter)
                
                # Draw handles
                for handle in self.slider.handles:
                    self._draw_handle_qt(painter, handle)
            
            def _draw_track_qt(self, painter):
                # Implementation similar to tkinter version but using QPainter
                pass
            
            def _draw_active_track_qt(self, painter):
                # Implementation for active track
                pass
            
            def _draw_handle_qt(self, painter, handle):
                # Implementation for handle drawing
                pass
        
        self._widget = SliderWidget(slider, parent)
        return self._widget


# PyQt6 Widget Implementation  
class SliderWidgetQt6:
    """PyQt6 implementation of slider widget"""
    
    def __init__(self, slider: AnimatedSlider, parent):
        try:
            from PyQt6.QtWidgets import QWidget
            from PyQt6.QtCore import Qt, QTimer, pyqtSignal
            from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
        except ImportError:
            raise ImportError("PyQt6 not installed")
        
        # Similar implementation to PyQt5 but with PyQt6 imports
        pass


# Utility functions for common slider configurations
def create_horizontal_slider(min_val: float = 0, max_val: float = 100, 
                           initial_val: float = 50, width: int = 300) -> AnimatedSlider:
    """Create a horizontal slider with common settings"""
    config = WidgetConfig(width=width, height=60)
    slider_config = SliderConfig(
        orientation=SliderOrientation.HORIZONTAL,
        min_value=min_val,
        max_value=max_val,
        initial_value=initial_val
    )
    return AnimatedSlider(config=config, config_slider=slider_config)


def create_vertical_slider(min_val: float = 0, max_val: float = 100,
                         initial_val: float = 50, height: int = 300) -> AnimatedSlider:
    """Create a vertical slider with common settings"""
    config = WidgetConfig(width=60, height=height)
    slider_config = SliderConfig(
        orientation=SliderOrientation.VERTICAL,
        min_value=min_val,
        max_value=max_val,
        initial_value=initial_val
    )
    return AnimatedSlider(config=config, config_slider=slider_config)


def create_range_slider(min_val: float = 0, max_val: float = 100,
                       initial_range: Tuple[float, float] = (25, 75),
                       width: int = 300) -> AnimatedSlider:
    """Create a range slider with common settings"""
    config = WidgetConfig(width=width, height=60)
    slider_config = SliderConfig(
        orientation=SliderOrientation.HORIZONTAL,
        slider_type=SliderType.RANGE,
        min_value=min_val,
        max_value=max_val,
        initial_range=initial_range
    )
    return AnimatedSlider(config=config, config_slider=slider_config)


def create_stepped_slider(min_val: float = 0, max_val: float = 100,
                         step_size: float = 10, width: int = 300) -> AnimatedSlider:
    """Create a stepped slider with common settings"""
    config = WidgetConfig(width=width, height=60)
    slider_config = SliderConfig(
        orientation=SliderOrientation.HORIZONTAL,
        slider_type=SliderType.STEPPED,
        min_value=min_val,
        max_value=max_val,
        step_size=step_size,
        initial_value=min_val + step_size
    )
    style = SliderStyle(snap_to_steps=True, show_ticks=True)
    return AnimatedSlider(config=config, config_slider=slider_config, style=style)


def create_log_slider(min_val: float = 1, max_val: float = 1000,
                     initial_val: float = 10, width: int = 300) -> AnimatedSlider:
    """Create a logarithmic slider with common settings"""
    config = WidgetConfig(width=width, height=60)
    slider_config = SliderConfig(
        orientation=SliderOrientation.HORIZONTAL,
        slider_type=SliderType.LOG_SCALE,
        min_value=min_val,
        max_value=max_val,
        initial_value=initial_val,
        precision=1
    )
    return AnimatedSlider(config=config, config_slider=slider_config)


# Preset styles
class SliderPresets:
    """Predefined slider styles"""
    
    @staticmethod
    def material_design() -> SliderStyle:
        """Material Design inspired slider"""
        return SliderStyle(
            track_color="#e0e0e0",
            track_active_color="#2196f3",
            handle_color="#2196f3",
            handle_hover_color="#1976d2",
            handle_pressed_color="#0d47a1",
            handle_size=24,
            track_height=4,
            handle_hover_scale=1.2,
            handle_press_scale=0.9,
            show_tooltip=True
        )
    
    @staticmethod
    def flat_design() -> SliderStyle:
        """Flat design slider"""
        return SliderStyle(
            track_color="#bdc3c7",
            track_active_color="#3498db",
            handle_color="#3498db",
            handle_hover_color="#2980b9",
            handle_pressed_color="#21618c",
            handle_size=20,
            track_height=6,
            handle_border_width=0,
            handle_shadow=False,
            handle_hover_scale=1.1
        )
    
    @staticmethod
    def neumorphism() -> SliderStyle:
        """Neumorphism design slider"""
        return SliderStyle(
            track_color="#e0e5ec",
            track_active_color="#a8c5e0",
            handle_color="#e0e5ec",
            handle_hover_color="#f0f5fc",
            handle_pressed_color="#d0d5dc",
            handle_size=28,
            track_height=8,
            track_style=TrackStyle.INSET,
            handle_border_width=0,
            handle_shadow=True,
            handle_shadow_color="#a3b1c6",
            handle_shadow_offset=(2, 2),
            handle_shadow_blur=6
        )
    
    @staticmethod
    def dark_theme() -> SliderStyle:
        """Dark theme slider"""
        return SliderStyle(
            track_color="#4a4a4a",
            track_active_color="#bb86fc",
            handle_color="#bb86fc",
            handle_hover_color="#985fbf",
            handle_pressed_color="#7b1fa2",
            handle_size=22,
            track_height=6,
            label_color="#ffffff",
            tick_color="#888888",
            tooltip_background="#333333",
            tooltip_text_color="#ffffff"
        )
    
    @staticmethod
    def minimal() -> SliderStyle:
        """Minimal design slider"""
        return SliderStyle(
            track_color="#f5f5f5",
            track_active_color="#333333",
            handle_color="#333333",
            handle_hover_color="#000000",
            handle_pressed_color="#666666",
            handle_size=16,
            track_height=2,
            handle_border_width=0,
            handle_shadow=False,
            show_value_label=False,
            show_tooltip=False,
            handle_hover_scale=1.0
        )


# Animation presets
def create_bounce_slider(width: int = 300) -> AnimatedSlider:
    """Create slider with bouncy animations"""
    config = WidgetConfig(width=width, height=60, animation_duration=0.4)
    slider_config = SliderConfig(orientation=SliderOrientation.HORIZONTAL)
    style = SliderStyle(handle_hover_scale=1.3, handle_press_scale=0.8)
    
    slider = AnimatedSlider(config=config, config_slider=slider_config, style=style)
    
    # Override animation easing for bouncy effect
    for handle in slider.handles:
        handle.animation_manager._easing_functions[EasingType.EASE_OUT_CUBIC] = lambda t: 1 - (1 - t) ** 3
    
    return slider


def create_smooth_slider(width: int = 300) -> AnimatedSlider:
    """Create slider with very smooth animations"""
    config = WidgetConfig(width=width, height=60, animation_duration=0.6)
    slider_config = SliderConfig(orientation=SliderOrientation.HORIZONTAL)
    style = SliderStyle(smooth_dragging=True, handle_hover_scale=1.1)
    
    return AnimatedSlider(config=config, config_slider=slider_config, style=style)