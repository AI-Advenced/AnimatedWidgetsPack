"""
Module progress_bar - Animated progress indicators
"""

import math
import time
import threading
from dataclasses import dataclass
from typing import Optional, Callable, Any, Union, List
from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, AnimationConfig, EasingType
from .utils import ColorUtils, Color, Rectangle, Point, GeometryUtils

@dataclass
class ProgressBarStyle:
    """Progress bar specific styling"""
    # Background (track) styling
    background_color: str = "#ecf0f1"
    background_border_radius: int = 10
    background_border_width: int = 1
    background_border_color: str = "#bdc3c7"
    
    # Progress fill styling
    fill_color: str = "#3498db"
    fill_gradient_enabled: bool = True
    fill_gradient_colors: List[str] = None
    fill_border_radius: int = 8
    
    # Text styling
    show_text: bool = True
    text_color: str = "#2c3e50"
    text_format: str = "{value}%"  # Format string for display
    text_font_size: int = 12
    text_position: str = "center"  # "center", "left", "right", "outside"
    
    # Animation settings
    fill_animation_duration: float = 0.5
    text_animation_duration: float = 0.3
    smooth_animation: bool = True
    
    # Visual effects
    pulse_enabled: bool = False
    pulse_color: str = "#ffffff"
    pulse_opacity: float = 0.3
    pulse_duration: float = 1.5
    
    glow_enabled: bool = False
    glow_color: str = "#3498db"
    glow_size: int = 4
    glow_intensity: float = 0.5
    
    # Striped pattern
    stripes_enabled: bool = False
    stripe_color: str = "#ffffff"
    stripe_opacity: float = 0.2
    stripe_width: int = 20
    stripe_angle: float = 45  # degrees
    stripe_animation_speed: float = 2.0  # pixels per frame
    
    # Shadow effect
    shadow_enabled: bool = True
    shadow_color: str = "#2c3e50"
    shadow_offset: tuple = (0, 2)
    shadow_blur: int = 4
    shadow_opacity: float = 0.2

@dataclass
class ProgressSegment:
    """Individual segment for segmented progress bars"""
    start_value: float
    end_value: float
    color: str
    label: str = ""

