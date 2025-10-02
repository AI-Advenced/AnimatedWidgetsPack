"""
Module buttons - Interactive buttons with animations
"""

from dataclasses import dataclass
from typing import Optional, Callable, Any
from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, AnimationConfig, EasingType
from .utils import ColorUtils, Color, Rectangle, Point

@dataclass
class ButtonStyle:
    """Button-specific styling"""
    normal_color: str = "#3498db"
    hover_color: str = "#2980b9"  
    pressed_color: str = "#21618c"
    disabled_color: str = "#95a5a6"
    text: str = "Button"
    icon: Optional[str] = None
    shadow_enabled: bool = True
    shadow_color: str = "#2c3e50"
    shadow_offset: tuple = (0, 2)
    hover_lift: float = 2.0  # Pixels of "lift" on hover
    click_scale: float = 0.95  # Scale factor when clicked

class AnimatedButton(AnimatedWidget):
    """
    Animated button with hover, click and focus effects
    Supports color, size and position animations
    """
    
    def __init__(self, text: str = "Button", config: Optional[WidgetConfig] = None,
                 style: Optional[ButtonStyle] = None):
        super().__init__(config)
        self.style = style or ButtonStyle()
        self.style.text = text
        
        # Internal state
        self._current_color = ColorUtils.parse_color(self.style.normal_color)
        self._current_scale = 1.0
        self._current_lift = 0.0
        self._is_pressed = False
        
        # Animation manager
        self._animation_manager = AnimationManager()
        
        # GUI widget (will be set during rendering)
        self._gui_widget = None
        self._gui_framework = None
    
    def render(self, parent_widget, framework: str = "tkinter"):
        """
        Render the button in the specified GUI framework
        Supported frameworks: 'tkinter', 'pyqt5'
        """
        self._gui_framework = framework
        
        if framework == "tkinter":
            self._render_tkinter(parent_widget)
        elif framework == "pyqt5":
            self._render_pyqt5(parent_widget)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
        
        return self._gui_widget
    
    def _render_tkinter(self, parent):
        """Render with Tkinter"""
        import tkinter as tk
        
        self._gui_widget = tk.Button(
            parent,
            text=self.style.text,
            width=self.config.width // 8,  # Approximate width in characters
            height=self.config.height // 20,  # Approximate height
            bg=self.style.normal_color,
            fg=self.config.text_color,
            font=(self.config.font_family, self.config.font_size),
            relief="flat",
            bd=self.config.border_width,
            cursor="hand2",
            activebackground=self.style.hover_color,
            activeforeground=self.config.text_color
        )
        
        # Bind events
        self._gui_widget.bind("<Button-1>", self._on_click)
        self._gui_widget.bind("<Enter>", self._on_hover_enter)
        self._gui_widget.bind("<Leave>", self._on_hover_leave)
        self._gui_widget.bind("<ButtonPress-1>", self._on_press)
        self._gui_widget.bind("<ButtonRelease-1>", self._on_release)
    
    def _render_pyqt5(self, parent):
        """Render with PyQt5"""
        try:
            from PyQt5.QtWidgets import QPushButton
            from PyQt5.QtCore import QTimer
            from PyQt5.QtGui import QFont
        except ImportError:
            raise ImportError("PyQt5 not installed. Install with: pip install PyQt5")
        
        self._gui_widget = QPushButton(self.style.text, parent)
        self._gui_widget.setFixedSize(self.config.width, self.config.height)
        
        # CSS styling
        self._update_pyqt5_style()
        
        # Bind events
        self._gui_widget.clicked.connect(self._on_click)
        self._gui_widget.enterEvent = self._on_hover_enter
        self._gui_widget.leaveEvent = self._on_hover_leave
        self._gui_widget.mousePressEvent = self._on_press
        self._gui_widget.mouseReleaseEvent = self._on_release
    
    def _update_pyqt5_style(self):
        """Update CSS style for PyQt5"""
        if self._gui_framework != "pyqt5" or not self._gui_widget:
            return
        
        color = self._current_color.to_hex()
        
        style = f"""
        QPushButton {{
            background-color: {color};
            color: {self.config.text_color};
            border: {self.config.border_width}px solid {self.config.border_color};
            border-radius: {self.config.border_radius}px;
            font-family: {self.config.font_family};
            font-size: {self.config.font_size}px;
            padding: 8px 16px;
        }}
        QPushButton:hover {{
            background-color: {self.style.hover_color};
        }}
        QPushButton:pressed {{
            background-color: {self.style.pressed_color};
        }}
        QPushButton:disabled {{
            background-color: {self.style.disabled_color};
        }}
        """
        
        self._gui_widget.setStyleSheet(style)
    
    def update_appearance(self):
        """Update button appearance"""
        if not self._gui_widget:
            return
        
        if self._gui_framework == "tkinter":
            self._gui_widget.configure(bg=self._current_color.to_hex())
        elif self._gui_framework == "pyqt5":
            self._update_pyqt5_style()
    
    def _on_hover_enter(self, event=None):
        """Handle mouse enter"""
        if self.get_state() == "disabled":
            return
        
        self.set_state("hover")
        self.trigger_callback('hover_enter')
        
        # Color animation
        start_color = self._current_color
        end_color = ColorUtils.parse_color(self.style.hover_color)
        
        self._animate_color_transition(start_color, end_color)
        
        # Lift animation
        if self.style.hover_lift > 0:
            self._animation_manager.animate(
                "lift",
                self._current_lift,
                self.style.hover_lift,
                lambda value: self._update_lift(value),
                AnimationConfig(duration=0.2, easing=EasingType.EASE_OUT_QUAD)
            )
    
    def _on_hover_leave(self, event=None):
        """Handle mouse leave"""
        if self.get_state() == "disabled":
            return
        
        self.set_state("normal")
        self.trigger_callback('hover_leave')
        
        # Return to normal color animation
        start_color = self._current_color
        end_color = ColorUtils.parse_color(self.style.normal_color)
        
        self._animate_color_transition(start_color, end_color)
        
        # Return lift animation
        self._animation_manager.animate(
            "lift",
            self._current_lift,
            0.0,
            lambda value: self._update_lift(value),
            AnimationConfig(duration=0.2, easing=EasingType.EASE_OUT_QUAD)
        )
    
    def _on_press(self, event=None):
        """Handle button press"""
        if self.get_state() == "disabled":
            return
        
        self._is_pressed = True
        self.set_state("pressed")
        
        # Pressed color animation
        start_color = self._current_color
        end_color = ColorUtils.parse_color(self.style.pressed_color)
        self._animate_color_transition(start_color, end_color, duration=0.1)
        
        # Scale animation (shrink)
        self._animation_manager.animate(
            "scale",
            self._current_scale,
            self.style.click_scale,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=0.1, easing=EasingType.EASE_OUT_QUAD)
        )
    
    def _on_release(self, event=None):
        """Handle button release"""
        if self.get_state() == "disabled":
            return
        
        self._is_pressed = False
        
        # Return to hover state if mouse is still over button
        if self._gui_framework == "tkinter":
            # For Tkinter, check mouse position
            try:
                x, y = self._gui_widget.winfo_pointerxy()
                widget_x = self._gui_widget.winfo_rootx()
                widget_y = self._gui_widget.winfo_rooty()
                widget_width = self._gui_widget.winfo_width()
                widget_height = self._gui_widget.winfo_height()
                
                if (widget_x <= x <= widget_x + widget_width and 
                    widget_y <= y <= widget_y + widget_height):
                    self.set_state("hover")
                    end_color = ColorUtils.parse_color(self.style.hover_color)
                else:
                    self.set_state("normal")
                    end_color = ColorUtils.parse_color(self.style.normal_color)
            except:
                self.set_state("normal")
                end_color = ColorUtils.parse_color(self.style.normal_color)
        else:
            self.set_state("hover")
            end_color = ColorUtils.parse_color(self.style.hover_color)
        
        # Return color animation
        start_color = self._current_color
        self._animate_color_transition(start_color, end_color, duration=0.15)
        
        # Return to normal scale animation
        self._animation_manager.animate(
            "scale",
            self._current_scale,
            1.0,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=0.15, easing=EasingType.ELASTIC_OUT)
        )
    
    def _on_click(self, event=None):
        """Handle button click"""
        if self.get_state() == "disabled":
            return
        
        self.trigger_callback('click')
    
    def _animate_color_transition(self, start_color: Color, end_color: Color, 
                                 duration: float = None):
        """Animate transition between two colors"""
        duration = duration or self.config.animation_duration
        
        def update_color(progress: float):
            self._current_color = ColorUtils.interpolate_colors(
                start_color, end_color, progress
            )
            self.update_appearance()
        
        self._animation_manager.animate(
            "color",
            0.0,
            1.0,
            update_color,
            AnimationConfig(duration=duration, easing=EasingType.EASE_OUT_CUBIC)
        )
    
    def _update_lift(self, lift_value: float):
        """Update lift effect (elevation)"""
        self._current_lift = lift_value
        # Here we could implement shadow or translation effects
        # depending on the GUI framework used
    
    def _update_scale(self, scale_value: float):
        """Update button scale"""
        self._current_scale = scale_value
        # Implementation depends on GUI framework
        # For PyQt5, we could use QGraphicsEffect
        # For Tkinter, we can adjust size
    
    def on_click(self, callback: Callable):
        """Set callback function for click"""
        self.bind_callback('click', callback)
        return self
    
    def set_text(self, text: str):
        """Change button text"""
        self.style.text = text
        if self._gui_widget:
            if self._gui_framework == "tkinter":
                self._gui_widget.configure(text=text)
            elif self._gui_framework == "pyqt5":
                self._gui_widget.setText(text)
    
    def set_colors(self, normal: str = None, hover: str = None, pressed: str = None):
        """Set button colors"""
        if normal:
            self.style.normal_color = normal
        if hover:
            self.style.hover_color = hover
        if pressed:
            self.style.pressed_color = pressed
        
        # Update current color if in normal state
        if self.get_state() == "normal" and normal:
            self._current_color = ColorUtils.parse_color(normal)
            self.update_appearance()
    
    def pulse_animation(self, duration: float = 1.0, scale_factor: float = 1.1):
        """Create a pulsing animation effect"""
        def pulse_update(value):
            scale = 1.0 + (scale_factor - 1.0) * value
            self._update_scale(scale)
        
        config = AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_IN_OUT_QUAD,
            auto_reverse=True,
            repeat_count=1
        )
        
        self._animation_manager.animate("pulse", 0.0, 1.0, pulse_update, config)
    
    def flash_animation(self, flash_color: str = "#ffffff", duration: float = 0.3):
        """Create a flash animation effect"""
        original_color = self._current_color
        flash_col = ColorUtils.parse_color(flash_color)
        
        def flash_update(progress):
            if progress <= 0.5:
                # Flash to white
                current = ColorUtils.interpolate_colors(original_color, flash_col, progress * 2)
            else:
                # Flash back to original
                current = ColorUtils.interpolate_colors(flash_col, original_color, (progress - 0.5) * 2)
            
            self._current_color = current
            self.update_appearance()
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_IN_OUT_QUAD)
        self._animation_manager.animate("flash", 0.0, 1.0, flash_update, config)
    
    def bounce_animation(self, duration: float = 0.6):
        """Create a bounce animation effect"""
        def bounce_update(value):
            self._update_scale(1.0 + value * 0.3)
        
        config = AnimationConfig(duration=duration, easing=EasingType.BOUNCE_OUT)
        self._animation_manager.animate("bounce", 1.0, 0.0, bounce_update, config)
    
    def stop_all_animations(self):
        """Stop all button animations"""
        self._animation_manager.stop_all_animations()
        super().stop_all_animations()
    
    def __del__(self):
        """Cleanup when button is destroyed"""
        if hasattr(self, '_animation_manager'):
            self._animation_manager.stop_all_animations()