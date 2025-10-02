"""
Module scroll_view - Scrollable container with smooth animations
"""

import math
import time
from dataclasses import dataclass
from typing import Optional, Callable, Any, List, Tuple, Union
from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, AnimationConfig, EasingType
from .utils import ColorUtils, Color, Rectangle, Point, GeometryUtils

@dataclass
class ScrollBarStyle:
    """Scroll bar specific styling"""
    # Track styling
    track_color: str = "#f8f9fa"
    track_width: int = 12
    track_border_radius: int = 6
    track_border_color: str = "#e9ecef"
    track_border_width: int = 1
    
    # Thumb styling
    thumb_color: str = "#adb5bd"
    thumb_hover_color: str = "#6c757d"
    thumb_active_color: str = "#495057"
    thumb_border_radius: int = 6
    thumb_min_size: int = 20
    thumb_margin: int = 2
    
    # Visibility
    auto_hide: bool = True
    auto_hide_delay: float = 1.5
    fade_duration: float = 0.3
    always_visible: bool = False
    
    # Animation
    smooth_scrolling: bool = True
    scroll_animation_duration: float = 0.4

@dataclass
class ScrollViewStyle:
    """Scroll view specific styling"""
    # Container styling
    background_color: str = "#ffffff"
    border_color: str = "#dee2e6"
    border_width: int = 1
    border_radius: int = 8
    
    # Content area
    content_padding: int = 10
    
    # Scroll behavior
    horizontal_scroll_enabled: bool = True
    vertical_scroll_enabled: bool = True
    scroll_sensitivity: float = 1.0
    momentum_enabled: bool = True
    momentum_friction: float = 0.95
    
    # Visual effects
    shadow_enabled: bool = True
    shadow_color: str = "#00000020"
    shadow_offset: tuple = (0, 2)
    shadow_blur: int = 4
    
    # Elastic scrolling
    elastic_enabled: bool = True
    elastic_distance: int = 50
    elastic_resistance: float = 0.3

