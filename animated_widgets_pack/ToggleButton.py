"""
Module toggle_button - Interactive toggle switches with animations
"""

import math
import time
from dataclasses import dataclass
from typing import Optional, Callable, Any, Union
from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, AnimationConfig, EasingType
from .utils import ColorUtils, Color, Rectangle, Point, GeometryUtils

@dataclass
class ToggleStyle:
    """Toggle button specific styling"""
    # Track colors
    track_color_off: str = "#95a5a6"
    track_color_on: str = "#27ae60"
    track_color_disabled: str = "#bdc3c7"
    
    # Thumb colors
    thumb_color_off: str = "#ecf0f1"
    thumb_color_on: str = "#ffffff"
    thumb_color_disabled: str = "#95a5a6"
    
    # Track dimensions
    track_width: int = 60
    track_height: int = 30
    track_border_radius: int = 15
    
    # Thumb dimensions
    thumb_size: int = 26
    thumb_padding: int = 2
    
    # Animation settings
    transition_duration: float = 0.3
    bounce_effect: bool = True
    
    # Visual effects
    shadow_enabled: bool = True
    shadow_color: str = "#2c3e50"
    shadow_blur: int = 4
    shadow_offset: tuple = (0, 2)
    
    # Glow effect
    glow_enabled: bool = False
    glow_color: str = "#3498db"
    glow_size: int = 8
    
    # Labels
    label_on: str = ""
    label_off: str = ""
    show_labels: bool = False
    label_font_size: int = 10

