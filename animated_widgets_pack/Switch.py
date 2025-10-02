"""
Module switch - Animated toggle switch with smooth transitions
"""

import math
import time
import threading
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional, Tuple
from enum import Enum
from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, AnimationConfig, EasingType
from .utils import ColorUtils, Color, Rectangle, Point, GeometryUtils

class SwitchState(Enum):
    """Switch states"""
    OFF = "off"
    ON = "on"

class SwitchStyle(Enum):
    """Switch visual styles"""
    MODERN = "modern"          # iOS-style switch
    CLASSIC = "classic"        # Traditional toggle
    MATERIAL = "material"      # Material Design switch
    CUSTOM = "custom"          # Custom styling

class SwitchAnimation(Enum):
    """Switch animation types"""
    SLIDE = "slide"            # Smooth sliding
    BOUNCE = "bounce"          # Bouncy slide
    ELASTIC = "elastic"        # Elastic snap
    FADE = "fade"             # Fade transition
    MORPH = "morph"           # Morphing transition

@dataclass
class SwitchAppearance:
    """Switch visual appearance configuration"""
    # Dimensions
    width: int = 60
    height: int = 30
    thumb_size: int = 26
    track_padding: int = 2
    
    # Colors - Track (background)
    track_off_color: str = "#cbd5e0"
    track_on_color: str = "#4299e1"
    track_disabled_color: str = "#e2e8f0"
    
    # Colors - Thumb (slider)
    thumb_off_color: str = "#ffffff"
    thumb_on_color: str = "#ffffff"
    thumb_disabled_color: str = "#f7fafc"
    thumb_hover_color: str = "#f7fafc"
    
    # Colors - Border
    border_color: str = "#e2e8f0"
    border_width: int = 1
    
    # Effects
    shadow_enabled: bool = True
    shadow_color: str = "#000000"
    shadow_opacity: float = 0.2
    shadow_blur: int = 4
    shadow_offset: Tuple[int, int] = (0, 2)
    
    # Animation properties
    animation_type: SwitchAnimation = SwitchAnimation.SLIDE
    animation_duration: float = 0.3
    hover_scale: float = 1.05
    active_scale: float = 0.95
    
    # Style-specific properties
    style: SwitchStyle = SwitchStyle.MODERN
    corner_radius_track: int = 15
    corner_radius_thumb: int = 13
    
    # Labels
    on_label: str = ""
    off_label: str = ""
    label_color: str = "#2d3748"
    label_font_size: int = 12
    
    # Icons (for future implementation)
    on_icon: Optional[str] = None
    off_icon: Optional[str] = None

class ThumbShadow:
    """Thumb shadow effect management"""
    
    def __init__(self, appearance: SwitchAppearance):
        self.appearance = appearance
        self.current_opacity = appearance.shadow_opacity
        self.current_blur = appearance.shadow_blur
        self.current_offset = Point(appearance.shadow_offset[0], appearance.shadow_offset[1])
        
    def animate_shadow(self, animation_manager: AnimationManager, 
                      target_opacity: float, duration: float = 0.2):
        """Animate shadow opacity"""
        animation_manager.animate(
            "shadow_opacity",
            self.current_opacity,
            target_opacity,
            lambda opacity: setattr(self, 'current_opacity', opacity),
            AnimationConfig(duration=duration, easing=EasingType.EASE_OUT_QUAD)
        )