class ScrollBar:
    """Individual scroll bar component"""
    
    def __init__(self, orientation: str, style: ScrollBarStyle, scroll_view):
        self.orientation = orientation  # "vertical" or "horizontal"
        self.style = style
        self.scroll_view = scroll_view
        
        # State
        self.visible = False
        self.opacity = 0.0
        self.is_hovering = False
        self.is_dragging = False
        
        # Geometry
        self.track_rect = Rectangle(0, 0, 0, 0)
        self.thumb_rect = Rectangle(0, 0, 0, 0)
        
        # Dragging state
        self.drag_start_pos = None
        self.drag_start_scroll = 0
        
        # Animation
        self.animation_manager = AnimationManager()
        
        # Auto-hide timer
        self.hide_timer = None
    
    def update_geometry(self, container_rect: Rectangle, content_size: Tuple[int, int]):
        """Update scroll bar geometry"""
        container_width, container_height = container_rect.width, container_rect.height
        content_width, content_height = content_size
        
        if self.orientation == "vertical":
            # Vertical scroll bar
            if content_height <= container_height:
                self.visible = False if not self.style.always_visible else True
                return
            
            self.visible = True
            
            # Track geometry
            self.track_rect = Rectangle(
                container_rect.x + container_width - self.style.track_width,
                container_rect.y,
                self.style.track_width,
                container_height
            )
            
            # Thumb geometry
            thumb_height = max(
                self.style.thumb_min_size,
                int((container_height / content_height) * container_height)
            )
            
            scroll_ratio = abs(self.scroll_view._scroll_y) / (content_height - container_height)
            scroll_ratio = GeometryUtils.clamp(scroll_ratio, 0.0, 1.0)
            
            thumb_y = container_rect.y + scroll_ratio * (container_height - thumb_height)
            
            self.thumb_rect = Rectangle(
                self.track_rect.x + self.style.thumb_margin,
                thumb_y,
                self.style.track_width - 2 * self.style.thumb_margin,
                thumb_height
            )
            
        else:  # horizontal
            # Horizontal scroll bar
            if content_width <= container_width:
                self.visible = False if not self.style.always_visible else True
                return
            
            self.visible = True
            
            # Track geometry
            self.track_rect = Rectangle(
                container_rect.x,
                container_rect.y + container_height - self.style.track_width,
                container_width,
                self.style.track_width
            )
            
            # Thumb geometry
            thumb_width = max(
                self.style.thumb_min_size,
                int((container_width / content_width) * container_width)
            )
            
            scroll_ratio = abs(self.scroll_view._scroll_x) / (content_width - container_width)
            scroll_ratio = GeometryUtils.clamp(scroll_ratio, 0.0, 1.0)
            
            thumb_x = container_rect.x + scroll_ratio * (container_width - thumb_width)
            
            self.thumb_rect = Rectangle(
                thumb_x,
                self.track_rect.y + self.style.thumb_margin,
                thumb_width,
                self.style.track_width - 2 * self.style.thumb_margin
            )
    
    def draw(self, canvas):
        """Draw the scroll bar"""
        if not self.visible or self.opacity <= 0:
            return
        
        # Calculate colors with opacity
        track_color = ColorUtils.parse_color(self.style.track_color)
        track_with_alpha = Color(track_color.r, track_color.g, track_color.b, self.opacity * 0.8)
        
        if self.is_dragging:
            thumb_color = ColorUtils.parse_color(self.style.thumb_active_color)
        elif self.is_hovering:
            thumb_color = ColorUtils.parse_color(self.style.thumb_hover_color)
        else:
            thumb_color = ColorUtils.parse_color(self.style.thumb_color)
        
        thumb_with_alpha = Color(thumb_color.r, thumb_color.g, thumb_color.b, self.opacity)
        
        if hasattr(canvas, 'create_rectangle'):  # Tkinter
            # Draw track
            canvas.create_rectangle(
                self.track_rect.x, self.track_rect.y,
                self.track_rect.x + self.track_rect.width,
                self.track_rect.y + self.track_rect.height,
                fill=track_with_alpha.to_hex(),
                outline="",
                tags="scrollbar_track"
            )
            
            # Draw thumb
            canvas.create_rectangle(
                self.thumb_rect.x, self.thumb_rect.y,
                self.thumb_rect.x + self.thumb_rect.width,
                self.thumb_rect.y + self.thumb_rect.height,
                fill=thumb_with_alpha.to_hex(),
                outline="",
                tags="scrollbar_thumb"
            )
    
    def show(self):
        """Show scroll bar with animation"""
        if self.style.auto_hide and not self.style.always_visible:
            # Cancel hide timer if active
            if self.hide_timer:
                self.hide_timer = None
            
            # Fade in
            config = AnimationConfig(
                duration=self.style.fade_duration,
                easing=EasingType.EASE_OUT_QUAD
            )
            
            self.animation_manager.animate(
                "fade_in", self.opacity, 1.0,
                lambda opacity: setattr(self, 'opacity', opacity),
                config
            )
        else:
            self.opacity = 1.0
    
    def hide(self):
        """Hide scroll bar with animation"""
        if self.style.always_visible:
            return
        
        if self.style.auto_hide:
            # Start hide timer
            def delayed_hide():
                time.sleep(self.style.auto_hide_delay)
                if not self.is_hovering and not self.is_dragging:
                    config = AnimationConfig(
                        duration=self.style.fade_duration,
                        easing=EasingType.EASE_OUT_QUAD
                    )
                    
                    self.animation_manager.animate(
                        "fade_out", self.opacity, 0.0,
                        lambda opacity: setattr(self, 'opacity', opacity),
                        config
                    )
            
            import threading
            self.hide_timer = threading.Thread(target=delayed_hide, daemon=True)
            self.hide_timer.start()
        else:
            self.opacity = 0.0