class AnimatedToggle(AnimatedWidget):
    """
    Animated toggle switch with smooth state transitions
    Supports customizable colors, sizes, and animation effects
    """
    
    def __init__(self, initial_state: bool = False, 
                 config: Optional[WidgetConfig] = None,
                 style: Optional[ToggleStyle] = None):
        super().__init__(config)
        self.style = style or ToggleStyle()
        
        # Toggle state
        self._is_on = initial_state
        self._previous_state = initial_state
        
        # Visual state properties
        self._current_thumb_position = self._get_thumb_end_position() if initial_state else self._get_thumb_start_position()
        self._current_track_color = ColorUtils.parse_color(
            self.style.track_color_on if initial_state else self.style.track_color_off
        )
        self._current_thumb_color = ColorUtils.parse_color(
            self.style.thumb_color_on if initial_state else self.style.thumb_color_off
        )
        
        # Animation properties
        self._thumb_scale = 1.0
        self._track_glow_intensity = 0.0
        self._is_pressed = False
        self._is_dragging = False
        self._drag_start_position = None
        self._drag_offset = 0
        
        # Animation manager
        self._animation_manager = AnimationManager()
        
        # GUI components
        self._gui_widget = None
        self._gui_framework = None
        self._canvas = None
        
        # Interaction tracking
        self._click_start_time = 0
        self._click_threshold = 0.2  # Maximum time for click vs drag
        
        # Performance optimization
        self._last_render_state = None
        self._needs_full_redraw = True
    
    def render(self, parent_widget, framework: str = "tkinter"):
        """
        Render the toggle switch in the specified GUI framework
        """
        self._gui_framework = framework
        
        if framework == "tkinter":
            self._render_tkinter(parent_widget)
        elif framework == "pyqt5":
            self._render_pyqt5(parent_widget)
        elif framework == "canvas":
            self._render_canvas(parent_widget)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
        
        return self._gui_widget
    
    def _render_tkinter(self, parent):
        """Render with Tkinter using Canvas for custom drawing"""
        import tkinter as tk
        
        # Calculate total size
        total_width = self.style.track_width + (self.style.glow_size * 2 if self.style.glow_enabled else 0)
        total_height = self.style.track_height + (self.style.glow_size * 2 if self.style.glow_enabled else 0)
        
        # Create frame container
        self._gui_widget = tk.Frame(parent, bg=parent.cget('bg') if hasattr(parent, 'cget') else 'white')
        
        # Create canvas for drawing
        self._canvas = tk.Canvas(
            self._gui_widget,
            width=total_width,
            height=total_height,
            highlightthickness=0,
            bg=parent.cget('bg') if hasattr(parent, 'cget') else 'white'
        )
        self._canvas.pack()
        
        # Bind events
        self._canvas.bind("<Button-1>", self._on_mouse_down)
        self._canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self._canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self._canvas.bind("<Enter>", self._on_mouse_enter)
        self._canvas.bind("<Leave>", self._on_mouse_leave)
        
        # Initial draw
        self._draw_toggle()
    
    def _render_pyqt5(self, parent):
        """Render with PyQt5 using custom widget"""
        try:
            from PyQt5.QtWidgets import QWidget
            from PyQt5.QtCore import QTimer, pyqtSignal
            from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
            
            class ToggleWidget(QWidget):
                toggled = pyqtSignal(bool)
                
                def __init__(self, toggle_instance):
                    super().__init__()
                    self.toggle = toggle_instance
                    self.setFixedSize(
                        self.toggle.style.track_width + 20,
                        self.toggle.style.track_height + 20
                    )
                    self.setMouseTracking(True)
                
                def paintEvent(self, event):
                    painter = QPainter(self)
                    painter.setRenderHint(QPainter.Antialiasing)
                    self.toggle._draw_pyqt5(painter)
                
                def mousePressEvent(self, event):
                    self.toggle._on_mouse_down_pyqt5(event)
                
                def mouseReleaseEvent(self, event):
                    self.toggle._on_mouse_up_pyqt5(event)
                
                def mouseMoveEvent(self, event):
                    self.toggle._on_mouse_drag_pyqt5(event)
            
            self._gui_widget = ToggleWidget(self)
            
        except ImportError:
            raise ImportError("PyQt5 not installed. Install with: pip install PyQt5")
    
    def _render_canvas(self, canvas):
        """Render directly on a provided canvas object"""
        self._canvas = canvas
        self._gui_widget = canvas
        self._draw_toggle()
    
    def _draw_toggle(self):
        """Draw the toggle switch on canvas"""
        if not self._canvas:
            return
        
        # Clear canvas
        if hasattr(self._canvas, 'delete'):
            self._canvas.delete("all")
        
        # Calculate positions
        glow_offset = self.style.glow_size if self.style.glow_enabled else 0
        track_x = glow_offset
        track_y = glow_offset
        
        # Draw glow effect
        if self.style.glow_enabled and self._track_glow_intensity > 0:
            self._draw_glow_effect(track_x, track_y)
        
        # Draw track
        self._draw_track(track_x, track_y)
        
        # Draw thumb
        self._draw_thumb()
        
        # Draw labels
        if self.style.show_labels:
            self._draw_labels(track_x, track_y)
        
        # Mark as rendered
        self._needs_full_redraw = False
    
    def _draw_track(self, x: float, y: float):
        """Draw the toggle track"""
        if not self._canvas:
            return
        
        color = self._current_track_color.to_hex()
        
        if hasattr(self._canvas, 'create_oval'):  # Tkinter
            # Draw rounded rectangle as overlapping ovals and rectangle
            radius = self.style.track_border_radius
            
            # Main rectangle
            self._canvas.create_rectangle(
                x + radius, y,
                x + self.style.track_width - radius, y + self.style.track_height,
                fill=color, outline="", tags="track"
            )
            
            # Left rounded end
            self._canvas.create_oval(
                x, y,
                x + radius * 2, y + self.style.track_height,
                fill=color, outline="", tags="track"
            )
            
            # Right rounded end
            self._canvas.create_oval(
                x + self.style.track_width - radius * 2, y,
                x + self.style.track_width, y + self.style.track_height,
                fill=color, outline="", tags="track"
            )
    
    def _draw_thumb(self):
        """Draw the toggle thumb"""
        if not self._canvas:
            return
        
        # Calculate thumb position and size
        thumb_x = self._current_thumb_position
        thumb_y = (self.style.glow_size if self.style.glow_enabled else 0) + self.style.thumb_padding
        
        scaled_size = self.style.thumb_size * self._thumb_scale
        size_offset = (self.style.thumb_size - scaled_size) / 2
        
        actual_x = thumb_x + size_offset
        actual_y = thumb_y + size_offset
        
        color = self._current_thumb_color.to_hex()
        
        if hasattr(self._canvas, 'create_oval'):  # Tkinter
            # Draw shadow
            if self.style.shadow_enabled:
                shadow_color = ColorUtils.parse_color(self.style.shadow_color)
                shadow_alpha = Color(shadow_color.r, shadow_color.g, shadow_color.b, 0.3)
                
                self._canvas.create_oval(
                    actual_x + self.style.shadow_offset[0],
                    actual_y + self.style.shadow_offset[1],
                    actual_x + scaled_size + self.style.shadow_offset[0],
                    actual_y + scaled_size + self.style.shadow_offset[1],
                    fill=shadow_alpha.to_hex(), outline="", tags="thumb_shadow"
                )
            
            # Draw thumb
            self._canvas.create_oval(
                actual_x, actual_y,
                actual_x + scaled_size, actual_y + scaled_size,
                fill=color, outline="", tags="thumb"
            )
    
    def _draw_glow_effect(self, track_x: float, track_y: float):
        """Draw glow effect around track"""
        if not self._canvas or self._track_glow_intensity <= 0:
            return
        
        glow_color = ColorUtils.parse_color(self.style.glow_color)
        intensity = self._track_glow_intensity
        
        # Create multiple glow layers
        for i in range(3):
            alpha = intensity * (0.3 - i * 0.1)
            if alpha <= 0:
                continue
            
            glow_size = self.style.glow_size + i * 2
            glow_with_alpha = Color(glow_color.r, glow_color.g, glow_color.b, alpha)
            
            if hasattr(self._canvas, 'create_rectangle'):  # Tkinter approximation
                self._canvas.create_rectangle(
                    track_x - glow_size, track_y - glow_size,
                    track_x + self.style.track_width + glow_size,
                    track_y + self.style.track_height + glow_size,
                    fill="", outline=glow_with_alpha.to_hex(), width=2,
                    tags="glow"
                )
    
    def _draw_labels(self, track_x: float, track_y: float):
        """Draw on/off labels"""
        if not self._canvas:
            return
        
        font_size = self.style.label_font_size
        
        if self.style.label_off:
            self._canvas.create_text(
                track_x - 20, track_y + self.style.track_height / 2,
                text=self.style.label_off,
                font=("Arial", font_size),
                fill=self.config.text_color,
                anchor="e", tags="label"
            )
        
        if self.style.label_on:
            self._canvas.create_text(
                track_x + self.style.track_width + 20, track_y + self.style.track_height / 2,
                text=self.style.label_on,
                font=("Arial", font_size),
                fill=self.config.text_color,
                anchor="w", tags="label"
            )
    
    def _get_thumb_start_position(self) -> float:
        """Get thumb position when toggle is OFF"""
        glow_offset = self.style.glow_size if self.style.glow_enabled else 0
        return glow_offset + self.style.thumb_padding
    
    def _get_thumb_end_position(self) -> float:
        """Get thumb position when toggle is ON"""
        glow_offset = self.style.glow_size if self.style.glow_enabled else 0
        return glow_offset + self.style.track_width - self.style.thumb_size - self.style.thumb_padding
    
    def _on_mouse_down(self, event):
        """Handle mouse down event"""
        if self.get_state() == "disabled":
            return
        
        self._is_pressed = True
        self._click_start_time = time.time()
        self._drag_start_position = event.x
        
        # Visual feedback
        self._start_press_animation()
        
        self.set_state("pressed")
        self.trigger_callback('press')
    
    def _on_mouse_up(self, event):
        """Handle mouse up event"""
        if self.get_state() == "disabled":
            return
        
        click_duration = time.time() - self._click_start_time
        
        if not self._is_dragging and click_duration < self._click_threshold:
            # Quick click - toggle state
            self.toggle()
        elif self._is_dragging:
            # Drag release - determine final state based on position
            center_x = self._get_thumb_start_position() + (self._get_thumb_end_position() - self._get_thumb_start_position()) / 2
            should_be_on = self._current_thumb_position > center_x
            
            if should_be_on != self._is_on:
                self.toggle()
            else:
                # Snap back to current state
                self._animate_to_state(self._is_on)
        
        # Reset interaction state
        self._is_pressed = False
        self._is_dragging = False
        self._drag_start_position = None
        self._drag_offset = 0
        
        # Visual feedback
        self._start_release_animation()
        
        self.set_state("normal")
        self.trigger_callback('release')
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag event"""
        if self.get_state() == "disabled" or not self._is_pressed:
            return
        
        if not self._is_dragging:
            # Start dragging
            self._is_dragging = True
            self.trigger_callback('drag_start')
        
        # Calculate drag offset
        if self._drag_start_position is not None:
            self._drag_offset = event.x - self._drag_start_position
            
            # Update thumb position with constraints
            start_pos = self._get_thumb_start_position()
            end_pos = self._get_thumb_end_position()
            base_pos = start_pos if not self._is_on else end_pos
            
            new_position = base_pos + self._drag_offset
            self._current_thumb_position = GeometryUtils.clamp(new_position, start_pos, end_pos)
            
            # Update colors based on position
            progress = (self._current_thumb_position - start_pos) / (end_pos - start_pos)
            self._update_colors_for_progress(progress)
            
            # Redraw
            self._draw_toggle()
            
            self.trigger_callback('drag', progress)
    
    def _on_mouse_enter(self, event):
        """Handle mouse enter event"""
        if self.get_state() == "disabled":
            return
        
        self.set_state("hover")
        self._start_hover_animation()
        self.trigger_callback('hover_enter')
    
    def _on_mouse_leave(self, event):
        """Handle mouse leave event"""
        if self.get_state() == "disabled":
            return
        
        self.set_state("normal")
        self._start_leave_animation()
        self.trigger_callback('hover_leave')
    
    def _start_press_animation(self):
        """Start press animation effects"""
        # Thumb scale animation
        config = AnimationConfig(
            duration=0.1,
            easing=EasingType.EASE_OUT_QUAD
        )
        
        self._animation_manager.animate(
            "thumb_scale_press",
            self._thumb_scale,
            0.9,
            lambda value: self._update_thumb_scale(value),
            config
        )
        
        # Glow intensity animation
        if self.style.glow_enabled:
            self._animation_manager.animate(
                "glow_press",
                self._track_glow_intensity,
                0.8,
                lambda value: self._update_glow_intensity(value),
                config
            )
    
    def _start_release_animation(self):
        """Start release animation effects"""
        config = AnimationConfig(
            duration=0.2,
            easing=EasingType.ELASTIC_OUT if self.style.bounce_effect else EasingType.EASE_OUT_CUBIC
        )
        
        # Return thumb to normal scale
        self._animation_manager.animate(
            "thumb_scale_release",
            self._thumb_scale,
            1.0,
            lambda value: self._update_thumb_scale(value),
            config
        )
        
        # Return glow to normal
        if self.style.glow_enabled:
            self._animation_manager.animate(
                "glow_release",
                self._track_glow_intensity,
                0.0,
                lambda value: self._update_glow_intensity(value),
                config
            )
    
    def _start_hover_animation(self):
        """Start hover animation effects"""
        if self.style.glow_enabled:
            config = AnimationConfig(
                duration=0.2,
                easing=EasingType.EASE_OUT_QUAD
            )
            
            self._animation_manager.animate(
                "glow_hover",
                self._track_glow_intensity,
                0.3,
                lambda value: self._update_glow_intensity(value),
                config
            )
    
    def _start_leave_animation(self):
        """Start mouse leave animation effects"""
        if self.style.glow_enabled:
            config = AnimationConfig(
                duration=0.3,
                easing=EasingType.EASE_OUT_QUAD
            )
            
            self._animation_manager.animate(
                "glow_leave",
                self._track_glow_intensity,
                0.0,
                lambda value: self._update_glow_intensity(value),
                config
            )
    
    def _update_thumb_scale(self, scale: float):
        """Update thumb scale and redraw"""
        self._thumb_scale = scale
        self._draw_toggle()
    
    def _update_glow_intensity(self, intensity: float):
        """Update glow intensity and redraw"""
        self._track_glow_intensity = intensity
        self._draw_toggle()
    
    def _update_colors_for_progress(self, progress: float):
        """Update colors based on animation progress"""
        # Interpolate track color
        off_color = ColorUtils.parse_color(self.style.track_color_off)
        on_color = ColorUtils.parse_color(self.style.track_color_on)
        self._current_track_color = ColorUtils.interpolate_colors(off_color, on_color, progress)
        
        # Interpolate thumb color
        thumb_off = ColorUtils.parse_color(self.style.thumb_color_off)
        thumb_on = ColorUtils.parse_color(self.style.thumb_color_on)
        self._current_thumb_color = ColorUtils.interpolate_colors(thumb_off, thumb_on, progress)
    
    def _animate_to_state(self, target_state: bool):
        """Animate toggle to target state"""
        if target_state == self._is_on:
            return
        
        # Calculate animation parameters
        start_pos = self._current_thumb_position
        end_pos = self._get_thumb_end_position() if target_state else self._get_thumb_start_position()
        
        # Create animation config
        config = AnimationConfig(
            duration=self.style.transition_duration,
            easing=EasingType.BOUNCE_OUT if self.style.bounce_effect else EasingType.EASE_OUT_CUBIC
        )
        
        # Animate thumb position
        def update_position(position):
            self._current_thumb_position = position
            # Calculate progress for color interpolation
            total_distance = self._get_thumb_end_position() - self._get_thumb_start_position()
            progress = (position - self._get_thumb_start_position()) / total_distance
            self._update_colors_for_progress(progress)
            self._draw_toggle()
        
        self._animation_manager.animate(
            "toggle_transition",
            start_pos,
            end_pos,
            update_position,
            config,
            completion_callback=lambda: self._on_animation_complete(target_state)
        )
    
    def _on_animation_complete(self, new_state: bool):
        """Handle animation completion"""
        self._is_on = new_state
        self.trigger_callback('value_changed', new_state)
        
        # Update final colors to exact values (avoid floating point errors)
        if new_state:
            self._current_track_color = ColorUtils.parse_color(self.style.track_color_on)
            self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_on)
        else:
            self._current_track_color = ColorUtils.parse_color(self.style.track_color_off)
            self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_off)
        
        self._draw_toggle()
    
    def toggle(self):
        """Toggle the switch state"""
        if self.get_state() == "disabled":
            return False
        
        new_state = not self._is_on
        self._animate_to_state(new_state)
        self.trigger_callback('toggle', new_state)
        return True
    
    def set_value(self, value: bool, animate: bool = True):
        """Set toggle value programmatically"""
        if self.get_state() == "disabled":
            return False
        
        if value == self._is_on:
            return True
        
        if animate:
            self._animate_to_state(value)
        else:
            self._is_on = value
            self._current_thumb_position = self._get_thumb_end_position() if value else self._get_thumb_start_position()
            
            # Update colors immediately
            if value:
                self._current_track_color = ColorUtils.parse_color(self.style.track_color_on)
                self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_on)
            else:
                self._current_track_color = ColorUtils.parse_color(self.style.track_color_off)
                self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_off)
            
            self._draw_toggle()
            self.trigger_callback('value_changed', value)
        
        return True
    
    def get_value(self) -> bool:
        """Get current toggle value"""
        return self._is_on
    
    def set_colors(self, track_off: str = None, track_on: str = None,
                   thumb_off: str = None, thumb_on: str = None):
        """Update toggle colors"""
        if track_off:
            self.style.track_color_off = track_off
        if track_on:
            self.style.track_color_on = track_on
        if thumb_off:
            self.style.thumb_color_off = thumb_off
        if thumb_on:
            self.style.thumb_color_on = thumb_on
        
        # Update current colors if not animating
        if not self._animation_manager.is_animating("toggle_transition"):
            if self._is_on:
                self._current_track_color = ColorUtils.parse_color(self.style.track_color_on)
                self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_on)
            else:
                self._current_track_color = ColorUtils.parse_color(self.style.track_color_off)
                self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_off)
            
            self._draw_toggle()
    
    def set_labels(self, label_on: str = None, label_off: str = None, show: bool = None):
        """Update toggle labels"""
        if label_on is not None:
            self.style.label_on = label_on
        if label_off is not None:
            self.style.label_off = label_off
        if show is not None:
            self.style.show_labels = show
        
        self._draw_toggle()
    
    def enable_glow(self, enabled: bool = True, color: str = None, size: int = None):
        """Enable or disable glow effect"""
        self.style.glow_enabled = enabled
        if color:
            self.style.glow_color = color
        if size:
            self.style.glow_size = size
        
        self._needs_full_redraw = True
        self._draw_toggle()
    
    def pulse_animation(self, duration: float = 2.0, intensity: float = 1.0):
        """Create a pulsing glow effect"""
        if not self.style.glow_enabled:
            return
        
        config = AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_IN_OUT_QUAD,
            auto_reverse=True,
            repeat_count=1
        )
        
        self._animation_manager.animate(
            "pulse",
            0.0,
            intensity,
            lambda value: self._update_glow_intensity(value),
            config
        )
    
    def flash_animation(self, color: str = "#ffffff", duration: float = 0.4):
        """Create a flash animation effect"""
        original_track_color = self._current_track_color
        flash_color = ColorUtils.parse_color(color)
        
        def flash_update(progress):
            if progress <= 0.5:
                # Flash to white
                current = ColorUtils.interpolate_colors(original_track_color, flash_color, progress * 2)
            else:
                # Flash back to original
                current = ColorUtils.interpolate_colors(flash_color, original_track_color, (progress - 0.5) * 2)
            
            self._current_track_color = current
            self._draw_toggle()
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_IN_OUT_QUAD)
        self._animation_manager.animate("flash", 0.0, 1.0, flash_update, config)
    
    def shake_animation(self, duration: float = 0.5, intensity: float = 5.0):
        """Create a shake animation effect"""
        original_position = self._current_thumb_position
        
        def shake_update(progress):
            # Sine wave for shake effect
            shake_offset = math.sin(progress * math.pi * 8) * intensity * (1 - progress)
            self._current_thumb_position = original_position + shake_offset
            self._draw_toggle()
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_OUT_CUBIC)
        self._animation_manager.animate(
            "shake", 
            0.0, 
            1.0, 
            shake_update, 
            config,
            completion_callback=lambda: setattr(self, '_current_thumb_position', original_position)
        )
    
    def update_appearance(self):
        """Update widget appearance"""
        self._draw_toggle()
    
    def disable(self):
        """Disable the toggle"""
        super().disable()
        
        # Update to disabled colors
        self._current_track_color = ColorUtils.parse_color(self.style.track_color_disabled)
        self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_disabled)
        
        self._draw_toggle()
    
    def enable(self):
        """Enable the toggle"""
        super().enable()
        
        # Restore normal colors
        if self._is_on:
            self._current_track_color = ColorUtils.parse_color(self.style.track_color_on)
            self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_on)
        else:
            self._current_track_color = ColorUtils.parse_color(self.style.track_color_off)
            self._current_thumb_color = ColorUtils.parse_color(self.style.thumb_color_off)
        
        self._draw_toggle()
    
    def on_toggle(self, callback: Callable[[bool], None]):
        """Set callback for toggle events"""
        self.bind_callback('toggle', callback)
        return self
    
    def on_value_changed(self, callback: Callable[[bool], None]):
        """Set callback for value change events"""
        self.bind_callback('value_changed', callback)
        return self
    
    def on_drag(self, callback: Callable[[float], None]):
        """Set callback for drag events (progress 0.0-1.0)"""
        self.bind_callback('drag', callback)
        return self
    
    def stop_all_animations(self):
        """Stop all toggle animations"""
        self._animation_manager.stop_all_animations()
        super().stop_all_animations()
    
    def __del__(self):
        """Cleanup when toggle is destroyed"""
        if hasattr(self, '_animation_manager'):
            self._animation_manager.stop_all_animations()