class AnimatedSwitch(AnimatedWidget):
    """
    Animated toggle switch with customizable appearance and smooth transitions
    Supports multiple visual styles and animation types
    """
    
    def __init__(self, initial_state: bool = False, label: str = "",
                 config: Optional[WidgetConfig] = None, 
                 appearance: Optional[SwitchAppearance] = None):
        super().__init__(config)
        
        self.appearance = appearance or SwitchAppearance()
        self.label = label
        
        # Internal state
        self._current_state = SwitchState.ON if initial_state else SwitchState.OFF
        self._is_hovered = False
        self._is_pressed = False
        self._is_dragging = False
        
        # Animation properties
        self._thumb_position = 1.0 if initial_state else 0.0  # 0.0 = left, 1.0 = right
        self._current_scale = 1.0
        self._track_color_progress = 1.0 if initial_state else 0.0
        self._thumb_color_progress = 1.0 if initial_state else 0.0
        
        # Drag state
        self._drag_start_x = 0
        self._drag_start_position = 0.0
        self._drag_threshold = 10  # Pixels to start drag
        self._drag_velocity = 0.0
        self._last_drag_time = 0
        self._last_drag_position = 0.0
        
        # Color interpolation
        self._current_track_color = ColorUtils.parse_color(
            self.appearance.track_on_color if initial_state else self.appearance.track_off_color
        )
        self._current_thumb_color = ColorUtils.parse_color(
            self.appearance.thumb_on_color if initial_state else self.appearance.thumb_off_color
        )
        
        # Shadow effect
        self._thumb_shadow = ThumbShadow(self.appearance)
        
        # Animation manager
        self._animation_manager = AnimationManager()
        
        # GUI widget references
        self._gui_widget = None
        self._gui_framework = None
        self._switch_canvas = None
        self._label_widget = None
        self._container_widget = None
        
        # Geometry calculations
        self._track_rect = Rectangle(0, 0, self.appearance.width, self.appearance.height)
        self._calculate_thumb_bounds()
    
    def _calculate_thumb_bounds(self):
        """Calculate thumb movement bounds"""
        padding = self.appearance.track_padding
        thumb_size = self.appearance.thumb_size
        
        self._thumb_min_x = padding
        self._thumb_max_x = self.appearance.width - thumb_size - padding
        self._thumb_travel_distance = self._thumb_max_x - self._thumb_min_x
        
        self._thumb_y = (self.appearance.height - thumb_size) / 2
    
    def render(self, parent_widget, framework: str = "tkinter"):
        """
        Render the switch in the specified GUI framework
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
        self._container_widget = tk.Frame(
            parent, 
            bg=parent.cget('bg') if hasattr(parent, 'cget') else '#f0f0f0'
        )
        
        # Create label if specified
        if self.label:
            self._label_widget = tk.Label(
                self._container_widget,
                text=self.label,
                font=(self.config.font_family, self.appearance.label_font_size),
                fg=self.appearance.label_color,
                bg=self._container_widget.cget('bg'),
                cursor="hand2"
            )
            self._label_widget.pack(side="left", padx=(0, 10))
            
            # Bind label events
            self._label_widget.bind("<Button-1>", self._on_click)
            self._label_widget.bind("<Enter>", self._on_hover_enter)
            self._label_widget.bind("<Leave>", self._on_hover_leave)
        
        # Create canvas for switch drawing
        canvas_width = self.appearance.width + 20  # Extra space for effects
        canvas_height = self.appearance.height + 20
        
        self._switch_canvas = tk.Canvas(
            self._container_widget,
            width=canvas_width,
            height=canvas_height,
            bg=self._container_widget.cget('bg'),
            highlightthickness=0,
            relief='flat',
            cursor="hand2"
        )
        self._switch_canvas.pack(side="left")
        
        # Bind canvas events
        self._switch_canvas.bind("<Button-1>", self._on_press)
        self._switch_canvas.bind("<ButtonRelease-1>", self._on_release)
        self._switch_canvas.bind("<B1-Motion>", self._on_drag)
        self._switch_canvas.bind("<Enter>", self._on_hover_enter)
        self._switch_canvas.bind("<Leave>", self._on_hover_leave)
        
        # Initial drawing
        self._draw_switch_tkinter()
        
        return self._container_widget
    
    def _render_pyqt5(self, parent):
        """Render with PyQt5"""
        try:
            from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QFont
        except ImportError:
            raise ImportError("PyQt5 non installé. Installez avec: pip install PyQt5")
        
        # Create container widget
        self._container_widget = QWidget(parent)
        layout = QHBoxLayout(self._container_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Create label if specified
        if self.label:
            self._label_widget = QLabel(self.label)
            self._label_widget.setFont(QFont(self.config.font_family, self.appearance.label_font_size))
            layout.addWidget(self._label_widget)
        
        # Create custom switch widget
        self._gui_widget = CustomSwitchWidget(self)
        self._gui_widget.setFixedSize(
            self.appearance.width + 20, 
            self.appearance.height + 20
        )
        layout.addWidget(self._gui_widget)
        
        return self._container_widget
    
    def _draw_switch_tkinter(self):
        """Draw switch on Tkinter canvas"""
        if not self._switch_canvas:
            return
        
        # Clear canvas
        self._switch_canvas.delete("all")
        
        # Calculate positions
        canvas_center_x = (self._switch_canvas.winfo_reqwidth()) / 2
        canvas_center_y = (self._switch_canvas.winfo_reqheight()) / 2
        
        track_x = canvas_center_x - self.appearance.width / 2
        track_y = canvas_center_y - self.appearance.height / 2
        
        # Apply scale transformation
        scaled_width = self.appearance.width * self._current_scale
        scaled_height = self.appearance.height * self._current_scale
        scale_offset_x = (self.appearance.width - scaled_width) / 2
        scale_offset_y = (self.appearance.height - scaled_height) / 2
        
        final_track_x = track_x + scale_offset_x
        final_track_y = track_y + scale_offset_y
        
        # Draw track shadow if enabled
        if self.appearance.shadow_enabled:
            shadow_x = final_track_x + self.appearance.shadow_offset[0]
            shadow_y = final_track_y + self.appearance.shadow_offset[1]
            
            self._switch_canvas.create_oval(
                shadow_x, shadow_y,
                shadow_x + scaled_width, shadow_y + scaled_height,
                fill=self.appearance.shadow_color,
                outline="",
                stipple="gray25",
                tags="track_shadow"
            )
        
        # Draw track (background)
        if self.appearance.style == SwitchStyle.MODERN:
            # Rounded rectangle for modern style
            self._switch_canvas.create_oval(
                final_track_x, final_track_y,
                final_track_x + scaled_width, final_track_y + scaled_height,
                fill=self._current_track_color.to_hex(),
                outline=self.appearance.border_color,
                width=self.appearance.border_width,
                tags="track"
            )
        else:
            # Rounded rectangle for other styles
            self._draw_rounded_rectangle_tkinter(
                final_track_x, final_track_y, scaled_width, scaled_height,
                self.appearance.corner_radius_track,
                fill=self._current_track_color.to_hex(),
                outline=self.appearance.border_color,
                width=self.appearance.border_width,
                tags="track"
            )
        
        # Calculate thumb position
        thumb_x = (final_track_x + self.appearance.track_padding + 
                  (self._thumb_position * self._thumb_travel_distance * self._current_scale))
        thumb_y = final_track_y + (scaled_height - self.appearance.thumb_size * self._current_scale) / 2
        thumb_size = self.appearance.thumb_size * self._current_scale
        
        # Draw thumb shadow
        if self.appearance.shadow_enabled and self._thumb_shadow.current_opacity > 0:
            shadow_thumb_x = thumb_x + self._thumb_shadow.current_offset.x
            shadow_thumb_y = thumb_y + self._thumb_shadow.current_offset.y
            
            shadow_stipple = f"gray{int((1 - self._thumb_shadow.current_opacity) * 100)}"
            
            self._switch_canvas.create_oval(
                shadow_thumb_x, shadow_thumb_y,
                shadow_thumb_x + thumb_size, shadow_thumb_y + thumb_size,
                fill=self.appearance.shadow_color,
                outline="",
                stipple=shadow_stipple,
                tags="thumb_shadow"
            )
        
        # Draw thumb
        self._switch_canvas.create_oval(
            thumb_x, thumb_y,
            thumb_x + thumb_size, thumb_y + thumb_size,
            fill=self._current_thumb_color.to_hex(),
            outline=self.appearance.border_color,
            width=self.appearance.border_width,
            tags="thumb"
        )
        
        # Draw state labels if specified
        if self.appearance.off_label or self.appearance.on_label:
            self._draw_state_labels_tkinter(final_track_x, final_track_y, scaled_width, scaled_height)
    
    def _draw_rounded_rectangle_tkinter(self, x: float, y: float, width: float, height: float,
                                       radius: int, **kwargs):
        """Draw rounded rectangle on Tkinter canvas (approximation)"""
        # Tkinter doesn't have native rounded rectangles, so we approximate
        # This is a simplified version - a full implementation would use polygon points
        self._switch_canvas.create_rectangle(
            x + radius, y, x + width - radius, y + height,
            **kwargs
        )
        
        # Add corner arcs (simplified)
        arc_kwargs = dict(kwargs)
        arc_kwargs.pop('tags', None)
        
        # Corner circles for rounded effect
        corner_size = radius * 2
        
        # Top-left
        self._switch_canvas.create_arc(
            x, y, x + corner_size, y + corner_size,
            start=90, extent=90, style="pieslice",
            **arc_kwargs
        )
        
        # Top-right  
        self._switch_canvas.create_arc(
            x + width - corner_size, y,
            x + width, y + corner_size,
            start=0, extent=90, style="pieslice",
            **arc_kwargs
        )
        
        # Bottom-left
        self._switch_canvas.create_arc(
            x, y + height - corner_size,
            x + corner_size, y + height,
            start=180, extent=90, style="pieslice",
            **arc_kwargs
        )
        
        # Bottom-right
        self._switch_canvas.create_arc(
            x + width - corner_size, y + height - corner_size,
            x + width, y + height,
            start=270, extent=90, style="pieslice",
            **arc_kwargs
        )
    
    def _draw_state_labels_tkinter(self, track_x: float, track_y: float, 
                                  track_width: float, track_height: float):
        """Draw ON/OFF labels on the track"""
        font_size = int(self.appearance.label_font_size * 0.8)
        
        # OFF label (left side)
        if self.appearance.off_label:
            off_x = track_x + track_width * 0.25
            off_y = track_y + track_height / 2
            
            # Adjust opacity based on thumb position
            off_opacity = 1.0 - self._thumb_position
            off_color = self._adjust_color_opacity(self.appearance.label_color, off_opacity)
            
            self._switch_canvas.create_text(
                off_x, off_y,
                text=self.appearance.off_label,
                fill=off_color,
                font=(self.config.font_family, font_size),
                tags="off_label"
            )
        
        # ON label (right side)
        if self.appearance.on_label:
            on_x = track_x + track_width * 0.75
            on_y = track_y + track_height / 2
            
            # Adjust opacity based on thumb position
            on_opacity = self._thumb_position
            on_color = self._adjust_color_opacity(self.appearance.label_color, on_opacity)
            
            self._switch_canvas.create_text(
                on_x, on_y,
                text=self.appearance.on_label,
                fill=on_color,
                font=(self.config.font_family, font_size),
                tags="on_label"
            )
    
    def _adjust_color_opacity(self, color_hex: str, opacity: float) -> str:
        """Adjust color opacity (approximation for Tkinter)"""
        if opacity <= 0:
            return self._container_widget.cget('bg')  # Background color
        elif opacity >= 1:
            return color_hex
        else:
            # Simple opacity approximation by blending with background
            color = ColorUtils.parse_color(color_hex)
            bg_color = ColorUtils.parse_color(self._container_widget.cget('bg'))
            blended = ColorUtils.interpolate_colors(bg_color, color, opacity)
            return blended.to_hex()
    
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
        
        # Return to normal state
        self._animate_hover_leave()
    
    def _on_press(self, event=None):
        """Handle mouse press"""
        if self.get_state() == "disabled":
            return
        
        self._is_pressed = True
        
        # Record drag start position
        if hasattr(event, 'x'):
            self._drag_start_x = event.x
            self._drag_start_position = self._thumb_position
            self._last_drag_time = time.time()
            self._last_drag_position = self._thumb_position
        
        # Scale down animation
        self._animation_manager.animate(
            "press_scale",
            self._current_scale,
            self.appearance.active_scale,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=0.1, easing=EasingType.EASE_OUT_QUAD)
        )
        
        # Enhanced shadow on press
        if self.appearance.shadow_enabled:
            self._thumb_shadow.animate_shadow(
                self._animation_manager, 
                self.appearance.shadow_opacity * 1.5, 
                0.1
            )
    
    def _on_release(self, event=None):
        """Handle mouse release"""
        if self.get_state() == "disabled":
            return
        
        was_dragging = self._is_dragging
        self._is_pressed = False
        self._is_dragging = False
        
        # Scale back up
        target_scale = self.appearance.hover_scale if self._is_hovered else 1.0
        self._animation_manager.animate(
            "release_scale",
            self._current_scale,
            target_scale,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=0.15, easing=EasingType.BOUNCE_OUT)
        )
        
        # Return shadow to normal
        if self.appearance.shadow_enabled:
            self._thumb_shadow.animate_shadow(
                self._animation_manager,
                self.appearance.shadow_opacity,
                0.2
            )
        
        # Handle state change
        if was_dragging:
            # Determine final state based on position and velocity
            self._finish_drag()
        else:
            # Simple click - toggle state
            self._toggle_state()
    
    def _on_drag(self, event=None):
        """Handle mouse drag"""
        if not self._is_pressed or self.get_state() == "disabled":
            return
        
        if not hasattr(event, 'x'):
            return
        
        # Check if we've moved far enough to start dragging
        drag_distance = abs(event.x - self._drag_start_x)
        if not self._is_dragging and drag_distance < self._drag_threshold:
            return
        
        self._is_dragging = True
        
        # Calculate new thumb position
        drag_delta = event.x - self._drag_start_x
        drag_progress = drag_delta / self._thumb_travel_distance
        new_position = GeometryUtils.clamp(
            self._drag_start_position + drag_progress, 
            0.0, 1.0
        )
        
        # Calculate drag velocity
        current_time = time.time()
        time_delta = current_time - self._last_drag_time
        if time_delta > 0:
            position_delta = new_position - self._last_drag_position
            self._drag_velocity = position_delta / time_delta
        
        self._last_drag_time = current_time
        self._last_drag_position = new_position
        
        # Update thumb position
        self._update_thumb_position(new_position)
        
        # Update colors based on position
        self._update_colors_from_position(new_position)
    
    def _on_click(self, event=None):
        """Handle click event (when not dragging)"""
        if self.get_state() == "disabled" or self._is_dragging:
            return
        
        self.trigger_callback('click')
    
    def _finish_drag(self):
        """Finish drag operation and determine final state"""
        # Determine target state based on position and velocity
        velocity_threshold = 2.0  # Minimum velocity to override position
        position_threshold = 0.5  # Position threshold for state change
        
        if abs(self._drag_velocity) > velocity_threshold:
            # High velocity - use velocity direction
            target_state = SwitchState.ON if self._drag_velocity > 0 else SwitchState.OFF
        else:
            # Low velocity - use position
            target_state = SwitchState.ON if self._thumb_position > position_threshold else SwitchState.OFF
        
        # Animate to final state
        self._animate_to_state(target_state)
    
    def _toggle_state(self):
        """Toggle between ON and OFF states"""
        new_state = SwitchState.OFF if self._current_state == SwitchState.ON else SwitchState.ON
        self._animate_to_state(new_state)
    
    def _animate_to_state(self, new_state: SwitchState):
        """Animate transition to new state"""
        old_state = self._current_state
        self._current_state = new_state
        
        # Determine target values
        target_position = 1.0 if new_state == SwitchState.ON else 0.0
        
        # Choose animation type
        if self.appearance.animation_type == SwitchAnimation.BOUNCE:
            easing = EasingType.BOUNCE_OUT
        elif self.appearance.animation_type == SwitchAnimation.ELASTIC:
            easing = EasingType.ELASTIC_OUT
        else:  # SLIDE or others
            easing = EasingType.EASE_OUT_CUBIC
        
        # Animate thumb position
        self._animation_manager.animate(
            "thumb_position",
            self._thumb_position,
            target_position,
            lambda pos: self._update_thumb_position(pos),
            AnimationConfig(
                duration=self.appearance.animation_duration,
                easing=easing
            )
        )
        
        # Animate track color
        target_track_color = (self.appearance.track_on_color if new_state == SwitchState.ON 
                             else self.appearance.track_off_color)
        
        self._animate_color_transition(
            self._current_track_color,
            ColorUtils.parse_color(target_track_color),
            "track"
        )
        
        # Animate thumb color  
        target_thumb_color = (self.appearance.thumb_on_color if new_state == SwitchState.ON
                             else self.appearance.thumb_off_color)
        
        self._animate_color_transition(
            self._current_thumb_color,
            ColorUtils.parse_color(target_thumb_color),
            "thumb"
        )
        
        # Trigger callbacks
        self.trigger_callback('state_changed', old_state, new_state)
        if new_state == SwitchState.ON:
            self.trigger_callback('switched_on')
        else:
            self.trigger_callback('switched_off')
    
    def _animate_hover_enter(self):
        """Animate hover enter effects"""
        if self.appearance.hover_scale != 1.0:
            self._animation_manager.animate(
                "hover_scale",
                self._current_scale,
                self.appearance.hover_scale,
                lambda value: self._update_scale(value),
                AnimationConfig(duration=0.2, easing=EasingType.EASE_OUT_QUAD)
            )
        
        # Enhance shadow on hover
        if self.appearance.shadow_enabled:
            self._thumb_shadow.animate_shadow(
                self._animation_manager,
                self.appearance.shadow_opacity * 1.2,
                0.2
            )
    
    def _animate_hover_leave(self):
        """Animate hover leave effects"""
        self._animation_manager.animate(
            "hover_leave_scale",
            self._current_scale,
            1.0,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=0.2, easing=EasingType.EASE_OUT_QUAD)
        )
        
        # Return shadow to normal
        if self.appearance.shadow_enabled:
            self._thumb_shadow.animate_shadow(
                self._animation_manager,
                self.appearance.shadow_opacity,
                0.2
            )
    
    def _animate_color_transition(self, start_color: Color, end_color: Color, element: str):
        """Animate color transition for track or thumb"""
        def update_color(progress: float):
            current_color = ColorUtils.interpolate_colors(start_color, end_color, progress)
            
            if element == "track":
                self._current_track_color = current_color
            elif element == "thumb":
                self._current_thumb_color = current_color
            
            self.update_appearance()
        
        self._animation_manager.animate(
            f"color_{element}",
            0.0,
            1.0,
            update_color,
            AnimationConfig(duration=self.appearance.animation_duration, 
                          easing=EasingType.EASE_OUT_CUBIC)
        )
    
    def _update_thumb_position(self, position: float):
        """Update thumb position"""
        self._thumb_position = GeometryUtils.clamp(position, 0.0, 1.0)
        self.update_appearance()
    
    def _update_scale(self, scale: float):
        """Update switch scale"""
        self._current_scale = scale
        self.update_appearance()
    
    def _update_colors_from_position(self, position: float):
        """Update colors based on thumb position (for drag feedback)"""
        # Interpolate track color
        off_color = ColorUtils.parse_color(self.appearance.track_off_color)
        on_color = ColorUtils.parse_color(self.appearance.track_on_color)
        self._current_track_color = ColorUtils.interpolate_colors(off_color, on_color, position)
        
        # Interpolate thumb color
        thumb_off = ColorUtils.parse_color(self.appearance.thumb_off_color)
        thumb_on = ColorUtils.parse_color(self.appearance.thumb_on_color)
        self._current_thumb_color = ColorUtils.interpolate_colors(thumb_off, thumb_on, position)
        
        self.update_appearance()
    
    def update_appearance(self):
        """Update switch appearance"""
        if self._gui_framework == "tkinter":
            self._draw_switch_tkinter()
        elif self._gui_framework == "pyqt5":
            if self._gui_widget:
                self._gui_widget.update()
    
    def is_on(self) -> bool:
        """Check if switch is in ON state"""
        return self._current_state == SwitchState.ON
    
    def get_switch_state(self) -> SwitchState:
        """Get current switch state"""
        return self._current_state
    
    def set_state(self, on: bool, animate: bool = True):
        """Set switch state programmatically"""
        new_state = SwitchState.ON if on else SwitchState.OFF
        
        if animate:
            self._animate_to_state(new_state)
        else:
            self._current_state = new_state
            self._thumb_position = 1.0 if on else 0.0
            
            # Update colors immediately
            if on:
                self._current_track_color = ColorUtils.parse_color(self.appearance.track_on_color)
                self._current_thumb_color = ColorUtils.parse_color(self.appearance.thumb_on_color)
            else:
                self._current_track_color = ColorUtils.parse_color(self.appearance.track_off_color)
                self._current_thumb_color = ColorUtils.parse_color(self.appearance.thumb_off_color)
            
            self.update_appearance()
    
    def set_colors(self, track_on: str = None, track_off: str = None,
                   thumb_on: str = None, thumb_off: str = None):
        """Update switch colors"""
        if track_on:
            self.appearance.track_on_color = track_on
        if track_off:
            self.appearance.track_off_color = track_off
        if thumb_on:
            self.appearance.thumb_on_color = thumb_on
        if thumb_off:
            self.appearance.thumb_off_color = thumb_off
        
        # Update current colors if needed
        if self._current_state == SwitchState.ON:
            if track_on:
                self._current_track_color = ColorUtils.parse_color(track_on)
            if thumb_on:
                self._current_thumb_color = ColorUtils.parse_color(thumb_on)
        else:
            if track_off:
                self._current_track_color = ColorUtils.parse_color(track_off)
            if thumb_off:
                self._current_thumb_color = ColorUtils.parse_color(thumb_off)
        
        self.update_appearance()
    
    def pulse_animation(self, duration: float = 1.0, intensity: float = 0.1):
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
    
    def glow_animation(self, color: str = "#4299e1", duration: float = 1.0):
        """Create glowing animation"""
        glow_color = ColorUtils.parse_color(color)
        original_track = self._current_track_color
        
        def glow_update(progress):
            if progress <= 0.5:
                # Glow in
                current = ColorUtils.interpolate_colors(original_track, glow_color, progress * 2)
            else:
                # Glow out
                current = ColorUtils.interpolate_colors(glow_color, original_track, (progress - 0.5) * 2)
            
            self._current_track_color = current
            self.update_appearance()
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_IN_OUT_QUAD)
        self._animation_manager.animate("glow", 0.0, 1.0, glow_update, config)
    
    def shake_animation(self, duration: float = 0.5):
        """Create shake animation for error feedback"""
        def shake_update(progress):
            offset = math.sin(progress * math.pi * 8) * 5 * (1 - progress)
            # Apply horizontal offset (implementation depends on framework)
            self._apply_shake_offset(offset)
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_OUT_CUBIC)
        self._animation_manager.animate("shake", 0.0, 1.0, shake_update, config)
    
    def _apply_shake_offset(self, offset: float):
        """Apply shake offset (framework-specific implementation)"""
        pass  # Implementation depends on GUI framework capabilities
    
    def flash_animation(self, flash_color: str = "#ffffff", duration: float = 0.4):
        """Create flash animation"""
        original_thumb = self._current_thumb_color
        flash_col = ColorUtils.parse_color(flash_color)
        
        def flash_update(progress):
            if progress <= 0.5:
                # Flash to color
                current = ColorUtils.interpolate_colors(original_thumb, flash_col, progress * 2)
            else:
                # Flash back to original
                current = ColorUtils.interpolate_colors(flash_col, original_thumb, (progress - 0.5) * 2)
            
            self._current_thumb_color = current
            self.update_appearance()
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_IN_OUT_QUAD)
        self._animation_manager.animate("flash", 0.0, 1.0, flash_update, config)
    
    def on_state_changed(self, callback: Callable):
        """Set callback for state changes"""
        self.bind_callback('state_changed', callback)
        return self
    
    def on_switched_on(self, callback: Callable):
        """Set callback for when switch turns ON"""
        self.bind_callback('switched_on', callback)
        return self
    
    def on_switched_off(self, callback: Callable):
        """Set callback for when switch turns OFF"""  
        self.bind_callback('switched_off', callback)
        return self
    
    def stop_all_animations(self):
        """Stop all switch animations"""
        self._animation_manager.stop_all_animations()
        super().stop_all_animations()
    
    def __del__(self):
        """Cleanup when switch is destroyed"""
        if hasattr(self, '_animation_manager'):
            self._animation_manager.stop_all_animations()

# PyQt5 Custom Widget Class
try:
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent, QLinearGradient
    
    class CustomSwitchWidget(QWidget):
        """Custom PyQt5 widget for advanced switch rendering"""
        
        state_changed = pyqtSignal(bool)
        
        def __init__(self, switch_instance):
            super().__init__()
            self.switch = switch_instance
            self.setMouseTracking(True)
        
        def paintEvent(self, event):
            """Custom paint event for switch"""
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Get current properties from switch instance
            width = self.switch.appearance.width
            height = self.switch.appearance.height
            scale = self.switch._current_scale
            
            # Calculate positions
            scaled_width = width * scale
            scaled_height = height * scale
            x = (self.width() - scaled_width) / 2
            y = (self.height() - scaled_height) / 2
            
            # Draw track
            track_color = QColor(self.switch._current_track_color.to_hex())
            painter.setBrush(QBrush(track_color))
            painter.setPen(QPen(QColor(self.switch.appearance.border_color), 
                              self.switch.appearance.border_width))
            painter.drawRoundedRect(
                x, y, scaled_width, scaled_height,
                self.switch.appearance.corner_radius_track,
                self.switch.appearance.corner_radius_track
            )
            
            # Calculate thumb position and size
            thumb_size = self.switch.appearance.thumb_size * scale
            thumb_x = (x + self.switch.appearance.track_padding + 
                      (self.switch._thumb_position * self.switch._thumb_travel_distance * scale))
            thumb_y = y + (scaled_height - thumb_size) / 2
            
            # Draw thumb shadow if enabled
            if self.switch.appearance.shadow_enabled and self.switch._thumb_shadow.current_opacity > 0:
                shadow_color = QColor(self.switch.appearance.shadow_color)
                shadow_color.setAlphaF(self.switch._thumb_shadow.current_opacity)
                
                shadow_x = thumb_x + self.switch._thumb_shadow.current_offset.x
                shadow_y = thumb_y + self.switch._thumb_shadow.current_offset.y
                
                painter.setBrush(QBrush(shadow_color))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(shadow_x, shadow_y, thumb_size, thumb_size)
            
            # Draw thumb
            thumb_color = QColor(self.switch._current_thumb_color.to_hex())
            painter.setBrush(QBrush(thumb_color))
            painter.setPen(QPen(QColor(self.switch.appearance.border_color), 
                              self.switch.appearance.border_width))
            painter.drawEllipse(thumb_x, thumb_y, thumb_size, thumb_size)
        
        def mousePressEvent(self, event: QMouseEvent):
            """Handle mouse press"""
            self.switch._on_press(event)
        
        def mouseReleaseEvent(self, event: QMouseEvent):
            """Handle mouse release"""
            self.switch._on_release(event)
        
        def mouseMoveEvent(self, event: QMouseEvent):
            """Handle mouse move"""
            if self.switch._is_pressed:
                self.switch._on_drag(event)
        
        def enterEvent(self, event):
            """Handle mouse enter"""
            self.switch._on_hover_enter(event)
        
        def leaveEvent(self, event):
            """Handle mouse leave"""
            self.switch._on_hover_leave(event)

except ImportError:
    # PyQt5 not available
    class CustomSwitchWidget:
        def __init__(self, switch_instance):
            pass