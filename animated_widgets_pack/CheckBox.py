"""
Module checkbox - Animated checkbox with smooth transitions
"""

import math
import time
import threading
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional, List
from enum import Enum
from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, AnimationConfig, EasingType
from .utils import ColorUtils, Color, Rectangle, Point, GeometryUtils

class CheckboxState(Enum):
    """Checkbox states"""
    UNCHECKED = "unchecked"
    CHECKED = "checked"
    INDETERMINATE = "indeterminate"  # For tri-state checkboxes

class CheckboxAnimation(Enum):
    """Types of checkbox animations"""
    SCALE = "scale"
    FADE = "fade"
    SLIDE = "slide"
    BOUNCE = "bounce"
    FILL = "fill"
    CHECKMARK_DRAW = "checkmark_draw"

@dataclass
class CheckboxStyle:
    """Checkbox-specific styling"""
    # Colors
    unchecked_color: str = "#bdc3c7"
    checked_color: str = "#3498db"
    indeterminate_color: str = "#f39c12"
    hover_color: str = "#2980b9"
    disabled_color: str = "#ecf0f1"
    
    # Checkmark colors
    checkmark_color: str = "#ffffff"
    checkmark_hover_color: str = "#ffffff"
    
    # Border
    border_width: int = 2
    border_radius: int = 4
    border_color: str = "#bdc3c7"
    checked_border_color: str = "#3498db"
    
    # Size and spacing
    size: int = 20
    checkmark_size: float = 0.6  # Relative to checkbox size
    label_spacing: int = 8
    
    # Animation properties
    animation_type: CheckboxAnimation = CheckboxAnimation.SCALE
    check_animation_duration: float = 0.3
    hover_animation_duration: float = 0.2
    
    # Effects
    hover_scale: float = 1.1
    check_scale: float = 0.9  # Scale during check animation
    shadow_enabled: bool = True
    shadow_color: str = "#34495e"
    shadow_blur: int = 4
    
    # Label properties
    label_text: str = ""
    label_color: str = "#2c3e50"
    label_font_size: int = 12
    label_position: str = "right"  # "left", "right", "top", "bottom"
    
    # Tri-state properties
    tri_state: bool = False
    indeterminate_symbol: str = "—"  # Symbol for indeterminate state

class CheckboxRippleEffect:
    """Ripple effect for modern checkbox interaction"""
    
    def __init__(self, center: Point, max_radius: float):
        self.center = center
        self.max_radius = max_radius
        self.current_radius = 0.0
        self.opacity = 1.0
        self.active = False
    
    def start(self, animation_manager: AnimationManager):
        """Start ripple animation"""
        self.active = True
        
        # Radius animation
        animation_manager.animate(
            "ripple_radius",
            0.0,
            self.max_radius,
            lambda r: setattr(self, 'current_radius', r),
            AnimationConfig(duration=0.4, easing=EasingType.EASE_OUT_QUAD)
        )
        
        # Opacity fade out
        animation_manager.animate(
            "ripple_opacity",
            1.0,
            0.0,
            lambda o: setattr(self, 'opacity', o),
            AnimationConfig(duration=0.4, easing=EasingType.EASE_OUT_QUAD),
            completion_callback=lambda: setattr(self, 'active', False)
        )