class AnimatedProgressBar(AnimatedWidget):
    """
    Animated progress bar with customizable styling and effects
    Supports linear and circular progress indicators
    """
    
    def __init__(self, initial_value: float = 0.0,
                 min_value: float = 0.0, max_value: float = 100.0,
                 config: Optional[WidgetConfig] = None,
                 style: Optional[ProgressBarStyle] = None,
                 circular: bool = False):
        super().__init__(config)
        self.style = style or ProgressBarStyle()
        
        # Initialize default gradient colors if not provided
        if self.style.fill_gradient_colors is None:
            self.style.fill_gradient_colors = [self.style.fill_color, ColorUtils.lighten_color(self.style.fill_color, 0.2).to_hex()]
        
        # Progress state
        self._min_value = min_value
        self._max_value = max_value
        self._current_value = initial_value
        self._display_value = initial_value  # For animated value display
        self._target_value = initial_value
        
        # Visual properties
        self._current_fill_width = self._calculate_fill_width(initial_value)
        self._current_fill_color = ColorUtils.parse_color(self.style.fill_color)
        self._pulse_opacity = 0.0
        self._glow_intensity = 0.0
        self._stripe_offset = 0.0
        
        # Shape properties
        self._is_circular = circular
        self._circle_start_angle = -90  # Start from top
        self._circle_sweep_angle = 0
        
        # Animation manager
        self._animation_manager = AnimationManager()
        
        # GUI components
        self._gui_widget = None
        self._gui_framework = None
        self._canvas = None
        
        # Segments for multi-colored progress
        self._segments: List[ProgressSegment] = []
        
        # Animation states
        self._is_indeterminate = False
        self._indeterminate_position = 0.0
        self._indeterminate_direction = 1
        
        # Performance optimization
        self._last_render_hash = None
        self._needs_redraw = True
        
        # Text measurement cache
        self._text_metrics_cache = {}
        
        # Background pattern
        self._background_pattern = None
    
    def _draw_rounded_rectangle(self, x, y, width, height, radius, fill, outline, tag):
        """
        Draw a rounded rectangle on the Tkinter canvas
        """
        if not hasattr(self._canvas, "create_polygon"):
            return
    
        # Ensure radius is not larger than half width/height
        radius = min(radius, width//2, height//2)
    
        # Points for rounded rectangle
        points = [
            (x+radius, y),
            (x+width-radius, y),
            (x+width, y),
            (x+width, y+radius),
            (x+width, y+height-radius),
            (x+width, y+height),
            (x+width-radius, y+height),
            (x+radius, y+height),
            (x, y+height),
            (x, y+height-radius),
            (x, y+radius),
            (x, y)
        ]
    
        # Draw main rectangle body
        self._canvas.create_rectangle(
            x+radius, y, x+width-radius, y+height,
            fill=fill, outline=outline, tags=tag
        )
        self._canvas.create_rectangle(
            x, y+radius, x+width, y+height-radius,
            fill=fill, outline=outline, tags=tag
        )
    
        # Draw 4 arcs for corners
        self._canvas.create_arc(x, y, x+2*radius, y+2*radius,
                                start=90, extent=90,
                                fill=fill, outline=outline, tags=tag)
        self._canvas.create_arc(x+width-2*radius, y, x+width, y+2*radius,
                                start=0, extent=90,
                                fill=fill, outline=outline, tags=tag)
        self._canvas.create_arc(x+width-2*radius, y+height-2*radius, x+width, y+height,
                                start=270, extent=90,
                                fill=fill, outline=outline, tags=tag)
        self._canvas.create_arc(x, y+height-2*radius, x+2*radius, y+height,
                                start=180, extent=90,
                                fill=fill, outline=outline, tags=tag)
    

    
    def render(self, parent_widget, framework: str = "tkinter"):
        """
        Render the progress bar in the specified GUI framework
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
        """Render with Tkinter using Canvas"""
        import tkinter as tk
        
        # Calculate total size including glow
        total_width = self.config.width + (self.style.glow_size * 2 if self.style.glow_enabled else 0)
        total_height = self.config.height + (self.style.glow_size * 2 if self.style.glow_enabled else 0)
        
        if self._is_circular:
            # Circular progress - use square canvas
            size = max(total_width, total_height)
            total_width = total_height = size
        
        # Create frame container
        self._gui_widget = tk.Frame(parent, bg=parent.cget('bg') if hasattr(parent, 'cget') else 'white')
        
        # Create canvas
        self._canvas = tk.Canvas(
            self._gui_widget,
            width=total_width,
            height=total_height,
            highlightthickness=0,
            bg=parent.cget('bg') if hasattr(parent, 'cget') else 'white'
        )
        self._canvas.pack()
        
        # Bind events for interactive features
        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<Enter>", self._on_mouse_enter)
        self._canvas.bind("<Leave>", self._on_mouse_leave)
        
        # Initial draw
        self._draw_progress_bar()
    
    def _render_pyqt5(self, parent):
        """Render with PyQt5"""
        try:
            from PyQt5.QtWidgets import QWidget
            from PyQt5.QtCore import QTimer
            from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QConicalGradient
            
            class ProgressWidget(QWidget):
                def __init__(self, progress_instance):
                    super().__init__()
                    self.progress = progress_instance
                    self.setFixedSize(
                        self.progress.config.width + 20,
                        self.progress.config.height + 20
                    )
                
                def paintEvent(self, event):
                    painter = QPainter(self)
                    painter.setRenderHint(QPainter.Antialiasing)
                    self.progress._draw_pyqt5(painter)
                
                def mousePressEvent(self, event):
                    self.progress._on_click_pyqt5(event)
            
            self._gui_widget = ProgressWidget(self)
            
        except ImportError:
            raise ImportError("PyQt5 not installed. Install with: pip install PyQt5")
    
    def _render_canvas(self, canvas):
        """Render directly on provided canvas"""
        self._canvas = canvas
        self._gui_widget = canvas
        self._draw_progress_bar()
    
    def _draw_progress_bar(self):
        """Main drawing method"""
        if not self._canvas:
            return
        
        # Check if redraw is needed
        current_hash = self._calculate_render_hash()
        if not self._needs_redraw and current_hash == self._last_render_hash:
            return
        
        # Clear canvas
        if hasattr(self._canvas, 'delete'):
            self._canvas.delete("all")
        
        if self._is_circular:
            self._draw_circular_progress()
        else:
            self._draw_linear_progress()
        
        # Update render state
        self._last_render_hash = current_hash
        self._needs_redraw = False
    
    def _draw_linear_progress(self):
        """Draw linear progress bar"""
        glow_offset = self.style.glow_size if self.style.glow_enabled else 0
        x = glow_offset
        y = glow_offset
        width = self.config.width
        height = self.config.height
        
        # Draw glow effect
        if self.style.glow_enabled and self._glow_intensity > 0:
            self._draw_glow_effect_linear(x, y, width, height)
        
        # Draw shadow
        if self.style.shadow_enabled:
            self._draw_fill_linear(x, y, width, height)
        
        # Draw background
        self._draw_background_linear(x, y, width, height)
        
        # Draw progress fill
        if not self._is_indeterminate:
            self._draw_fill_linear(x, y, width, height)
        else:
            self._draw_indeterminate_linear(x, y, width, height)
        
        # Draw segments if any
        if self._segments:
            self._draw_segments_linear(x, y, width, height)
        
        # Draw stripes
        if self.style.stripes_enabled:
            self._draw_stripes_linear(x, y, width, height)
        
        # Draw pulse effect
        if self.style.pulse_enabled and self._pulse_opacity > 0:
            self._draw_pulse_linear(x, y, width, height)
        
        # Draw text
        if self.style.show_text:
            self._draw_text_linear(x, y, width, height)
    
    def _draw_circular_progress(self):
        """Draw circular progress bar"""
        center_x = self.config.width // 2 + (self.style.glow_size if self.style.glow_enabled else 0)
        center_y = self.config.height // 2 + (self.style.glow_size if self.style.glow_enabled else 0)
        radius = min(self.config.width, self.config.height) // 2 - 10
        
        # Draw glow effect
        if self.style.glow_enabled and self._glow_intensity > 0:
            self._draw_glow_effect_circular(center_x, center_y, radius)
        
        # Draw background circle
        self._draw_background_circular(center_x, center_y, radius)
        
        # Draw progress arc
        if not self._is_indeterminate:
            self._draw_fill_circular(center_x, center_y, radius)
        else:
            self._draw_indeterminate_circular(center_x, center_y, radius)
        
        # Draw text in center
        if self.style.show_text:
            self._draw_text_circular(center_x, center_y)
    
    def _draw_background_linear(self, x: float, y: float, width: float, height: float):
        """Draw linear background"""
        if not hasattr(self._canvas, 'create_rectangle'):
            return
        
        # Draw main background
        self._canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=self.style.background_color,
            outline=self.style.background_border_color,
            width=self.style.background_border_width,
            tags="background"
        )
        
        # Add rounded corners if needed
        if self.style.background_border_radius > 0:
            self._draw_rounded_rectangle(
                x, y, width, height,
                self.style.background_border_radius,
                self.style.background_color,
                self.style.background_border_color,
                "background"
            )
    
    def _draw_fill_linear(self, x: float, y: float, width: float, height: float):
        """Draw linear progress fill"""
        if self._current_fill_width <= 0:
            return
        
        fill_width = min(self._current_fill_width, width - 4)  # Account for borders
        fill_x = x + 2
        fill_y = y + 2
        fill_height = height - 4
        
        if self.style.fill_gradient_enabled and len(self.style.fill_gradient_colors) > 1:
            self._draw_gradient_fill(fill_x, fill_y, fill_width, fill_height)
        else:
            # Simple solid fill
            if hasattr(self._canvas, 'create_rectangle'):
                self._canvas.create_rectangle(
                    fill_x, fill_y,
                    fill_x + fill_width, fill_y + fill_height,
                    fill=self._current_fill_color.to_hex(),
                    outline="",
                    tags="fill"
                )
    
    def _draw_gradient_fill(self, x: float, y: float, width: float, height: float):
        """Draw gradient fill (approximated for Tkinter)"""
        if not hasattr(self._canvas, 'create_rectangle'):
            return
        
        # Tkinter doesn't support gradients natively, so we approximate with strips
        num_strips = min(int(width), 50)  # Limit for performance
        
        colors = [ColorUtils.parse_color(c) for c in self.style.fill_gradient_colors]
        
        for i in range(num_strips):
            progress = i / (num_strips - 1) if num_strips > 1 else 0
            
            # Interpolate between gradient colors
            if len(colors) == 2:
                color = ColorUtils.interpolate_colors(colors[0], colors[1], progress)
            else:
                # Multi-color gradient
                segment_size = 1.0 / (len(colors) - 1)
                segment_index = int(progress / segment_size)
                segment_progress = (progress % segment_size) / segment_size
                
                if segment_index >= len(colors) - 1:
                    color = colors[-1]
                else:
                    color = ColorUtils.interpolate_colors(
                        colors[segment_index], 
                        colors[segment_index + 1], 
                        segment_progress
                    )
            
            strip_x = x + (width * i / num_strips)
            strip_width = width / num_strips + 1  # Overlap slightly to avoid gaps
            
            self._canvas.create_rectangle(
                strip_x, y,
                strip_x + strip_width, y + height,
                fill=color.to_hex(),
                outline="",
                tags="fill"
            )
    
    def _draw_stripes_linear(self, x: float, y: float, width: float, height: float):
        """Draw animated stripes pattern"""
        if not hasattr(self._canvas, 'create_polygon'):
            return
        
        stripe_color = ColorUtils.parse_color(self.style.stripe_color)
        stripe_with_alpha = Color(
            stripe_color.r, stripe_color.g, stripe_color.b, 
            self.style.stripe_opacity
        )
        
        # Calculate stripe parameters
        angle_rad = math.radians(self.style.stripe_angle)
        stripe_spacing = self.style.stripe_width * 2
        
        # Draw stripes within fill area
        fill_width = self._current_fill_width
        if fill_width <= 0:
            return
        
        # Calculate number of stripes needed
        diagonal_length = math.sqrt(width**2 + height**2)
        num_stripes = int(diagonal_length / stripe_spacing) + 2
        
        for i in range(num_stripes):
            # Calculate stripe position with animation offset
            stripe_pos = (i * stripe_spacing) + self._stripe_offset
            
            # Calculate stripe vertices
            x1 = x + 2 + stripe_pos
            y1 = y + 2
            x2 = x1 + self.style.stripe_width
            y2 = y1
            x3 = x2 + height * math.tan(angle_rad)
            y3 = y1 + height - 4
            x4 = x1 + height * math.tan(angle_rad)
            y4 = y3
            
            # Clip to fill area
            if x1 > x + fill_width:
                break
            
            # Create stripe polygon
            try:
                self._canvas.create_polygon(
                    x1, y1, x2, y2, x3, y3, x4, y4,
                    fill=stripe_with_alpha.to_hex(),
                    outline="",
                    tags="stripes"
                )
            except:
                # Fallback to rectangles if polygon fails
                self._canvas.create_rectangle(
                    x1, y1, min(x2, x + fill_width), y3,
                    fill=stripe_with_alpha.to_hex(),
                    outline="",
                    tags="stripes"
                )
    
    def _draw_pulse_linear(self, x: float, y: float, width: float, height: float):
        """Draw pulse effect"""
        if self._pulse_opacity <= 0:
            return
        
        pulse_color = ColorUtils.parse_color(self.style.pulse_color)
        pulse_with_alpha = Color(
            pulse_color.r, pulse_color.g, pulse_color.b,
            self._pulse_opacity
        )
        
        fill_width = self._current_fill_width
        if fill_width > 0 and hasattr(self._canvas, 'create_rectangle'):
            self._canvas.create_rectangle(
                x + 2, y + 2,
                x + 2 + fill_width, y + height - 2,
                fill=pulse_with_alpha.to_hex(),
                outline="",
                tags="pulse"
            )
    
    def _draw_text_linear(self, x: float, y: float, width: float, height: float):
        """Draw progress text"""
        if not hasattr(self._canvas, 'create_text'):
            return
        
        # Format text
        text = self._format_text(self._display_value)
        
        # Calculate position
        text_y = y + height / 2
        
        if self.style.text_position == "center":
            text_x = x + width / 2
            anchor = "center"
        elif self.style.text_position == "left":
            text_x = x + 10
            anchor = "w"
        elif self.style.text_position == "right":
            text_x = x + width - 10
            anchor = "e"
        else:  # outside
            text_x = x + width + 10
            anchor = "w"
        
        # Draw text
        self._canvas.create_text(
            text_x, text_y,
            text=text,
            font=(self.config.font_family, self.style.text_font_size),
            fill=self.style.text_color,
            anchor=anchor,
            tags="text"
        )
    
    def _draw_indeterminate_linear(self, x: float, y: float, width: float, height: float):
        """Draw indeterminate progress animation"""
        if not hasattr(self._canvas, 'create_rectangle'):
            return
        
        # Calculate moving block parameters
        block_width = width * 0.3  # 30% of total width
        total_travel = width - block_width
        
        # Calculate current position
        block_x = x + 2 + (total_travel * self._indeterminate_position)
        block_y = y + 2
        block_height = height - 4
        
        # Draw the moving block
        self._canvas.create_rectangle(
            block_x, block_y,
            block_x + block_width, block_y + block_height,
            fill=self._current_fill_color.to_hex(),
            outline="",
            tags="indeterminate"
        )
        
        # Add gradient effect to the block
        if self.style.fill_gradient_enabled:
            self._draw_gradient_fill(block_x, block_y, block_width, block_height)
    
    def _draw_glow_effect_linear(self, x: float, y: float, width: float, height: float):
        """Draw glow effect around linear progress bar"""
        if not hasattr(self._canvas, 'create_rectangle'):
            return
        
        glow_color = ColorUtils.parse_color(self.style.glow_color)
        
        for i in range(3):
            alpha = self._glow_intensity * (0.3 - i * 0.1)
            if alpha <= 0:
                continue
            
            glow_size = self.style.glow_size + i * 2
            glow_with_alpha = Color(glow_color.r, glow_color.g, glow_color.b, alpha)
            
            self._canvas.create_rectangle(
                x - glow_size, y - glow_size,
                x + width + glow_size, y + height + glow_size,
                fill="", outline=glow_with_alpha.to_hex(),
                width=2, tags="glow"
            )
    
    def _calculate_fill_width(self, value: float) -> float:
        """Calculate fill width based on value"""
        if self._max_value <= self._min_value:
            return 0
        
        progress = (value - self._min_value) / (self._max_value - self._min_value)
        progress = GeometryUtils.clamp(progress, 0.0, 1.0)
        
        return (self.config.width - 4) * progress  # Account for borders
    
    def _format_text(self, value: float) -> str:
        """Format value for display"""
        try:
            if "{value}" in self.style.text_format:
                return self.style.text_format.format(value=int(value))
            elif "{percent}" in self.style.text_format:
                percent = (value - self._min_value) / (self._max_value - self._min_value) * 100
                return self.style.text_format.format(percent=int(percent))
            else:
                return self.style.text_format
        except:
            return f"{int(value)}%"
    
    def _calculate_render_hash(self) -> int:
        """Calculate hash for render optimization"""
        return hash((
            self._current_value, self._display_value, self._current_fill_width,
            self._pulse_opacity, self._glow_intensity, self._stripe_offset,
            self._indeterminate_position, str(self._current_fill_color),
            self.get_state()
        ))
    
    def _animate_to_value(self, target_value: float):
        """Animate progress to target value"""
        target_value = GeometryUtils.clamp(target_value, self._min_value, self._max_value)
        
        if target_value == self._current_value:
            return
        
        start_value = self._current_value
        start_fill_width = self._current_fill_width
        target_fill_width = self._calculate_fill_width(target_value)
        
        # Animation config
        config = AnimationConfig(
            duration=self.style.fill_animation_duration,
            easing=EasingType.EASE_OUT_CUBIC if self.style.smooth_animation else EasingType.LINEAR
        )
        
        # Animate fill width
        def update_fill(width):
            self._current_fill_width = width
            # Calculate corresponding value for display
            if self.config.width > 4:
                progress = width / (self.config.width - 4)
                self._current_value = self._min_value + progress * (self._max_value - self._min_value)
            self._needs_redraw = True
            self._draw_progress_bar()
        
        self._animation_manager.animate(
            "fill_animation",
            start_fill_width,
            target_fill_width,
            update_fill,
            config,
            completion_callback=lambda: self._on_value_animation_complete(target_value)
        )
        
        # Animate text value separately if enabled
        if self.style.show_text:
            text_config = AnimationConfig(
                duration=self.style.text_animation_duration,
                easing=EasingType.EASE_OUT_QUAD
            )
            
            def update_display_value(value):
                self._display_value = value
                self._needs_redraw = True
                self._draw_progress_bar()
            
            self._animation_manager.animate(
                "text_animation",
                start_value,
                target_value,
                update_display_value,
                text_config
            )
    
    def _on_value_animation_complete(self, final_value: float):
        """Handle value animation completion"""
        self._current_value = final_value
        self._display_value = final_value
        self._target_value = final_value
        
        self.trigger_callback('value_changed', final_value)
        self.trigger_callback('animation_complete', final_value)
    
    def _start_indeterminate_animation(self):
        """Start indeterminate progress animation"""
        if not self._is_indeterminate:
            return
        
        def update_position(position):
            # Bounce back and forth
            if position >= 1.0:
                self._indeterminate_direction = -1
                position = 1.0
            elif position <= 0.0:
                self._indeterminate_direction = 1
                position = 0.0
            
            self._indeterminate_position = position
            self._needs_redraw = True
            self._draw_progress_bar()
            
            # Continue animation
            if self._is_indeterminate:
                next_position = position + (0.02 * self._indeterminate_direction)
                self._animation_manager.animate(
                    "indeterminate",
                    position,
                    next_position,
                    update_position,
                    AnimationConfig(duration=0.05, easing=EasingType.LINEAR)
                )
        
        # Start the animation
        update_position(self._indeterminate_position)
    
    def _start_stripe_animation(self):
        """Start stripe animation"""
        if not self.style.stripes_enabled:
            return
        
        def update_stripe_offset(offset):
            self._stripe_offset = offset % (self.style.stripe_width * 2)
            self._needs_redraw = True
            self._draw_progress_bar()
            
            # Continue animation
            if self.style.stripes_enabled:
                next_offset = offset + self.style.stripe_animation_speed
                self._animation_manager.animate(
                    "stripes",
                    offset,
                    next_offset,
                    update_stripe_offset,
                    AnimationConfig(duration=0.03, easing=EasingType.LINEAR)
                )
        
        update_stripe_offset(self._stripe_offset)
    
    def _start_pulse_animation(self):
        """Start pulse animation"""
        if not self.style.pulse_enabled:
            return
        
        config = AnimationConfig(
            duration=self.style.pulse_duration,
            easing=EasingType.EASE_IN_OUT_QUAD,
            auto_reverse=True,
            repeat_count=-1  # Infinite
        )
        
        def update_pulse(opacity):
            self._pulse_opacity = opacity
            self._needs_redraw = True
            self._draw_progress_bar()
        
        self._animation_manager.animate(
            "pulse",
            0.0,
            self.style.pulse_opacity,
            update_pulse,
            config
        )
    
    def set_value(self, value: float, animate: bool = True):
        """Set progress value"""
        value = GeometryUtils.clamp(value, self._min_value, self._max_value)
        
        if animate and self.style.fill_animation_duration > 0:
            self._target_value = value
            self._animate_to_value(value)
        else:
            self._current_value = value
            self._display_value = value
            self._target_value = value
            self._current_fill_width = self._calculate_fill_width(value)
            self._needs_redraw = True
            self._draw_progress_bar()
            self.trigger_callback('value_changed', value)
    
    def get_value(self) -> float:
        """Get current progress value"""
        return self._current_value
    
    def set_range(self, min_value: float, max_value: float):
        """Set value range"""
        self._min_value = min_value
        self._max_value = max_value
        
        # Recalculate current fill width
        self._current_fill_width = self._calculate_fill_width(self._current_value)
        self._needs_redraw = True
        self._draw_progress_bar()
    
    def get_range(self) -> tuple:
        """Get current range"""
        return (self._min_value, self._max_value)
    
    def set_indeterminate(self, enabled: bool = True):
        """Enable/disable indeterminate mode"""
        if self._is_indeterminate == enabled:
            return
        
        self._is_indeterminate = enabled
        
        if enabled:
            self._indeterminate_position = 0.0
            self._indeterminate_direction = 1
            self._start_indeterminate_animation()
        else:
            self._animation_manager.stop_animation("indeterminate")
        
        self._needs_redraw = True
        self._draw_progress_bar()
    
    def add_segment(self, start_value: float, end_value: float, color: str, label: str = ""):
        """Add colored segment"""
        segment = ProgressSegment(start_value, end_value, color, label)
        self._segments.append(segment)
        self._needs_redraw = True
        self._draw_progress_bar()
    
    def clear_segments(self):
        """Clear all segments"""
        self._segments.clear()
        self._needs_redraw = True
        self._draw_progress_bar()
    
    def set_colors(self, background: str = None, fill: str = None, text: str = None):
        """Update colors"""
        if background:
            self.style.background_color = background
        if fill:
            self.style.fill_color = fill
            self._current_fill_color = ColorUtils.parse_color(fill)
        if text:
            self.style.text_color = text
        
        self._needs_redraw = True
        self._draw_progress_bar()
    
    def enable_pulse(self, enabled: bool = True, color: str = None, opacity: float = None):
        """Enable/disable pulse effect"""
        self.style.pulse_enabled = enabled
        if color:
            self.style.pulse_color = color
        if opacity:
            self.style.pulse_opacity = opacity
        
        if enabled:
            self._start_pulse_animation()
        else:
            self._animation_manager.stop_animation("pulse")
            self._pulse_opacity = 0.0
        
        self._needs_redraw = True
        self._draw_progress_bar()
    
    def enable_stripes(self, enabled: bool = True, color: str = None, 
                      width: int = None, speed: float = None):
        """Enable/disable stripe animation"""
        self.style.stripes_enabled = enabled
        if color:
            self.style.stripe_color = color
        if width:
            self.style.stripe_width = width
        if speed:
            self.style.stripe_animation_speed = speed
        
        if enabled:
            self._start_stripe_animation()
        else:
            self._animation_manager.stop_animation("stripes")
        
        self._needs_redraw = True
        self._draw_progress_bar()
    
    def flash_animation(self, color: str = "#ffffff", duration: float = 0.4):
        """Create flash animation"""
        original_color = self._current_fill_color
        flash_color = ColorUtils.parse_color(color)
        
        def flash_update(progress):
            if progress <= 0.5:
                current = ColorUtils.interpolate_colors(original_color, flash_color, progress * 2)
            else:
                current = ColorUtils.interpolate_colors(flash_color, original_color, (progress - 0.5) * 2)
            
            self._current_fill_color = current
            self._needs_redraw = True
            self._draw_progress_bar()
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_IN_OUT_QUAD)
        self._animation_manager.animate("flash", 0.0, 1.0, flash_update, config)
    
    def increment(self, amount: float = 1.0, animate: bool = True):
        """Increment progress value"""
        new_value = self._target_value + amount
        self.set_value(new_value, animate)
    
    def decrement(self, amount: float = 1.0, animate: bool = True):
        """Decrement progress value"""
        new_value = self._target_value - amount
        self.set_value(new_value, animate)
    
    def reset(self, animate: bool = True):
        """Reset to minimum value"""
        self.set_value(self._min_value, animate)
    
    def complete(self, animate: bool = True):
        """Set to maximum value"""
        self.set_value(self._max_value, animate)
    
    def _on_click(self, event):
        """Handle click for interactive progress bars"""
        if self.get_state() == "disabled" or self._is_indeterminate:
            return
        
        # Calculate clicked position
        glow_offset = self.style.glow_size if self.style.glow_enabled else 0
        click_x = event.x - glow_offset - 2  # Account for borders
        
        if 0 <= click_x <= self.config.width - 4:
            # Calculate value based on click position
            progress = click_x / (self.config.width - 4)
            new_value = self._min_value + progress * (self._max_value - self._min_value)
            
            self.set_value(new_value, animate=True)
            self.trigger_callback('click', new_value)
    
    def _on_mouse_enter(self, event):
        """Handle mouse enter"""
        if self.get_state() == "disabled":
            return
        
        self.set_state("hover")
        
        # Start hover glow
        if self.style.glow_enabled:
            config = AnimationConfig(duration=0.2, easing=EasingType.EASE_OUT_QUAD)
            self._animation_manager.animate(
                "hover_glow", self._glow_intensity, 0.5,
                lambda intensity: setattr(self, '_glow_intensity', intensity) or self._draw_progress_bar(),
                config
            )
    
    def _on_mouse_leave(self, event):
        """Handle mouse leave"""
        if self.get_state() == "disabled":
            return
        
        self.set_state("normal")
        
        # Stop hover glow
        if self.style.glow_enabled:
            config = AnimationConfig(duration=0.3, easing=EasingType.EASE_OUT_QUAD)
            self._animation_manager.animate(
                "leave_glow", self._glow_intensity, 0.0,
                lambda intensity: setattr(self, '_glow_intensity', intensity) or self._draw_progress_bar(),
                config
            )
    
    def update_appearance(self):
        """Update widget appearance"""
        self._needs_redraw = True
        self._draw_progress_bar()
    
    def on_value_changed(self, callback: Callable[[float], None]):
        """Set value change callback"""
        self.bind_callback('value_changed', callback)
        return self
    
    def on_click(self, callback: Callable[[float], None]):
        """Set click callback"""
        self.bind_callback('click', callback)
        return self
    
    def stop_all_animations(self):
        """Stop all animations"""
        self._animation_manager.stop_all_animations()
        super().stop_all_animations()
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, '_animation_manager'):
            self._animation_manager.stop_all_animations()