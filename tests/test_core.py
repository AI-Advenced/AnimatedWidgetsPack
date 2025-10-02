"""
Unit tests for the core module
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch
import sys
import os

# Add library path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from animated_widgets_pack.core import AnimatedWidget, WidgetConfig

class TestWidget(AnimatedWidget):
    """Test implementation of AnimatedWidget for testing"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.rendered = False
        self.appearance_updates = 0
    
    def render(self, parent_widget):
        """Test render implementation"""
        self.rendered = True
        return "test_widget"
    
    def update_appearance(self):
        """Test appearance update implementation"""
        self.appearance_updates += 1

class TestWidgetConfig(unittest.TestCase):
    """Tests for WidgetConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = WidgetConfig()
        
        self.assertEqual(config.width, 120)
        self.assertEqual(config.height, 40)
        self.assertEqual(config.background_color, "#3498db")
        self.assertEqual(config.text_color, "#ffffff")
        self.assertEqual(config.border_radius, 8)
        self.assertEqual(config.border_width, 0)
        self.assertEqual(config.border_color, "#2c3e50")
        self.assertEqual(config.font_family, "Arial")
        self.assertEqual(config.font_size, 12)
        self.assertEqual(config.animation_duration, 0.3)
        self.assertTrue(config.enable_animations)
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = WidgetConfig(
            width=200,
            height=60,
            background_color="#e74c3c",
            animation_duration=0.5,
            enable_animations=False
        )
        
        self.assertEqual(config.width, 200)
        self.assertEqual(config.height, 60)
        self.assertEqual(config.background_color, "#e74c3c")
        self.assertEqual(config.animation_duration, 0.5)
        self.assertFalse(config.enable_animations)

class TestAnimatedWidget(unittest.TestCase):
    """Tests for AnimatedWidget base class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = WidgetConfig(animation_duration=0.1)  # Short for testing
        self.widget = TestWidget(self.config)
    
    def test_initialization(self):
        """Test widget initialization"""
        self.assertIsNotNone(self.widget.config)
        self.assertEqual(self.widget.get_state(), "normal")
        self.assertIsInstance(self.widget._callbacks, dict)
        self.assertIsInstance(self.widget._current_animations, dict)
        self.assertFalse(self.widget._is_animating)
    
    def test_default_config_initialization(self):
        """Test initialization with default config"""
        widget = TestWidget()
        self.assertIsNotNone(widget.config)
        self.assertEqual(widget.config.width, 120)
    
    def test_callback_binding(self):
        """Test callback binding and triggering"""
        callback = Mock()
        self.widget.bind_callback('click', callback)
        
        self.widget.trigger_callback('click')
        callback.assert_called_once()
    
    def test_multiple_callbacks(self):
        """Test multiple callbacks for same event"""
        callback1 = Mock()
        callback2 = Mock()
        
        self.widget.bind_callback('click', callback1)
        self.widget.bind_callback('click', callback2)
        
        self.widget.trigger_callback('click')
        
        callback1.assert_called_once()
        callback2.assert_called_once()
    
    def test_callback_with_arguments(self):
        """Test callbacks with arguments"""
        callback = Mock()
        self.widget.bind_callback('value_changed', callback)
        
        self.widget.trigger_callback('value_changed', 42, "test")
        callback.assert_called_once_with(42, "test")
    
    def test_invalid_event_type(self):
        """Test binding to invalid event type"""
        callback = Mock()
        self.widget.bind_callback('invalid_event', callback)
        
        # Should not raise error, just not call callback
        self.widget.trigger_callback('invalid_event')
        callback.assert_not_called()
    
    def test_state_management(self):
        """Test widget state management"""
        self.assertEqual(self.widget.get_state(), "normal")
        
        self.widget.set_state("hover")
        self.assertEqual(self.widget.get_state(), "hover")
        
        self.widget.set_state("pressed")
        self.assertEqual(self.widget.get_state(), "pressed")
        
        self.widget.disable()
        self.assertEqual(self.widget.get_state(), "disabled")
        
        self.widget.enable()
        self.assertEqual(self.widget.get_state(), "normal")
    
    def test_state_change_callback(self):
        """Test state change callback triggering"""
        callback = Mock()
        self.widget.bind_callback('state_changed', callback)
        
        self.widget.set_state("hover")
        callback.assert_called_once_with("normal", "hover")
        
        callback.reset_mock()
        self.widget.set_state("pressed")
        callback.assert_called_once_with("hover", "pressed")
    
    def test_no_state_change_callback(self):
        """Test no callback when state doesn't change"""
        callback = Mock()
        self.widget.bind_callback('state_changed', callback)
        
        self.widget.set_state("normal")  # Already normal
        callback.assert_not_called()
    
    def test_animate_property_disabled(self):
        """Test animation when disabled in config"""
        self.widget.config.enable_animations = False
        self.widget.test_property = 0
        
        self.widget.animate_property("test_property", 0, 100)
        
        # Should set immediately
        self.assertEqual(self.widget.test_property, 100)
        self.assertEqual(self.widget.appearance_updates, 1)
    
    def test_animate_property_enabled(self):
        """Test animation when enabled"""
        self.widget.test_property = 0
        
        self.widget.animate_property("test_property", 0, 100, duration=0.1)
        
        # Should start animation
        time.sleep(0.05)  # Wait a bit
        
        # Property should be between start and end
        self.assertGreater(self.widget.test_property, 0)
        self.assertLess(self.widget.test_property, 100)
        
        # Wait for animation to complete
        time.sleep(0.15)
        
        # Should reach end value
        self.assertAlmostEqual(self.widget.test_property, 100, delta=1)
    
    def test_stop_animation(self):
        """Test stopping animations"""
        self.widget.test_property = 0
        
        self.widget.animate_property("test_property", 0, 100, duration=0.2)
        time.sleep(0.05)  # Let animation start
        
        # Stop animation
        self.widget.stop_all_animations()
        
        current_value = self.widget.test_property
        time.sleep(0.1)  # Wait more
        
        # Value should not have changed much after stopping
        self.assertAlmostEqual(self.widget.test_property, current_value, delta=5)
    
    def test_easing_function(self):
        """Test easing function"""
        # Test cubic easing
        result = self.widget._ease_out_cubic(0.5)
        self.assertGreater(result, 0.5)  # Should be accelerated
        
        # Test boundaries
        self.assertEqual(self.widget._ease_out_cubic(0), 0)
        self.assertEqual(self.widget._ease_out_cubic(1), 1)
    
    def test_is_animating(self):
        """Test animation state checking"""
        self.assertFalse(self.widget.is_animating())
        
        self.widget.test_property = 0
        self.widget.animate_property("test_property", 0, 100, duration=0.1)
        
        # Should be animating briefly
        self.assertTrue(self.widget.is_animating())
        
        # Wait for completion
        time.sleep(0.15)
        self.assertFalse(self.widget.is_animating())
    
    def test_concurrent_animations(self):
        """Test multiple concurrent animations"""
        self.widget.prop1 = 0
        self.widget.prop2 = 0
        
        self.widget.animate_property("prop1", 0, 100, duration=0.1)
        self.widget.animate_property("prop2", 0, 200, duration=0.1)
        
        time.sleep(0.15)  # Wait for completion
        
        self.assertAlmostEqual(self.widget.prop1, 100, delta=1)
        self.assertAlmostEqual(self.widget.prop2, 200, delta=1)
    
    def test_animation_override(self):
        """Test animation override when new animation starts"""
        self.widget.test_property = 0
        
        # Start first animation
        self.widget.animate_property("test_property", 0, 100, duration=0.2)
        time.sleep(0.05)
        
        intermediate_value = self.widget.test_property
        
        # Start second animation (should override first)
        self.widget.animate_property("test_property", intermediate_value, 200, duration=0.1)
        time.sleep(0.15)
        
        # Should reach second animation's target
        self.assertAlmostEqual(self.widget.test_property, 200, delta=5)
    
    def test_callback_exception_handling(self):
        """Test that callback exceptions don't crash the widget"""
        def bad_callback():
            raise Exception("Test exception")
        
        self.widget.bind_callback('click', bad_callback)
        
        # Should not raise exception
        self.widget.trigger_callback('click')
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self.widget, '_current_animations'):
            self.widget.stop_all_animations()

if __name__ == '__main__':
    unittest.main()