class AnimatedScrollView(AnimatedWidget):
    """
    Animated scrollable container with smooth scrolling and custom scroll bars
    """
    
    def __init__(self, config: Optional[WidgetConfig] = None,
                 style: Optional[ScrollViewStyle] = None,
                 scrollbar_style: Optional[ScrollBarStyle] = None):
        super().__init__(config)
        self.style = style or ScrollViewStyle()
        self.scrollbar_style = scrollbar_style or ScrollBarStyle()
        
        # Scroll state
        self._scroll_x = 0.0
        self._scroll_y = 0.0
        self._target_scroll_x = 0.0
        self._target_scroll_y = 0.0
        
        # Content dimensions
        self._content_width = 0
        self._content_height = 0
        
        # Momentum scrolling
        self._momentum_x = 0.0
        self._momentum_y = 0.0
        self._last_scroll_time = 0
        
        # Elastic scrolling
        self._elastic_x = 0.0
        self._elastic_y = 0.0
        
        # GUI components
        self._gui_widget = None
        self._gui_framework = None
        self._canvas = None
        self._content_frame = None
        
        # Scroll bars
        self._v_scrollbar = ScrollBar("vertical", self.scrollbar_style, self)
        self._h_scrollbar = ScrollBar("horizontal", self.scrollbar_style, self)
        
        # Animation manager
        self._animation_manager = AnimationManager()
        
        # Event tracking
        self._is_dragging = False
        self._drag_start_pos = None
        self._drag_start_scroll = None
        self._last_mouse_pos = None
        self._mouse_velocity = Point(0, 0)
        
        # Child widgets
        self._child_widgets = []
        
        # Performance optimization
        self._needs_redraw = True
        self._last_render_hash = None
        
        # Touch/gesture support
        self._touch_points = {}
        self._pinch_scale = 1.0
        self._pinch_center = Point(0, 0)
    
    def render(self, parent_widget, framework: str = "tkinter"):
        """Render the scroll view"""
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
        
        # Create main frame
        self._gui_widget = tk.Frame(
            parent,
            width=self.config.width,
            height=self.config.height,
            relief="solid",
            bd=self.style.border_width,
            bg=self.style.background_color
        )
        
        # Create canvas for scrollable content
        self._canvas = tk.Canvas(
            self._gui_widget,
            width=self.config.width - 2 * self.style.border_width,
            height=self.config.height - 2 * self.style.border_width,
            highlightthickness=0,
            bg=self.style.background_color
        )
        self._canvas.pack(fill="both", expand=True)
        
        # Create content frame
        self._content_frame = tk.Frame(self._canvas, bg=self.style.background_color)
        self._canvas_window = self._canvas.create_window(
            0, 0, anchor="nw", window=self._content_frame
        )
        
        # Bind events
        self._canvas.bind("<Button-1>", self._on_mouse_down)
        self._canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self._canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self._canvas.bind("<Button-4>", self._on_mouse_wheel)  # Linux
        self._canvas.bind("<Button-5>", self._on_mouse_wheel)  # Linux
        self._canvas.bind("<Enter>", self._on_mouse_enter)
        self._canvas.bind("<Leave>", self._on_mouse_leave)
        self._canvas.bind("<Motion>", self._on_mouse_motion)
        
        # Bind content frame resize
        self._content_frame.bind("<Configure>", self._on_content_configure)
        
        # Focus for keyboard events
        self._canvas.focus_set()
        self._canvas.bind("<Key>", self._on_key_press)
        
        # Initial draw
        self._update_scroll_region()
        self._draw_scroll_view()
    
    def _render_pyqt5(self, parent):
        """Render with PyQt5"""
        try:
            from PyQt5.QtWidgets import (QScrollArea, QWidget, QVBoxLayout, 
                                       QHBoxLayout, QFrame)
            from PyQt5.QtCore import Qt, QTimer
            from PyQt5.QtGui import QPainter
            
            class ScrollWidget(QScrollArea):
                def __init__(self, scroll_view_instance):
                    super().__init__()
                    self.scroll_view = scroll_view_instance
                    self.setFixedSize(
                        self.scroll_view.config.width,
                        self.scroll_view.config.height
                    )
                    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                    
                    # Create content widget
                    self.content_widget = QWidget()
                    self.setWidget(self.content_widget)
                    self.setWidgetResizable(True)
                
                def paintEvent(self, event):
                    super().paintEvent(event)
                    painter = QPainter(self)
                    painter.setRenderHint(QPainter.Antialiasing)
                    self.scroll_view._draw_scroll_bars_pyqt5(painter)
                
                def wheelEvent(self, event):
                    self.scroll_view._on_wheel_pyqt5(event)
            
            self._gui_widget = ScrollWidget(self)
            self._content_frame = self._gui_widget.content_widget
            
        except ImportError:
            raise ImportError("PyQt5 not installed. Install with: pip install PyQt5")
    
    def _draw_scroll_view(self):
        """Draw the scroll view and scroll bars"""
        if not self._canvas:
            return
        
        # Clear scroll bar drawings
        if hasattr(self._canvas, 'delete'):
            self._canvas.delete("scrollbar_track")
            self._canvas.delete("scrollbar_thumb")
        
        # Update scroll bar geometry
        container_rect = Rectangle(0, 0, self.config.width, self.config.height)
        content_size = (self._content_width, self._content_height)
        
        self._v_scrollbar.update_geometry(container_rect, content_size)
        self._h_scrollbar.update_geometry(container_rect, content_size)
        
        # Draw scroll bars
        self._v_scrollbar.draw(self._canvas)
        self._h_scrollbar.draw(self._canvas)
        
        # Update content position
        self._update_content_position()
    
    def _update_content_position(self):
        """Update the position of content within the scroll view"""
        if not self._canvas or not hasattr(self._canvas, 'coords'):
            return
        
        # Calculate final scroll position including elastic effect
        final_x = self._scroll_x + self._elastic_x
        final_y = self._scroll_y + self._elastic_y
        
        # Update canvas window position
        self._canvas.coords(self._canvas_window, -final_x, -final_y)
        
        # Update scroll region
        self._update_scroll_region()
    
    def _update_scroll_region(self):
        """Update the scrollable region"""
        if not self._canvas:
            return
        
        # Get content size
        self._content_frame.update_idletasks()
        self._content_width = self._content_frame.winfo_reqwidth()
        self._content_height = self._content_frame.winfo_reqheight()
        
        # Set scroll region
        self._canvas.configure(scrollregion=(
            0, 0, self._content_width, self._content_height
        ))
    
    def _on_content_configure(self, event):
        """Handle content frame resize"""
        self._content_width = event.width
        self._content_height = event.height
        self._update_scroll_region()
        self._draw_scroll_view()
    
    def _on_mouse_down(self, event):
        """Handle mouse down for dragging"""
        self._is_dragging = True
        self._drag_start_pos = Point(event.x, event.y)
        self._drag_start_scroll = Point(self._scroll_x, self._scroll_y)
        self._last_mouse_pos = Point(event.x, event.y)
        self._mouse_velocity = Point(0, 0)
        self._last_scroll_time = time.time()
        
        # Stop any ongoing momentum
        self._animation_manager.stop_animation("momentum")
        self._animation_manager.stop_animation("smooth_scroll")
        
        # Check scroll bar interactions
        mouse_point = Point(event.x, event.y)
        
        if self._v_scrollbar.visible and self._v_scrollbar.thumb_rect.contains_point(mouse_point):
            self._v_scrollbar.is_dragging = True
            self._v_scrollbar.drag_start_pos = event.y
            self._v_scrollbar.drag_start_scroll = self._scroll_y
        
        if self._h_scrollbar.visible and self._h_scrollbar.thumb_rect.contains_point(mouse_point):
            self._h_scrollbar.is_dragging = True
            self._h_scrollbar.drag_start_pos = event.x
            self._h_scrollbar.drag_start_scroll = self._scroll_x
        
        self.trigger_callback('drag_start', event)
    
    def _on_mouse_drag(self, event):
        """Handle mouse dragging"""
        if not self._is_dragging:
            return
        
        current_pos = Point(event.x, event.y)
        current_time = time.time()
        
        # Calculate velocity for momentum
        if self._last_mouse_pos and current_time > self._last_scroll_time:
            dt = current_time - self._last_scroll_time
            if dt > 0:
                self._mouse_velocity.x = (current_pos.x - self._last_mouse_pos.x) / dt
                self._mouse_velocity.y = (current_pos.y - self._last_mouse_pos.y) / dt
        
        # Handle scroll bar dragging
        if self._v_scrollbar.is_dragging:
            self._handle_scrollbar_drag("vertical", event)
        elif self._h_scrollbar.is_dragging:
            self._handle_scrollbar_drag("horizontal", event)
        else:
            # Handle content dragging
            if self.style.horizontal_scroll_enabled:
                dx = current_pos.x - self._drag_start_pos.x
                target_x = self._drag_start_scroll.x - dx
                self._scroll_to_x(target_x, animate=False)
            
            if self.style.vertical_scroll_enabled:
                dy = current_pos.y - self._drag_start_pos.y
                target_y = self._drag_start_scroll.y - dy
                self._scroll_to_y(target_y, animate=False)
        
        self._last_mouse_pos = current_pos
        self._last_scroll_time = current_time
        
        self.trigger_callback('drag', event)
    
    def _on_mouse_up(self, event):
        """Handle mouse up"""
        if not self._is_dragging:
            return
        
        self._is_dragging = False
        self._v_scrollbar.is_dragging = False
        self._h_scrollbar.is_dragging = False
        
        # Apply momentum if enabled
        if self.style.momentum_enabled and not (self._v_scrollbar.is_dragging or self._h_scrollbar.is_dragging):
            self._apply_momentum()
        
        # Handle elastic snap back
        self._handle_elastic_bounds()
        
        # Auto-hide scroll bars
        self._v_scrollbar.hide()
        self._h_scrollbar.hide()
        
        self.trigger_callback('drag_end', event)
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling"""
        # Calculate scroll delta
        if hasattr(event, 'delta'):  # Windows
            delta = -event.delta / 120.0
        elif hasattr(event, 'num'):  # Linux
            delta = 1 if event.num == 5 else -1
        else:
            delta = -event.delta if hasattr(event, 'delta') else 0
        
        # Apply sensitivity
        delta *= self.style.scroll_sensitivity * 20
        
        # Determine scroll direction based on modifier keys
        if hasattr(event, 'state') and event.state & 0x1:  # Shift key
            # Horizontal scroll
            if self.style.horizontal_scroll_enabled:
                self.scroll_by(delta, 0)
        else:
            # Vertical scroll
            if self.style.vertical_scroll_enabled:
                self.scroll_by(0, delta)
        
        # Show scroll bars
        self._v_scrollbar.show()
        self._h_scrollbar.show()
        
        self.trigger_callback('wheel', event)
    
    def _on_mouse_enter(self, event):
        """Handle mouse enter"""
        self.set_state("hover")
        
        # Show scroll bars
        if self._v_scrollbar.visible:
            self._v_scrollbar.show()
        if self._h_scrollbar.visible:
            self._h_scrollbar.show()
    
    def _on_mouse_leave(self, event):
        """Handle mouse leave"""
        self.set_state("normal")
        
        # Check if leaving scroll bars
        mouse_point = Point(event.x, event.y)
        
        if not (self._v_scrollbar.track_rect.contains_point(mouse_point) or 
                self._h_scrollbar.track_rect.contains_point(mouse_point)):
            self._v_scrollbar.is_hovering = False
            self._h_scrollbar.is_hovering = False
            
            # Hide scroll bars
            self._v_scrollbar.hide()
            self._h_scrollbar.hide()
    
    def _on_mouse_motion(self, event):
        """Handle mouse motion for scroll bar hover effects"""
        mouse_point = Point(event.x, event.y)
        
        # Check vertical scroll bar hover
        if self._v_scrollbar.visible:
            was_hovering = self._v_scrollbar.is_hovering
            self._v_scrollbar.is_hovering = self._v_scrollbar.track_rect.contains_point(mouse_point)
            
            if self._v_scrollbar.is_hovering != was_hovering:
                self._draw_scroll_view()
        
        # Check horizontal scroll bar hover
        if self._h_scrollbar.visible:
            was_hovering = self._h_scrollbar.is_hovering
            self._h_scrollbar.is_hovering = self._h_scrollbar.track_rect.contains_point(mouse_point)
            
            if self._h_scrollbar.is_hovering != was_hovering:
                self._draw_scroll_view()
    
    def _on_key_press(self, event):
        """Handle keyboard scrolling"""
        scroll_amount = 20
        
        if event.keysym == "Up":
            self.scroll_by(0, -scroll_amount)
        elif event.keysym == "Down":
            self.scroll_by(0, scroll_amount)
        elif event.keysym == "Left":
            self.scroll_by(-scroll_amount, 0)
        elif event.keysym == "Right":
            self.scroll_by(scroll_amount, 0)
        elif event.keysym == "Prior":  # Page Up
            self.scroll_by(0, -self.config.height * 0.8)
        elif event.keysym == "Next":  # Page Down
            self.scroll_by(0, self.config.height * 0.8)
        elif event.keysym == "Home":
            self.scroll_to(0, 0)
        elif event.keysym == "End":
            self.scroll_to(0, self._content_height - self.config.height)
    
    def _handle_scrollbar_drag(self, orientation: str, event):
        """Handle scroll bar thumb dragging"""
        if orientation == "vertical":
            scrollbar = self._v_scrollbar
            current_pos = event.y
            
            # Calculate scroll position based on thumb position
            track_height = scrollbar.track_rect.height
            thumb_height = scrollbar.thumb_rect.height
            available_space = track_height - thumb_height
            
            if available_space > 0:
                drag_delta = current_pos - scrollbar.drag_start_pos
                scroll_ratio = drag_delta / available_space
                max_scroll = self._content_height - self.config.height
                
                new_scroll = scrollbar.drag_start_scroll + (scroll_ratio * max_scroll)
                self._scroll_to_y(new_scroll, animate=False)
        
        else:  # horizontal
            scrollbar = self._h_scrollbar
            current_pos = event.x
            
            # Calculate scroll position based on thumb position
            track_width = scrollbar.track_rect.width
            thumb_width = scrollbar.thumb_rect.width
            available_space = track_width - thumb_width
            
            if available_space > 0:
                drag_delta = current_pos - scrollbar.drag_start_pos
                scroll_ratio = drag_delta / available_space
                max_scroll = self._content_width - self.config.width
                
                new_scroll = scrollbar.drag_start_scroll + (scroll_ratio * max_scroll)
                self._scroll_to_x(new_scroll, animate=False)
    
    def _apply_momentum(self):
        """Apply momentum scrolling after drag release"""
        if abs(self._mouse_velocity.x) < 10 and abs(self._mouse_velocity.y) < 10:
            return
        
        # Calculate momentum distance
        momentum_x = self._mouse_velocity.x * 100  # Adjust multiplier as needed
        momentum_y = self._mouse_velocity.y * 100
        
        # Start momentum animation
        start_time = time.time()
        initial_velocity_x = momentum_x
        initial_velocity_y = momentum_y
        
        def update_momentum(progress):
            current_time = time.time()
            dt = current_time - start_time
            
            # Apply friction
            velocity_x = initial_velocity_x * (self.style.momentum_friction ** (dt * 60))
            velocity_y = initial_velocity_y * (self.style.momentum_friction ** (dt * 60))
            
            # Calculate displacement
            displacement_x = velocity_x * (1/60)  # Assuming 60 FPS
            displacement_y = velocity_y * (1/60)
            
            # Apply scroll
            if abs(displacement_x) > 0.1 or abs(displacement_y) > 0.1:
                self.scroll_by(displacement_x, displacement_y, animate=False)
                
                # Continue if velocity is significant
                if abs(velocity_x) > 1 or abs(velocity_y) > 1:
                    return True
            
            return False
        
        # Start momentum loop
        self._start_momentum_loop(update_momentum)
    
    def _start_momentum_loop(self, update_function):
        """Start momentum animation loop"""
        def momentum_step():
            if update_function(0):
                # Schedule next frame
                if self._gui_framework == "tkinter" and self._canvas:
                    self._canvas.after(16, momentum_step)  # ~60 FPS
        
        momentum_step()
    
    def _handle_elastic_bounds(self):
        """Handle elastic scrolling bounds"""
        if not self.style.elastic_enabled:
            return
        
        # Check X bounds
        max_scroll_x = max(0, self._content_width - self.config.width)
        if self._scroll_x < 0:
            # Snap back from left
            self._animate_elastic_return("x", 0)
        elif self._scroll_x > max_scroll_x:
            # Snap back from right
            self._animate_elastic_return("x", max_scroll_x)
        
        # Check Y bounds
        max_scroll_y = max(0, self._content_height - self.config.height)
        if self._scroll_y < 0:
            # Snap back from top
            self._animate_elastic_return("y", 0)
        elif self._scroll_y > max_scroll_y:
            # Snap back from bottom
            self._animate_elastic_return("y", max_scroll_y)
    
    def _animate_elastic_return(self, axis: str, target_position: float):
        """Animate elastic return to bounds"""
        config = AnimationConfig(
            duration=0.4,
            easing=EasingType.EASE_OUT_CUBIC
        )
        
        if axis == "x":
            start_pos = self._scroll_x
            
            def update_x(pos):
                self._scroll_x = pos
                self._update_content_position()
                self._draw_scroll_view()
            
            self._animation_manager.animate(
                "elastic_x", start_pos, target_position, update_x, config
            )
        else:  # y
            start_pos = self._scroll_y
            
            def update_y(pos):
                self._scroll_y = pos
                self._update_content_position()
                self._draw_scroll_view()
            
            self._animation_manager.animate(
                "elastic_y", start_pos, target_position, update_y, config
            )
    
    def _scroll_to_x(self, x: float, animate: bool = True):
        """Scroll to specific X position"""
        max_scroll = max(0, self._content_width - self.config.width)
        
        if self.style.elastic_enabled:
            # Allow over-scroll with resistance
            if x < 0:
                x = x * self.style.elastic_resistance
            elif x > max_scroll:
                over_scroll = x - max_scroll
                x = max_scroll + (over_scroll * self.style.elastic_resistance)
        else:
            x = GeometryUtils.clamp(x, 0, max_scroll)
        
        if animate and self.scrollbar_style.smooth_scrolling:
            config = AnimationConfig(
                duration=self.scrollbar_style.scroll_animation_duration,
                easing=EasingType.EASE_OUT_CUBIC
            )
            
            def update_x(pos):
                self._scroll_x = pos
                self._update_content_position()
                self._draw_scroll_view()
            
            self._animation_manager.animate(
                "smooth_scroll_x", self._scroll_x, x, update_x, config
            )
        else:
            self._scroll_x = x
            self._update_content_position()
            self._draw_scroll_view()
    
    def _scroll_to_y(self, y: float, animate: bool = True):
        """Scroll to specific Y position"""
        max_scroll = max(0, self._content_height - self.config.height)
        
        if self.style.elastic_enabled:
            # Allow over-scroll with resistance
            if y < 0:
                y = y * self.style.elastic_resistance
            elif y > max_scroll:
                over_scroll = y - max_scroll
                y = max_scroll + (over_scroll * self.style.elastic_resistance)
        else:
            y = GeometryUtils.clamp(y, 0, max_scroll)
        
        if animate and self.scrollbar_style.smooth_scrolling:
            config = AnimationConfig(
                duration=self.scrollbar_style.scroll_animation_duration,
                easing=EasingType.EASE_OUT_CUBIC
            )
            
            def update_y(pos):
                self._scroll_y = pos
                self._update_content_position()
                self._draw_scroll_view()
            
            self._animation_manager.animate(
                "smooth_scroll_y", self._scroll_y, y, update_y, config
            )
        else:
            self._scroll_y = y
            self._update_content_position()
            self._draw_scroll_view()
    
    def scroll_to(self, x: float, y: float, animate: bool = True):
        """Scroll to specific position"""
        if self.style.horizontal_scroll_enabled:
            self._scroll_to_x(x, animate)
        if self.style.vertical_scroll_enabled:
            self._scroll_to_y(y, animate)
    
    def scroll_by(self, dx: float, dy: float, animate: bool = True):
        """Scroll by relative amount"""
        new_x = self._scroll_x + dx
        new_y = self._scroll_y + dy
        self.scroll_to(new_x, new_y, animate)
    
    def get_scroll_position(self) -> Tuple[float, float]:
        """Get current scroll position"""
        return (self._scroll_x, self._scroll_y)
    
    def get_content_size(self) -> Tuple[int, int]:
        """Get content size"""
        return (self._content_width, self._content_height)
    
    def add_widget(self, widget, **pack_options):
        """Add widget to scrollable content"""
        self._child_widgets.append(widget)
        widget.pack(in_=self._content_frame, **pack_options)
        
        # Update content size
        self._content_frame.update_idletasks()
        self._update_scroll_region()
        self._draw_scroll_view()
    
    def remove_widget(self, widget):
        """Remove widget from scrollable content"""
        if widget in self._child_widgets:
            self._child_widgets.remove(widget)
            widget.pack_forget()
            
            # Update content size
            self._content_frame.update_idletasks()
            self._update_scroll_region()
            self._draw_scroll_view()
    
    def clear_widgets(self):
        """Remove all widgets from scrollable content"""
        for widget in self._child_widgets:
            widget.pack_forget()
        self._child_widgets.clear()
        
        self._update_scroll_region()
        self._draw_scroll_view()
    
    def scroll_to_widget(self, widget, animate: bool = True):
        """Scroll to make widget visible"""
        try:
            # Get widget position relative to content frame
            widget_x = widget.winfo_x()
            widget_y = widget.winfo_y()
            widget_width = widget.winfo_width()
            widget_height = widget.winfo_height()
            
            # Calculate scroll position to center widget
            center_x = widget_x + widget_width / 2 - self.config.width / 2
            center_y = widget_y + widget_height / 2 - self.config.height / 2
            
            self.scroll_to(center_x, center_y, animate)
        except:
            pass  # Widget might not be mapped yet
    
    def set_scroll_sensitivity(self, sensitivity: float):
        """Set scroll sensitivity"""
        self.style.scroll_sensitivity = sensitivity
    
    def enable_momentum(self, enabled: bool = True, friction: float = None):
        """Enable/disable momentum scrolling"""
        self.style.momentum_enabled = enabled
        if friction is not None:
            self.style.momentum_friction = friction
    
    def enable_elastic(self, enabled: bool = True, distance: int = None, resistance: float = None):
        """Enable/disable elastic scrolling"""
        self.style.elastic_enabled = enabled
        if distance is not None:
            self.style.elastic_distance = distance
        if resistance is not None:
            self.style.elastic_resistance = resistance
    
    def set_scrollbar_style(self, auto_hide: bool = None, always_visible: bool = None,
                           track_color: str = None, thumb_color: str = None):
        """Update scroll bar styling"""
        if auto_hide is not None:
            self.scrollbar_style.auto_hide = auto_hide
        if always_visible is not None:
            self.scrollbar_style.always_visible = always_visible
        if track_color is not None:
            self.scrollbar_style.track_color = track_color
        if thumb_color is not None:
            self.scrollbar_style.thumb_color = thumb_color
        
        self._draw_scroll_view()
    
    def update_appearance(self):
        """Update widget appearance"""
        self._needs_redraw = True
        self._draw_scroll_view()
    
    def on_scroll(self, callback: Callable[[float, float], None]):
        """Set scroll callback"""
        self.bind_callback('scroll', callback)
        return self
    
    def on_drag_start(self, callback: Callable):
        """Set drag start callback"""
        self.bind_callback('drag_start', callback)
        return self
    
    def on_drag_end(self, callback: Callable):
        """Set drag end callback"""
        self.bind_callback('drag_end', callback)
        return self
    
    def stop_all_animations(self):
        """Stop all animations"""
        self._animation_manager.stop_all_animations()
        self._v_scrollbar.animation_manager.stop_all_animations()
        self._h_scrollbar.animation_manager.stop_all_animations()
        super().stop_all_animations()
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, '_animation_manager'):
            self._animation_manager.stop_all_animations()
        if hasattr(self, '_v_scrollbar'):
            self._v_scrollbar.animation_manager.stop_all_animations()
        if hasattr(self, '_h_scrollbar'):
            self._h_scrollbar.animation_manager.stop_all_animations()