class AnimatedCheckbox(AnimatedWidget):
    """
    Animated checkbox with smooth state transitions and multiple animation styles
    Supports standard and tri-state modes with customizable appearance
    """
    
    def __init__(self, label: str = "", checked: bool = False,
                 config: Optional[WidgetConfig] = None, style: Optional[CheckboxStyle] = None):
        super().__init__(config)
        
        self.style = style or CheckboxStyle()
        self.style.label_text = label
        
        # Internal state
        self._current_state = CheckboxState.CHECKED if checked else CheckboxState.UNCHECKED
        self._is_hovered = False
        self._is_pressed = False
        
        # Animation properties
        self._current_scale = 1.0
        self._current_opacity = 1.0
        self._checkmark_progress = 1.0 if checked else 0.0
        self._fill_progress = 1.0 if checked else 0.0
        self._current_color = ColorUtils.parse_color(
            self.style.checked_color if checked else self.style.unchecked_color
        )
        self._current_border_color = ColorUtils.parse_color(
            self.style.checked_border_color if checked else self.style.border_color
        )
        
        # Ripple effect
        self._ripple_effects: List[CheckboxRippleEffect] = []
        
        # Animation manager
        self._animation_manager = AnimationManager()
        
        # GUI widget references
        self._gui_widget = None
        self._gui_framework = None
        self._checkbox_canvas = None
        self._label_widget = None
        self._container_widget = None
        
        # Geometry
        self._checkbox_rect = Rectangle(0, 0, self.style.size, self.style.size)
        self._checkmark_points: List[Point] = []
        
        self._calculate_checkmark_points()
    
    def _calculate_checkmark_points(self):
        """Calculate checkmark path points"""
        size = self.style.size * self.style.checkmark_size
        center = self.style.size / 2
        
        # Create checkmark path (as percentage of checkbox size)
        start_x = center - size * 0.3
        start_y = center
        
        middle_x = center - size * 0.1
        middle_y = center + size * 0.2
        
        end_x = center + size * 0.3
        end_y = center - size * 0.2
        
        self._checkmark_points = [
            Point(start_x, start_y),
            Point(middle_x, middle_y),
            Point(end_x, end_y)
        ]
    
    def render(self, parent_widget, framework: str = "tkinter"):
        """
        Render the checkbox in the specified GUI framework
        """
        self._gui_framework = framework
        
        if framework == "tkinter":
            return self._render_tkinter(parent_widget)
        elif framework == "pyqt5":
            return self._render_pyqt5(parent_widget)
        else:
            raise ValueError(f"Framework non supporté: {framework}")
    
    def _render_tkinter(self, parent):
        """Render with Tkinter"""
        import tkinter as tk
        
        # Create container frame
        self._container_widget = tk.Frame(parent, bg=parent.cget('bg') if hasattr(parent, 'cget') else '#f0f0f0')
        
        # Create canvas for custom checkbox drawing
        canvas_size = self.style.size + 10  # Extra space for effects
        self._checkbox_canvas = tk.Canvas(
            self._container_widget,
            width=canvas_size,
            height=canvas_size,
            bg=self._container_widget.cget('bg'),
            highlightthickness=0,
            relief='flat'
        )
        
        # Position checkbox based on label position
        if self.style.label_position == "right":
            self._checkbox_canvas.pack(side="left", padx=(0, self.style.label_spacing))
        elif self.style.label_position == "left":
            self._checkbox_canvas.pack(side="right", padx=(self.style.label_spacing, 0))
        elif self.style.label_position == "top":
            self._checkbox_canvas.pack(side="bottom", pady=(self.style.label_spacing, 0))
        else:  # bottom
            self._checkbox_canvas.pack(side="top", pady=(0, self.style.label_spacing))
        
        # Create label if specified
        if self.style.label_text:
            self._label_widget = tk.Label(
                self._container_widget,
                text=self.style.label_text,
                font=(self.config.font_family, self.style.label_font_size),
                fg=self.style.label_color,
                bg=self._container_widget.cget('bg'),
                cursor="hand2"
            )
            
            if self.style.label_position == "right":
                self._label_widget.pack(side="left", fill="y")
            elif self.style.label_position == "left":
                self._label_widget.pack(side="right", fill="y")
            elif self.style.label_position == "top":
                self._label_widget.pack(side="bottom")
            else:  # bottom
                self._label_widget.pack(side="top")
            
            # Bind label events
            self._label_widget.bind("<Button-1>", self._on_click)
            self._label_widget.bind("<Enter>", self._on_hover_enter)
            self._label_widget.bind("<Leave>", self._on_hover_leave)
        
        # Bind canvas events
        self._checkbox_canvas.bind("<Button-1>", self._on_click)
        self._checkbox_canvas.bind("<Enter>", self._on_hover_enter)
        self._checkbox_canvas.bind("<Leave>", self._on_hover_leave)
        self._checkbox_canvas.bind("<ButtonPress-1>", self._on_press)
        self._checkbox_canvas.bind("<ButtonRelease-1>", self._on_release)
        
        # Initial drawing
        self._draw_checkbox_tkinter()
        
        return self._container_widget
    
    def _render_pyqt5(self, parent):
        """Render with PyQt5"""
        try:
            from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox
            from PyQt5.QtCore import Qt, pyqtSignal
            from PyQt5.QtGui import QFont, QPainter, QPen, QBrush, QColor
        except ImportError:
            raise ImportError("PyQt5 non installé. Installez avec: pip install PyQt5")
        
        # Create container widget
        self._container_widget = QWidget(parent)
        
        # Create layout based on label position
        if self.style.label_position in ["left", "right"]:
            layout = QHBoxLayout(self._container_widget)
        else:
            layout = QVBoxLayout(self._container_widget)
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.style.label_spacing)
        
        # Create custom checkbox widget
        self._gui_widget = CustomCheckboxWidget(self)
        self._gui_widget.setFixedSize(self.style.size + 10, self.style.size + 10)
        
        # Create label if specified
        if self.style.label_text:
            self._label_widget = QLabel(self.style.label_text)
            self._label_widget.setFont(QFont(self.config.font_family, self.style.label_font_size))
            
            # Add widgets to layout based on position
            if self.style.label_position == "left":
                layout.addWidget(self._label_widget)
                layout.addWidget(self._gui_widget)
            elif self.style.label_position == "right":
                layout.addWidget(self._gui_widget)
                layout.addWidget(self._label_widget)
            elif self.style.label_position == "top":
                layout.addWidget(self._label_widget)
                layout.addWidget(self._gui_widget)
            else:  # bottom
                layout.addWidget(self._gui_widget)
                layout.addWidget(self._label_widget)
        else:
            layout.addWidget(self._gui_widget)
        
        return self._container_widget
    
    def _draw_checkbox_tkinter(self):
        """Draw checkbox on Tkinter canvas"""
        if not self._checkbox_canvas:
            return
        
        # Clear canvas
        self._checkbox_canvas.delete("all")
        
        # Calculate position (centered in canvas)
        canvas_size = self.style.size + 10
        offset = 5
        x = offset
        y = offset
        size = self.style.size
        
        # Draw shadow if enabled
        if self.style.shadow_enabled:
            shadow_offset = 2
            self._checkbox_canvas.create_rectangle(
                x + shadow_offset, y + shadow_offset,
                x + size + shadow_offset, y + size + shadow_offset,
                fill=self.style.shadow_color,
                outline="",
                tags="shadow"
            )
        
        # Draw checkbox background
        current_size = size * self._current_scale
        size_offset = (size - current_size) / 2
        
        checkbox_x1 = x + size_offset
        checkbox_y1 = y + size_offset
        checkbox_x2 = x + size - size_offset
        checkbox_y2 = y + size - size_offset
        
        # Background color based on state and fill progress
        if self._current_state == CheckboxState.CHECKED:
            if self.style.animation_type == CheckboxAnimation.FILL:
                # Gradient fill effect
                fill_height = current_size * self._fill_progress
                
                # Unchecked background
                self._checkbox_canvas.create_rectangle(
                    checkbox_x1, checkbox_y1, checkbox_x2, checkbox_y2,
                    fill=self.style.unchecked_color,
                    outline=self._current_border_color.to_hex(),
                    width=self.style.border_width,
                    tags="checkbox_bg"
                )
                
                # Filled portion
                if fill_height > 0:
                    self._checkbox_canvas.create_rectangle(
                        checkbox_x1, checkbox_y2 - fill_height,
                        checkbox_x2, checkbox_y2,
                        fill=self._current_color.to_hex(),
                        outline="",
                        tags="checkbox_fill"
                    )
            else:
                # Standard fill
                self._checkbox_canvas.create_rectangle(
                    checkbox_x1, checkbox_y1, checkbox_x2, checkbox_y2,
                    fill=self._current_color.to_hex(),
                    outline=self._current_border_color.to_hex(),
                    width=self.style.border_width,
                    tags="checkbox_bg"
                )
        else:
            # Unchecked state
            self._checkbox_canvas.create_rectangle(
                checkbox_x1, checkbox_y1, checkbox_x2, checkbox_y2,
                fill=self.style.unchecked_color,
                outline=self._current_border_color.to_hex(),
                width=self.style.border_width,
                tags="checkbox_bg"
            )
        
        # Draw checkmark or indeterminate symbol
        if self._current_state == CheckboxState.CHECKED and self._checkmark_progress > 0:
            self._draw_checkmark_tkinter(checkbox_x1, checkbox_y1, current_size)
        elif self._current_state == CheckboxState.INDETERMINATE:
            self._draw_indeterminate_tkinter(checkbox_x1, checkbox_y1, current_size)
        
        # Draw ripple effects
        for ripple in self._ripple_effects:
            if ripple.active:
                self._draw_ripple_tkinter(ripple)
    
    def _draw_checkmark_tkinter(self, x: float, y: float, size: float):
        """Draw animated checkmark"""
        if self._checkmark_progress <= 0:
            return
        
        # Scale checkmark points to current size
        scale_factor = size / self.style.size
        scaled_points = [
            Point(p.x * scale_factor + x, p.y * scale_factor + y)
            for p in self._checkmark_points
        ]
        
        # Draw checkmark path based on progress
        if self._checkmark_progress >= 1.0:
            # Full checkmark
            self._checkbox_canvas.create_line(
                scaled_points[0].x, scaled_points[0].y,
                scaled_points[1].x, scaled_points[1].y,
                scaled_points[2].x, scaled_points[2].y,
                fill=self.style.checkmark_color,
                width=3,
                capstyle="round",
                joinstyle="round",
                tags="checkmark"
            )
        else:
            # Partial checkmark (animated drawing)
            total_length = (scaled_points[0].distance_to(scaled_points[1]) + 
                          scaled_points[1].distance_to(scaled_points[2]))
            current_length = total_length * self._checkmark_progress
            
            # First segment
            segment1_length = scaled_points[0].distance_to(scaled_points[1])
            
            if current_length <= segment1_length:
                # Drawing first segment
                progress = current_length / segment1_length
                end_x = scaled_points[0].x + (scaled_points[1].x - scaled_points[0].x) * progress
                end_y = scaled_points[0].y + (scaled_points[1].y - scaled_points[0].y) * progress
                
                self._checkbox_canvas.create_line(
                    scaled_points[0].x, scaled_points[0].y,
                    end_x, end_y,
                    fill=self.style.checkmark_color,
                    width=3,
                    capstyle="round",
                    tags="checkmark"
                )
            else:
                # First segment complete, drawing second segment
                remaining_length = current_length - segment1_length
                segment2_length = scaled_points[1].distance_to(scaled_points[2])
                progress = remaining_length / segment2_length
                
                end_x = scaled_points[1].x + (scaled_points[2].x - scaled_points[1].x) * progress
                end_y = scaled_points[1].y + (scaled_points[2].y - scaled_points[1].y) * progress
                
                # Draw both segments
                self._checkbox_canvas.create_line(
                    scaled_points[0].x, scaled_points[0].y,
                    scaled_points[1].x, scaled_points[1].y,
                    fill=self.style.checkmark_color,
                    width=3,
                    capstyle="round",
                    tags="checkmark"
                )
                
                self._checkbox_canvas.create_line(
                    scaled_points[1].x, scaled_points[1].y,
                    end_x, end_y,
                    fill=self.style.checkmark_color,
                    width=3,
                    capstyle="round",
                    tags="checkmark"
                )
    
    def _draw_indeterminate_tkinter(self, x: float, y: float, size: float):
        """Draw indeterminate symbol"""
        line_width = size * 0.6
        line_height = 3
        
        center_x = x + size / 2
        center_y = y + size / 2
        
        self._checkbox_canvas.create_rectangle(
            center_x - line_width / 2, center_y - line_height / 2,
            center_x + line_width / 2, center_y + line_height / 2,
            fill=self.style.checkmark_color,
            outline="",
            tags="indeterminate"
        )
    
    def _draw_ripple_tkinter(self, ripple: CheckboxRippleEffect):
        """Draw ripple effect"""
        if ripple.current_radius <= 0:
            return
        
        # Convert opacity to alpha (Tkinter limitation workaround)
        alpha = int(ripple.opacity * 50)  # Reduced intensity
        
        self._checkbox_canvas.create_oval(
            ripple.center.x - ripple.current_radius,
            ripple.center.y - ripple.current_radius,
            ripple.center.x + ripple.current_radius,
            ripple.center.y + ripple.current_radius,
            fill=self.style.hover_color,
            outline="",
            stipple="gray" + str(alpha) if alpha > 0 else "",
            tags="ripple"
        )
    
    def _on_hover_enter(self, event=None):
        """Handle mouse enter"""
        if self.get_state() == "disabled":
            return
        
        self._is_hovered = True
        self.set_state("hover")
        self.trigger_callback('hover_enter')
        
        # Hover animations
        self._animate_hover_enter()
    
    def _on_hover_leave(self, event=None):
        """Handle mouse leave"""
        if self.get_state() == "disabled":
            return
        
        self._is_hovered = False
        self.set_state("normal")
        self.trigger_callback('hover_leave')
        
        # Return to normal animations
        self._animate_hover_leave()
    
    def _on_press(self, event=None):
        """Handle mouse press"""
        if self.get_state() == "disabled":
            return
        
        self._is_pressed = True
        
        # Create ripple effect
        if hasattr(event, 'x') and hasattr(event, 'y'):
            ripple_center = Point(event.x, event.y)
        else:
            # Default to center of checkbox
            ripple_center = Point(self.style.size / 2 + 5, self.style.size / 2 + 5)
        
        ripple = CheckboxRippleEffect(ripple_center, self.style.size)
        self._ripple_effects.append(ripple)
        ripple.start(self._animation_manager)
        
        # Scale down animation
        self._animation_manager.animate(
            "press_scale",
            self._current_scale,
            self.style.check_scale,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=0.1, easing=EasingType.EASE_OUT_QUAD)
        )
    
    def _on_release(self, event=None):
        """Handle mouse release"""
        if self.get_state() == "disabled":
            return
        
        self._is_pressed = False
        
        # Scale back up animation
        target_scale = self.style.hover_scale if self._is_hovered else 1.0
        self._animation_manager.animate(
            "release_scale",
            self._current_scale,
            target_scale,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=0.15, easing=EasingType.BOUNCE_OUT)
        )
    
    def _on_click(self, event=None):
        """Handle click event"""
        if self.get_state() == "disabled":
            return
        
        # Toggle state
        if self.style.tri_state:
            self._toggle_tri_state()
        else:
            self._toggle_state()
        
        self.trigger_callback('click')
        self.trigger_callback('state_changed', self._current_state)
    
    def _toggle_state(self):
        """Toggle between checked and unchecked"""
        new_state = (CheckboxState.UNCHECKED if self._current_state == CheckboxState.CHECKED 
                    else CheckboxState.CHECKED)
        self._animate_to_state(new_state)
    
    def _toggle_tri_state(self):
        """Toggle through tri-state cycle"""
        if self._current_state == CheckboxState.UNCHECKED:
            new_state = CheckboxState.INDETERMINATE
        elif self._current_state == CheckboxState.INDETERMINATE:
            new_state = CheckboxState.CHECKED
        else:
            new_state = CheckboxState.UNCHECKED
        
        self._animate_to_state(new_state)
    
    def _animate_to_state(self, new_state: CheckboxState):
        """Animate transition to new state"""
        old_state = self._current_state
        self._current_state = new_state
        
        # Determine target colors
        if new_state == CheckboxState.CHECKED:
            target_color = self.style.checked_color
            target_border = self.style.checked_border_color
            target_checkmark = 1.0
            target_fill = 1.0
        elif new_state == CheckboxState.INDETERMINATE:
            target_color = self.style.indeterminate_color
            target_border = self.style.indeterminate_color
            target_checkmark = 0.0
            target_fill = 1.0
        else:  # UNCHECKED
            target_color = self.style.unchecked_color
            target_border = self.style.border_color
            target_checkmark = 0.0
            target_fill = 0.0
        
        # Color animations
        self._animate_color_transition(
            self._current_color,
            ColorUtils.parse_color(target_color),
            "background"
        )
        
        self._animate_color_transition(
            self._current_border_color,
            ColorUtils.parse_color(target_border),
            "border"
        )
        
        # Checkmark animation
        if self.style.animation_type == CheckboxAnimation.CHECKMARK_DRAW:
            duration = self.style.check_animation_duration
            if new_state == CheckboxState.CHECKED:
                # Animate checkmark drawing
                self._animation_manager.animate(
                    "checkmark_draw",
                    0.0,
                    1.0,
                    lambda progress: self._update_checkmark_progress(progress),
                    AnimationConfig(duration=duration, easing=EasingType.EASE_OUT_CUBIC)
                )
            else:
                # Instantly hide checkmark for unchecked state
                self._checkmark_progress = 0.0
        
        # Fill animation
        if self.style.animation_type == CheckboxAnimation.FILL:
            self._animation_manager.animate(
                "fill_progress",
                self._fill_progress,
                target_fill,
                lambda progress: self._update_fill_progress(progress),
                AnimationConfig(duration=self.style.check_animation_duration, 
                              easing=EasingType.EASE_OUT_CUBIC)
            )
        
        # Scale animation
        if self.style.animation_type == CheckboxAnimation.SCALE:
            # Bounce effect on state change
            self._animation_manager.animate(
                "state_scale",
                self._current_scale,
                1.2,
                lambda value: self._update_scale(value),
                AnimationConfig(duration=0.1, easing=EasingType.EASE_OUT_QUAD),
                completion_callback=lambda: self._animation_manager.animate(
                    "state_scale_return",
                    1.2,
                    1.0,
                    lambda value: self._update_scale(value),
                    AnimationConfig(duration=0.2, easing=EasingType.BOUNCE_OUT)
                )
            )
    
    def _animate_hover_enter(self):
        """Animate hover enter effects"""
        # Scale animation
        if self.style.hover_scale != 1.0:
            self._animation_manager.animate(
                "hover_scale",
                self._current_scale,
                self.style.hover_scale,
                lambda value: self._update_scale(value),
                AnimationConfig(duration=self.style.hover_animation_duration, 
                              easing=EasingType.EASE_OUT_QUAD)
            )
        
        # Color hover effect
        if self._current_state == CheckboxState.CHECKED:
            hover_color = ColorUtils.lighten_color(self._current_color, 0.1)
            self._animate_color_transition(self._current_color, hover_color, "background")
    
    def _animate_hover_leave(self):
        """Animate hover leave effects"""
        # Scale back to normal
        self._animation_manager.animate(
            "hover_leave_scale",
            self._current_scale,
            1.0,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=self.style.hover_animation_duration, 
                          easing=EasingType.EASE_OUT_QUAD)
        )
        
        # Return to original color
        if self._current_state == CheckboxState.CHECKED:
            original_color = ColorUtils.parse_color(self.style.checked_color)
            self._animate_color_transition(self._current_color, original_color, "background")
    
    def _animate_color_transition(self, start_color: Color, end_color: Color, property_type: str):
        """Animate color transition"""
        def update_color(progress: float):
            current_color = ColorUtils.interpolate_colors(start_color, end_color, progress)
            
            if property_type == "background":
                self._current_color = current_color
            elif property_type == "border":
                self._current_border_color = current_color
            
            self.update_appearance()
        
        self._animation_manager.animate(
            f"color_{property_type}",
            0.0,
            1.0,
            update_color,
            AnimationConfig(duration=0.25, easing=EasingType.EASE_OUT_CUBIC)
        )
    
    def _update_scale(self, scale_value: float):
        """Update checkbox scale"""
        self._current_scale = scale_value
        self.update_appearance()
    
    def _update_checkmark_progress(self, progress: float):
        """Update checkmark drawing progress"""
        self._checkmark_progress = progress
        self.update_appearance()
    
    def _update_fill_progress(self, progress: float):
        """Update fill animation progress"""
        self._fill_progress = progress
        self.update_appearance()
    
    def update_appearance(self):
        """Update checkbox appearance"""
        if self._gui_framework == "tkinter":
            self._draw_checkbox_tkinter()
        elif self._gui_framework == "pyqt5":
            if self._gui_widget:
                self._gui_widget.update()
    
    def is_checked(self) -> bool:
        """Check if checkbox is in checked state"""
        return self._current_state == CheckboxState.CHECKED
    
    def is_indeterminate(self) -> bool:
        """Check if checkbox is in indeterminate state"""
        return self._current_state == CheckboxState.INDETERMINATE
    
    def get_checkbox_state(self) -> CheckboxState:
        """Get current checkbox state"""
        return self._current_state
    
    def set_checked(self, checked: bool, animate: bool = True):
        """Set checkbox state programmatically"""
        new_state = CheckboxState.CHECKED if checked else CheckboxState.UNCHECKED
        
        if animate:
            self._animate_to_state(new_state)
        else:
            self._current_state = new_state
            if new_state == CheckboxState.CHECKED:
                self._checkmark_progress = 1.0
                self._fill_progress = 1.0
                self._current_color = ColorUtils.parse_color(self.style.checked_color)
            else:
                self._checkmark_progress = 0.0
                self._fill_progress = 0.0
                self._current_color = ColorUtils.parse_color(self.style.unchecked_color)
            
            self.update_appearance()
    
    def set_indeterminate(self, animate: bool = True):
        """Set checkbox to indeterminate state"""
        if not self.style.tri_state:
            raise ValueError("Indeterminate state only available in tri-state mode")
        
        if animate:
            self._animate_to_state(CheckboxState.INDETERMINATE)
        else:
            self._current_state = CheckboxState.INDETERMINATE
            self._checkmark_progress = 0.0
            self._fill_progress = 1.0
            self._current_color = ColorUtils.parse_color(self.style.indeterminate_color)
            self.update_appearance()
    
    def set_colors(self, checked: str = None, unchecked: str = None, 
                   indeterminate: str = None, hover: str = None):
        """Update checkbox colors"""
        if checked:
            self.style.checked_color = checked
        if unchecked:
            self.style.unchecked_color = unchecked
        if indeterminate:
            self.style.indeterminate_color = indeterminate
        if hover:
            self.style.hover_color = hover
        
        # Update current color if needed
        if self._current_state == CheckboxState.CHECKED and checked:
            self._current_color = ColorUtils.parse_color(checked)
        elif self._current_state == CheckboxState.UNCHECKED and unchecked:
            self._current_color = ColorUtils.parse_color(unchecked)
        elif self._current_state == CheckboxState.INDETERMINATE and indeterminate:
            self._current_color = ColorUtils.parse_color(indeterminate)
        
        self.update_appearance()
    
    def pulse_animation(self, duration: float = 1.0, intensity: float = 0.2):
        """Create pulsing animation"""
        def pulse_update(progress):
            pulse_value = 1.0 + intensity * math.sin(progress * math.pi * 4)
            self._update_scale(pulse_value)
        
        config = AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_IN_OUT_QUAD,
            repeat_count=2
        )
        self._animation_manager.animate("pulse", 0.0, 1.0, pulse_update, config)
    
    def shake_animation(self, duration: float = 0.5):
        """Create shake animation for invalid states"""
        def shake_update(progress):
            offset = math.sin(progress * math.pi * 8) * 5 * (1 - progress)
            # Apply offset to position (implementation depends on framework)
            self._apply_shake_offset(offset)
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_OUT_CUBIC)
        self._animation_manager.animate("shake", 0.0, 1.0, shake_update, config)
    
    def _apply_shake_offset(self, offset: float):
        """Apply shake offset (framework-specific)"""
        pass  # Implementation depends on GUI framework capabilities
    
    def glow_animation(self, color: str = "#3498db", duration: float = 1.0):
        """Create glowing animation"""
        glow_color = ColorUtils.parse_color(color)
        original_border = self._current_border_color
        
        def glow_update(progress):
            if progress <= 0.5:
                # Glow in
                current = ColorUtils.interpolate_colors(original_border, glow_color, progress * 2)
            else:
                # Glow out
                current = ColorUtils.interpolate_colors(glow_color, original_border, (progress - 0.5) * 2)
            
            self._current_border_color = current
            self.update_appearance()
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_IN_OUT_QUAD)
        self._animation_manager.animate("glow", 0.0, 1.0, glow_update, config)
    
    def on_state_changed(self, callback: Callable):
        """Set callback for state changes"""
        self.bind_callback('state_changed', callback)
        return self
    
    def on_checked(self, callback: Callable):
        """Set callback for when checkbox becomes checked"""
        def check_callback(state):
            if state == CheckboxState.CHECKED:
                callback()
        
        self.bind_callback('state_changed', check_callback)
        return self
    
    def on_unchecked(self, callback: Callable):
        """Set callback for when checkbox becomes unchecked"""
        def uncheck_callback(state):
            if state == CheckboxState.UNCHECKED:
                callback()
        
        self.bind_callback('state_changed', uncheck_callback)
        return self
    
    def stop_all_animations(self):
        """Stop all checkbox animations"""
        self._animation_manager.stop_all_animations()
        # Clear ripple effects
        self._ripple_effects.clear()
        super().stop_all_animations()
    
    def __del__(self):
        """Cleanup when checkbox is destroyed"""
        if hasattr(self, '_animation_manager'):
            self._animation_manager.stop_all_animations()

