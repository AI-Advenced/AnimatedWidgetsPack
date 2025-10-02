"""
Module core - Base class for all animated widgets
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Callable, Optional, Tuple
import threading
import time
import math

@dataclass
class WidgetConfig:
    """Base configuration for widgets"""
    width: int = 120
    height: int = 40
    background_color: str = "#3498db"
    text_color: str = "#ffffff"
    border_radius: int = 8
    border_width: int = 0
    border_color: str = "#2c3e50"
    font_family: str = "Arial"
    font_size: int = 12
    animation_duration: float = 0.3
    enable_animations: bool = True

class AnimatedWidget(ABC):
    """
    Abstract base class for all animated widgets
    Provides common animation and state management functionality
    """
    
    def __init__(self, config: Optional[WidgetConfig] = None):
        self.config = config or WidgetConfig()
        self._callbacks: Dict[str, list] = {
            'click': [],
            'hover_enter': [],
            'hover_leave': [],
            'value_changed': [],
            'state_changed': [],
            'focus_in': [],
            'focus_out': [],
            'validation_error': [],
            'switched_on': [],
            'switched_off': [],
            'checked': [],
            'unchecked': []
        }
        self._current_animations: Dict[str, threading.Thread] = {}
        self._widget_state = "normal"  # normal, hover, pressed, disabled
        self._is_animating = False
        
    @abstractmethod
    def render(self, parent_widget):
        """Abstract method for widget rendering"""
        pass
    
    @abstractmethod
    def update_appearance(self):
        """Abstract method for updating widget appearance"""
        pass
    
    def bind_callback(self, event_type: str, callback: Callable):
        """Bind a callback function to an event"""
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
    
    def trigger_callback(self, event_type: str, *args, **kwargs):
        """Trigger all callbacks for an event type"""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error in callback {event_type}: {e}")
   
    # Ajouter ces nouvelles méthodes à la classe AnimatedWidget
    
    def set_size(self, width: int, height: int, animate: bool = True):
        """Change widget size with optional animation"""
        if animate and self.config.enable_animations:
            # Animate size change
            start_width = self.config.width
            start_height = self.config.height
            
            def update_size(progress):
                current_width = start_width + (width - start_width) * progress
                current_height = start_height + (height - start_height) * progress
                self.config.width = int(current_width)
                self.config.height = int(current_height)
                self.update_appearance()
            
            self.animate_property("size_animation", 0.0, 1.0, 
                                duration=self.config.animation_duration, 
                                easing_function=self._ease_out_cubic)
            
            # Set callback to update size during animation
            self._current_animations["size_animation"].update_callback = update_size
        else:
            self.config.width = width
            self.config.height = height
            self.update_appearance()
    
    def pulse_effect(self, duration: float = 1.0, scale_factor: float = 1.1):
        """Generic pulse effect for any widget"""
        def pulse_update(value):
            # This should be overridden by specific widgets
            pass
        
        config = {
            'duration': duration,
            'easing': self._ease_in_out_quad,
            'auto_reverse': True,
            'repeat_count': 1
        }
        
        self.animate_property("pulse", 1.0, scale_factor, 
                             duration=duration,
                             easing_function=self._ease_in_out_quad)
    
    def shake_effect(self, duration: float = 0.5, intensity: float = 5.0):
        """Generic shake effect"""
        original_x = getattr(self, 'x', 0)
        
        def shake_update(progress):
            # Sine wave shake
            offset = math.sin(progress * math.pi * 8) * intensity * (1 - progress)
            # This should be implemented by specific widgets
            pass
        
        self.animate_property("shake", 0.0, 1.0, 
                             duration=duration,
                             easing_function=self._ease_out_cubic)
    
    def fade_in(self, duration: float = 0.3):
        """Fade in animation"""
        self.animate_property("opacity", 0.0, 1.0, 
                             duration=duration,
                             easing_function=self._ease_out_quad)
    
    def fade_out(self, duration: float = 0.3):
        """Fade out animation"""
        self.animate_property("opacity", 1.0, 0.0, 
                             duration=duration,
                             easing_function=self._ease_out_quad)
    
    def slide_in(self, direction: str = "left", duration: float = 0.4):
        """Slide in from direction"""
        # This should be implemented by specific widgets based on their rendering
        pass
    
    def get_animation_state(self) -> dict:
        """Get current animation state information"""
        return {
            'is_animating': self.is_animating(),
            'active_animations': list(self._current_animations.keys()),
            'animation_count': len(self._current_animations),
            'widget_state': self._widget_state
        }

   
    # Ajouter ces nouvelles méthodes utilitaires à la classe AnimatedWidget :
    
    def animate_shake(self, intensity: float = 5.0, duration: float = 0.5):
        """Create a shake animation for error feedback"""
        def shake_update(progress):
            import math
            offset = math.sin(progress * math.pi * 8) * intensity * (1 - progress)
            # Store offset for framework-specific implementation
            self._shake_offset = offset
            self.update_appearance()
        
        self.animate_property("shake_progress", 0.0, 1.0, duration, self._ease_out_cubic)
    
    def animate_glow(self, glow_color: str = "#3498db", duration: float = 1.0):
        """Create a glow animation effect"""
        def glow_update(progress):
            import math
            glow_intensity = math.sin(progress * math.pi * 2) * 0.5 + 0.5
            # Store glow properties for framework-specific implementation
            self._glow_intensity = glow_intensity
            self._glow_color = glow_color
            self.update_appearance()
        
        self.animate_property("glow_progress", 0.0, 1.0, duration, self._ease_in_out_quad)
    
    def animate_pulse(self, scale_factor: float = 1.1, duration: float = 1.0):
        """Create a pulse animation effect"""
        def pulse_update(progress):
            import math
            pulse_scale = 1.0 + (scale_factor - 1.0) * (math.sin(progress * math.pi * 2) * 0.5 + 0.5)
            self._pulse_scale = pulse_scale
            self.update_appearance()
        
        self.animate_property("pulse_progress", 0.0, 1.0, duration, self._ease_in_out_quad)
    
    def _ease_in_out_quad(self, t: float) -> float:
        """Quadratic in-out easing function"""
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

   
    # Dans la classe AnimatedWidget, ajouter ces méthodes:
    
    def animate_multiple_properties(self, property_animations: Dict[str, Tuple[float, float]], 
                                  duration: float = None, easing_function: Callable = None):
        """
        Animate multiple properties simultaneously
        property_animations: dict of {property_name: (start_value, end_value)}
        """
        duration = duration or self.config.animation_duration
        easing_function = easing_function or self._ease_out_cubic
        
        for property_name, (start_value, end_value) in property_animations.items():
            self.animate_property(property_name, start_value, end_value, duration, easing_function)
    
    def animate_to_state(self, target_state: str, property_mapping: Dict[str, Dict[str, float]]):
        """
        Animate widget to a specific state with property mappings
        property_mapping: {state: {property: value}}
        """
        if target_state not in property_mapping:
            return
        
        current_state = self.get_state()
        if current_state in property_mapping:
            start_properties = property_mapping[current_state]
            end_properties = property_mapping[target_state]
            
            animations = {}
            for prop in end_properties:
                start_val = getattr(self, prop, start_properties.get(prop, 0))
                end_val = end_properties[prop]
                animations[prop] = (start_val, end_val)
            
            self.animate_multiple_properties(animations)
        
        self.set_state(target_state)
    
    def get_animation_progress(self, property_name: str) -> float:
        """Get current animation progress for a property (0.0 to 1.0)"""
        if property_name in self._current_animations:
            # This would require tracking animation progress in the animation thread
            # Implementation depends on specific needs
            return 0.5  # Placeholder
        return 1.0  # Not animating = complete
    
    def pause_animations(self):
        """Pause all current animations"""
        for thread in self._current_animations.values():
            if hasattr(thread, 'paused'):
                thread.paused = True
    
    def resume_animations(self):
        """Resume all paused animations"""
        for thread in self._current_animations.values():
            if hasattr(thread, 'paused'):
                thread.paused = False

    
    def animate_property(self, property_name: str, start_value: float, 
                        end_value: float, duration: float = None,
                        easing_function: Callable = None):
        """
        Animate a numeric property of the widget
        """
        if not self.config.enable_animations:
            setattr(self, property_name, end_value)
            self.update_appearance()
            return
            
        duration = duration or self.config.animation_duration
        easing_function = easing_function or self._ease_out_cubic
        
        # Stop existing animation if it exists
        if property_name in self._current_animations:
            self._current_animations[property_name].do_run = False
        
        # Create new animation
        animation_thread = threading.Thread(
            target=self._animate_property_thread,
            args=(property_name, start_value, end_value, duration, easing_function)
        )
        animation_thread.do_run = True
        self._current_animations[property_name] = animation_thread
        animation_thread.start()
    
    def _animate_property_thread(self, property_name: str, start_value: float,
                                end_value: float, duration: float, 
                                easing_function: Callable):
        """Animation thread for a property"""
        start_time = time.time()
        
        while getattr(threading.current_thread(), "do_run", True):
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            
            # Apply easing function
            eased_progress = easing_function(progress)
            current_value = start_value + (end_value - start_value) * eased_progress
            
            # Update property
            setattr(self, property_name, current_value)
            self.update_appearance()
            
            if progress >= 1.0:
                break
                
            time.sleep(1/60)  # 60 FPS
    
    def _ease_out_cubic(self, t: float) -> float:
        """Cubic-out easing function"""
        return 1 - (1 - t) ** 3
    
    def set_state(self, new_state: str):
        """Change widget state with animation"""
        if self._widget_state != new_state:
            old_state = self._widget_state
            self._widget_state = new_state
            self._on_state_changed(old_state, new_state)
    
    def _on_state_changed(self, old_state: str, new_state: str):
        """Handle state change"""
        self.trigger_callback('state_changed', old_state, new_state)
        self.update_appearance()
    
    def get_state(self) -> str:
        """Get current widget state"""
        return self._widget_state
    
    def enable(self):
        """Enable the widget"""
        self.set_state("normal")
    
    def disable(self):
        """Disable the widget"""
        self.set_state("disabled")
    
    def stop_all_animations(self):
        """Stop all running animations"""
        for thread in self._current_animations.values():
            if hasattr(thread, 'do_run'):
                thread.do_run = False
        self._current_animations.clear()
    
    def is_animating(self) -> bool:
        """Check if any animations are running"""
        return len(self._current_animations) > 0