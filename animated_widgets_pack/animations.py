"""
Module animations - Animation manager and visual effects
"""

import math
import time
import threading
from enum import Enum
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass

class EasingType(Enum):
    """Available easing function types"""
    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    BOUNCE_OUT = "bounce_out"
    ELASTIC_OUT = "elastic_out"
    EASE_IN_BACK = "ease_in_back"
    EASE_OUT_BACK = "ease_out_back"
    EASE_IN_OUT_BACK = "ease_in_out_back"
    EASE_IN_CIRC = "ease_in_circ"
    EASE_OUT_CIRC = "ease_out_circ"
    EASE_IN_OUT_CIRC = "ease_in_out_circ"
    
@dataclass
class AnimationConfig:
    """Animation configuration"""
    duration: float = 0.3
    easing: EasingType = EasingType.EASE_OUT_CUBIC
    fps: int = 60
    auto_reverse: bool = False
    repeat_count: int = 1
    delay: float = 0.0

class EasingFunctions:
    """Collection of mathematical easing functions"""
    
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in_back(t: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return c3 * t * t * t - c1 * t * t
    
    @staticmethod
    def ease_out_back(t: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    @staticmethod
    def ease_in_out_back(t: float) -> float:
        c1 = 1.70158
        c2 = c1 * 1.525
        
        if t < 0.5:
            return (pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
        else:
            return (pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
    
    @staticmethod
    def ease_in_circ(t: float) -> float:
        return 1 - math.sqrt(1 - pow(t, 2))
    
    @staticmethod
    def ease_out_circ(t: float) -> float:
        return math.sqrt(1 - pow(t - 1, 2))
    
    @staticmethod
    def ease_in_out_circ(t: float) -> float:
        if t < 0.5:
            return (1 - math.sqrt(1 - pow(2 * t, 2))) / 2
        else:
            return (math.sqrt(1 - pow(-2 * t + 2, 2)) + 1) / 2

    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def bounce_out(t: float) -> float:
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375
    
    @staticmethod
    def elastic_out(t: float) -> float:
        if t == 0 or t == 1:
            return t
        return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1
    
    @staticmethod
    def ease_in_back(t: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return c3 * t * t * t - c1 * t * t
    
    @staticmethod
    def ease_out_back(t: float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
    
    @staticmethod
    def ease_in_out_back(t: float) -> float:
        c1 = 1.70158
        c2 = c1 * 1.525
        return (2 * t * t * ((c2 + 1) * 2 * t - c2)) / 2 if t < 0.5 else (pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2

class AnimationManager:
    """Central animation manager"""
    
    def __init__(self):
        self._active_animations: Dict[str, threading.Thread] = {}
        self._easing_functions = {
            EasingType.LINEAR: EasingFunctions.linear,
            EasingType.EASE_IN_QUAD: EasingFunctions.ease_in_quad,
            EasingType.EASE_OUT_QUAD: EasingFunctions.ease_out_quad,
            EasingType.EASE_IN_OUT_QUAD: EasingFunctions.ease_in_out_quad,
            EasingType.EASE_IN_CUBIC: EasingFunctions.ease_in_cubic,
            EasingType.EASE_OUT_CUBIC: EasingFunctions.ease_out_cubic,
            EasingType.EASE_IN_OUT_CUBIC: EasingFunctions.ease_in_out_cubic,
            EasingType.BOUNCE_OUT: EasingFunctions.bounce_out,
            EasingType.ELASTIC_OUT: EasingFunctions.elastic_out,
            EasingType.EASE_IN_BACK: EasingFunctions.ease_in_back,
            EasingType.EASE_OUT_BACK: EasingFunctions.ease_out_back,
            EasingType.EASE_IN_OUT_BACK: EasingFunctions.ease_in_out_back,
            EasingType.EASE_IN_CIRC: EasingFunctions.ease_in_circ,
            EasingType.EASE_OUT_CIRC: EasingFunctions.ease_out_circ,
            EasingType.EASE_IN_OUT_CIRC: EasingFunctions.ease_in_out_circ,
        }
    
    def animate(self, animation_id: str, start_value: float, end_value: float,
                update_callback: Callable, config: AnimationConfig = None,
                completion_callback: Callable = None):
        """
        Create and start a new animation
        """
        config = config or AnimationConfig()
        
        # Stop existing animation
        self.stop_animation(animation_id)
        
        # Create animation thread
        animation_thread = threading.Thread(
            target=self._animation_loop,
            args=(animation_id, start_value, end_value, update_callback,
                  config, completion_callback)
        )
        animation_thread.daemon = True
        animation_thread.do_run = True
        
        self._active_animations[animation_id] = animation_thread
        animation_thread.start()
    
    def _animation_loop(self, animation_id: str, start_value: float,
                       end_value: float, update_callback: Callable,
                       config: AnimationConfig, completion_callback: Callable):
        """Main animation loop"""
        
        # Initial delay
        if config.delay > 0:
            time.sleep(config.delay)
        
        easing_func = self._easing_functions.get(config.easing, EasingFunctions.ease_out_cubic)
        frame_duration = 1.0 / config.fps
        
        for repeat in range(config.repeat_count):
            start_time = time.time()
            
            while getattr(threading.current_thread(), "do_run", True):
                elapsed = time.time() - start_time
                progress = min(elapsed / config.duration, 1.0)
                
                # Apply easing
                eased_progress = easing_func(progress)
                
                # Auto-reverse for ping-pong animations
                if config.auto_reverse and repeat % 2 == 1:
                    eased_progress = 1.0 - eased_progress
                
                # Calculate current value
                current_value = start_value + (end_value - start_value) * eased_progress
                
                # Update via callback
                try:
                    update_callback(current_value)
                except Exception as e:
                    print(f"Error in update_callback: {e}")
                    break
                
                # Check if animation is complete
                if progress >= 1.0:
                    break
                
                time.sleep(frame_duration)
        
        # Clean up and call completion callback
        if animation_id in self._active_animations:
            del self._active_animations[animation_id]
        
        if completion_callback:
            try:
                completion_callback()
            except Exception as e:
                print(f"Error in completion_callback: {e}")
    
    def stop_animation(self, animation_id: str):
        """Stop a specific animation"""
        if animation_id in self._active_animations:
            self._active_animations[animation_id].do_run = False
            del self._active_animations[animation_id]
    
    def stop_all_animations(self):
        """Stop all active animations"""
        for thread in self._active_animations.values():
            thread.do_run = False
        self._active_animations.clear()
    
    def is_animating(self, animation_id: str) -> bool:
        """Check if an animation is running"""
        return animation_id in self._active_animations
    
    def get_active_count(self) -> int:
        """Get number of active animations"""
        return len(self._active_animations)

# Ajouter ces nouvelles fonctions d'easing à la classe EasingFunctions






# Ajouter ces nouvelles fonctions utilitaires à la fin du fichier

def create_text_input_animation(duration: float = 0.25) -> AnimationConfig:
    """Create a text input focus animation configuration"""
    return AnimationConfig(
        duration=duration,
        easing=EasingType.EASE_OUT_CUBIC
    )

def create_checkbox_animation(animation_type: str = "scale", duration: float = 0.3) -> AnimationConfig:
    """Create a checkbox state change animation configuration"""
    if animation_type == "bounce":
        return AnimationConfig(
            duration=duration,
            easing=EasingType.BOUNCE_OUT
        )
    elif animation_type == "elastic":
        return AnimationConfig(
            duration=duration,
            easing=EasingType.ELASTIC_OUT
        )
    else:  # scale or default
        return AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_OUT_CUBIC
        )

def create_switch_animation(animation_type: str = "slide", duration: float = 0.3) -> AnimationConfig:
    """Create a switch toggle animation configuration"""
    if animation_type == "bounce":
        return AnimationConfig(
            duration=duration,
            easing=EasingType.BOUNCE_OUT
        )
    elif animation_type == "elastic":
        return AnimationConfig(
            duration=duration,
            easing=EasingType.ELASTIC_OUT
        )
    else:  # slide or default
        return AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_OUT_CUBIC
        )

def create_validation_error_animation(duration: float = 0.5) -> AnimationConfig:
    """Create a validation error shake animation configuration"""
    return AnimationConfig(
        duration=duration,
        easing=EasingType.EASE_OUT_CUBIC
    )

# Utility functions for common animation patterns

def create_fade_animation(start_opacity: float, end_opacity: float,
                         duration: float = 0.3) -> AnimationConfig:
    """Create a fade animation configuration"""
    return AnimationConfig(
        duration=duration,
        easing=EasingType.EASE_OUT_QUAD
    )

def create_scale_animation(duration: float = 0.2, 
                          easing: EasingType = EasingType.BOUNCE_OUT) -> AnimationConfig:
    """Create a scale animation configuration"""
    return AnimationConfig(
        duration=duration,
        easing=easing
    )

def create_slide_animation(duration: float = 0.4,
                          easing: EasingType = EasingType.EASE_OUT_CUBIC) -> AnimationConfig:
    """Create a slide animation configuration"""
    return AnimationConfig(
        duration=duration,
        easing=easing
    )

def create_bounce_animation(duration: float = 0.6) -> AnimationConfig:
    """Create a bounce animation configuration"""
    return AnimationConfig(
        duration=duration,
        easing=EasingType.BOUNCE_OUT
    )

def create_elastic_animation(duration: float = 0.8) -> AnimationConfig:
    """Create an elastic animation configuration"""
    return AnimationConfig(
        duration=duration,
        easing=EasingType.ELASTIC_OUT
    )

def create_slider_animation(duration: float = 0.3, 
                          easing: EasingType = EasingType.EASE_OUT_BACK) -> AnimationConfig:
    """Create a slider-specific animation configuration"""
    return AnimationConfig(
        duration=duration,
        easing=easing,
        fps=60
    )