# PyQt5 Custom Widget Class (for PyQt5 rendering)
try:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent
    
    class CustomCheckboxWidget(QWidget):
        """Custom PyQt5 widget for advanced checkbox rendering"""
        
        clicked = pyqtSignal()
        
        def __init__(self, checkbox_instance):
            super().__init__()
            self.checkbox = checkbox_instance
            self.setMouseTracking(True)
        
        def paintEvent(self, event):
            """Custom paint event for checkbox"""
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Get current properties from checkbox instance
            size = self.checkbox.style.size
            scale = self.checkbox._current_scale
            current_size = size * scale
            
            # Calculate position
            x = (self.width() - current_size) / 2
            y = (self.height() - current_size) / 2
            
            # Draw checkbox background
            bg_color = QColor(self.checkbox._current_color.to_hex())
            border_color = QColor(self.checkbox._current_border_color.to_hex())
            
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, self.checkbox.style.border_width))
            painter.drawRoundedRect(
                x, y, current_size, current_size,
                self.checkbox.style.border_radius,
                self.checkbox.style.border_radius
            )
            
            # Draw checkmark or indeterminate symbol
            if (self.checkbox._current_state == CheckboxState.CHECKED and 
                self.checkbox._checkmark_progress > 0):
                self._draw_checkmark_pyqt5(painter, x, y, current_size)
            elif self.checkbox._current_state == CheckboxState.INDETERMINATE:
                self._draw_indeterminate_pyqt5(painter, x, y, current_size)
        
        def _draw_checkmark_pyqt5(self, painter, x, y, size):
            """Draw checkmark in PyQt5"""
            painter.setPen(QPen(QColor(self.checkbox.style.checkmark_color), 3, Qt.SolidLine, Qt.RoundCap))
            
            # Scale checkmark points
            scale_factor = size / self.checkbox.style.size
            points = [
                (p.x * scale_factor + x, p.y * scale_factor + y)
                for p in self.checkbox._checkmark_points
            ]
            
            # Draw checkmark based on progress
            if self.checkbox._checkmark_progress >= 1.0:
                # Full checkmark
                painter.drawLine(points[0][0], points[0][1], points[1][0], points[1][1])
                painter.drawLine(points[1][0], points[1][1], points[2][0], points[2][1])
            # Partial drawing implementation would go here
        
        def _draw_indeterminate_pyqt5(self, painter, x, y, size):
            """Draw indeterminate symbol in PyQt5"""
            line_width = size * 0.6
            line_height = 3
            
            center_x = x + size / 2
            center_y = y + size / 2
            
            painter.setBrush(QBrush(QColor(self.checkbox.style.checkmark_color)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(
                center_x - line_width / 2, center_y - line_height / 2,
                line_width, line_height
            )
        
        def mousePressEvent(self, event: QMouseEvent):
            """Handle mouse press"""
            self.checkbox._on_press(event)
        
        def mouseReleaseEvent(self, event: QMouseEvent):
            """Handle mouse release"""
            self.checkbox._on_release(event)
            if self.rect().contains(event.pos()):
                self.checkbox._on_click(event)
        
        def enterEvent(self, event):
            """Handle mouse enter"""
            self.checkbox._on_hover_enter(event)
        
        def leaveEvent(self, event):
            """Handle mouse leave"""
            self.checkbox._on_hover_leave(event)

except ImportError:
    # PyQt5 not available
    class CustomCheckboxWidget:
        def __init__(self, checkbox_instance):
            pass