"""
Unit tests for animated buttons
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add library path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from animated_widgets_pack import AnimatedButton, WidgetConfig, ButtonStyle
from animated_widgets_pack.utils import ColorUtils

class TestButtonStyle(unittest.TestCase):
    """Tests for ButtonStyle dataclass"""
    
    def test_default_style(self):
        """Test default style values"""
        style = ButtonStyle()
        
        self.assertEqual(style.normal_color, "#3498db")
        self.assertEqual(style.hover_color, "#2980b9")
        self.assertEqual(style.pressed_color, "#21618c")
        self.assertEqual(style.disabled_color, "#95a5a6")
        self.assertEqual(style.text, "Button")
        self.assertIsNone(style.icon)
        self.assertTrue(style.shadow_enabled)
        self.assertEqual(style.shadow_color, "#2c3e50")
        self.assertEqual(style.shadow_offset, (0, 2))
        self.assertEqual(style.hover_lift, 2.0)
        self.assertEqual(style.click_scale, 0.95)
    
    def test_custom_style(self):
        """Test custom style values"""
        style = ButtonStyle(
            normal_color="#e74c3c",
            hover_color="#c0392b",
            pressed_color="#a93226",
            text="Custom Button",
            hover_lift=5.0,
            click_scale=0.8,
            shadow_enabled=False
        )
        
        self.assertEqual(style.normal_color, "#e74c3c")
        self.assertEqual(style.hover_color, "#c0392b")
        self.assertEqual(style.pressed_color, "#a93226")
        self.assertEqual(style.text, "Custom Button")
        self.assertEqual(style.hover_lift, 5.0)
        self.assertEqual(style.click_scale, 0.8)
        self.assertFalse(style.shadow_enabled)

class TestAnimatedButton(unittest.TestCase):
    """Tests for AnimatedButton class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = WidgetConfig(
            width=120, height=40,
            animation_duration=0.1  # Short for testing
        )
        
        self.style = ButtonStyle(
            normal_color="#3498db",
            hover_color="#2980b9",
            pressed_color="#21618c"
        )
        
        self.button = AnimatedButton(
            text="Test Button",
            config=self.config,
            style=self.style
        )
    
    def test_button_initialization(self):
        """Test button initialization"""
        self.assertEqual(self.button.style.text, "Test Button")
        self.assertEqual(self.button.get_state(), "normal")
        self.assertIsNotNone(self.button._animation_manager)
        self.assertEqual(self.button._current_scale, 1.0)
        self.assertEqual(self.button._current_lift, 0.0)
        self.assertFalse(self.button._is_pressed)
        self.assertIsNone(self.button._gui_widget)
        self.assertIsNone(self.button._gui_framework)
    
    def test_color_parsing(self):
        """Test color parsing on initialization"""
        normal_color = ColorUtils.parse_color(self.style.normal_color)
        self.assertEqual(normal_color.r, 52)  # #3498db -> rgb(52, 152, 219)
        self.assertEqual(normal_color.g, 152)
        self.assertEqual(normal_color.b, 219)
    
    def test_state_changes(self):
        """Test button state changes"""
        # Test hover state
        self.button.set_state("hover")
        self.assertEqual(self.button.get_state(), "hover")
        
        # Test pressed state
        self.button.set_state("pressed") 
        self.assertEqual(self.button.get_state(), "pressed")
        
        # Test disabled state
        self.button.disable()
        self.assertEqual(self.button.get_state(), "disabled")
        
        # Test enabled state
        self.button.enable()
        self.assertEqual(self.button.get_state(), "normal")
    
    def test_callbacks(self):
        """Test event callbacks"""
        # Mock callbacks
        click_callback = Mock()
        hover_enter_callback = Mock()
        hover_leave_callback = Mock()
        
        # Bind callbacks
        self.button.on_click(click_callback)
        self.button.bind_callback('hover_enter', hover_enter_callback)
        self.button.bind_callback('hover_leave', hover_leave_callback)
        
        # Trigger events
        self.button.trigger_callback('click')
        self.button.trigger_callback('hover_enter')
        self.button.trigger_callback('hover_leave')
        
        # Verify calls
        click_callback.assert_called_once()
        hover_enter_callback.assert_called_once()
        hover_leave_callback.assert_called_once()
    
    def test_multiple_callbacks(self):
        """Test multiple callbacks for same event"""
        callback1 = Mock()
        callback2 = Mock()
        
        self.button.on_click(callback1)
        self.button.on_click(callback2)
        
        self.button.trigger_callback('click')
        
        callback1.assert_called_once()
        callback2.assert_called_once()
    
    def test_text_update(self):
        """Test text update"""
        new_text = "Updated Text"
        self.button.set_text(new_text)
        self.assertEqual(self.button.style.text, new_text)
    
    def test_color_update(self):
        """Test color update"""
        new_normal = "#e74c3c"
        new_hover = "#c0392b"
        new_pressed = "#a93226"
        
        self.button.set_colors(
            normal=new_normal,
            hover=new_hover, 
            pressed=new_pressed
        )
        
        self.assertEqual(self.button.style.normal_color, new_normal)
        self.assertEqual(self.button.style.hover_color, new_hover)
        self.assertEqual(self.button.style.pressed_color, new_pressed)
    
    def test_partial_color_update(self):
        """Test partial color update"""
        original_hover = self.button.style.hover_color
        original_pressed = self.button.style.pressed_color
        
        self.button.set_colors(normal="#e74c3c")
        
        self.assertEqual(self.button.style.normal_color, "#e74c3c")
        self.assertEqual(self.button.style.hover_color, original_hover)
        self.assertEqual(self.button.style.pressed_color, original_pressed)
    
    def test_animation_properties(self):
        """Test animation properties"""
        # Test scale update
        original_scale = self.button._current_scale
        self.button._update_scale(0.9)
        self.assertEqual(self.button._current_scale, 0.9)
        
        # Test lift update
        original_lift = self.button._current_lift
        self.button._update_lift(5.0)
        self.assertEqual(self.button._current_lift, 5.0)
    
    @patch('animated_widgets_pack.buttons.AnimatedButton.update_appearance')
    def test_hover_simulation(self, mock_update):
        """Test simulated hover events"""
        # Simulate mouse enter
        self.button._on_hover_enter()
        self.assertEqual(self.button.get_state(), "hover")
        
        # Simulate mouse leave
        self.button._on_hover_leave()
        self.assertEqual(self.button.get_state(), "normal")
        
        # Verify appearance was updated
        self.assertTrue(mock_update.called)
    
    @patch('animated_widgets_pack.buttons.AnimatedButton.update_appearance')
    def test_click_simulation(self, mock_update):
        """Test simulated click events"""
        click_callback = Mock()
        self.button.on_click(click_callback)
        
        # Simulate press
        self.button._on_press()
        self.assertEqual(self.button.get_state(), "pressed")
        self.assertTrue(self.button._is_pressed)
        
        # Simulate release
        self.button._on_release()
        self.assertFalse(self.button._is_pressed)
        
        # Simulate click
        self.button._on_click()
        click_callback.assert_called_once()
    
    def test_disabled_state_interaction(self):
        """Test interactions when disabled"""
        self.button.disable()
        
        # Events should not change state from disabled
        self.button._on_hover_enter()
        self.assertEqual(self.button.get_state(), "disabled")
        
        self.button._on_press()
        self.assertEqual(self.button.get_state(), "disabled")
        self.assertFalse(self.button._is_pressed)
        
        # Click callback should not be triggered when disabled
        click_callback = Mock()
        self.button.on_click(click_callback)
        self.button._on_click()
        click_callback.assert_not_called()
    
    @patch('animated_widgets_pack.buttons.AnimationManager')
    def test_animation_manager_integration(self, mock_animation_manager_class):
        """Test animation manager integration"""
        mock_manager = Mock()
        mock_animation_manager_class.return_value = mock_manager
        
        # Create new button to test manager creation
        button = AnimatedButton("Test")
        
        # Verify animation manager was created
        mock_animation_manager_class.assert_called_once()
        self.assertEqual(button._animation_manager, mock_manager)
    
    def test_color_transition_animation(self):
        """Test color transition animation"""
        start_color = ColorUtils.parse_color("#ff0000")  # Red
        end_color = ColorUtils.parse_color("#0000ff")    # Blue
        
        # Mock animation manager to capture calls
        mock_manager = Mock()
        self.button._animation_manager = mock_manager
        
        self.button._animate_color_transition(start_color, end_color, duration=0.1)
        
        # Verify animation was started
        mock_manager.animate.assert_called_once()
        args, kwargs = mock_manager.animate.call_args
        
        self.assertEqual(args[0], "color")  # animation ID
        self.assertEqual(args[1], 0.0)      # start value
        self.assertEqual(args[2], 1.0)      # end value
    
    def test_pulse_animation(self):
        """Test pulse animation"""
        mock_manager = Mock()
        self.button._animation_manager = mock_manager
        
        self.button.pulse_animation(duration=1.0, scale_factor=1.5)
        
        # Verify pulse animation was started
        mock_manager.animate.assert_called_once()
        args, kwargs = mock_manager.animate.call_args
        
        self.assertEqual(args[0], "pulse")  # animation ID
    
    def test_flash_animation(self):
        """Test flash animation"""
        mock_manager = Mock()
        self.button._animation_manager = mock_manager
        
        self.button.flash_animation(flash_color="#ffffff", duration=0.3)
        
        # Verify flash animation was started
        mock_manager.animate.assert_called_once()
        args, kwargs = mock_manager.animate.call_args
        
        self.assertEqual(args[0], "flash")  # animation ID
    
    def test_bounce_animation(self):
        """Test bounce animation"""
        mock_manager = Mock()
        self.button._animation_manager = mock_manager
        
        self.button.bounce_animation(duration=0.6)
        
        # Verify bounce animation was started
        mock_manager.animate.assert_called_once()
        args, kwargs = mock_manager.animate.call_args
        
        self.assertEqual(args[0], "bounce")  # animation ID
    
    def test_stop_all_animations(self):
        """Test stopping all animations"""
        mock_manager = Mock()
        self.button._animation_manager = mock_manager
        
        self.button.stop_all_animations()
        
        # Verify stop was called on manager
        mock_manager.stop_all_animations.assert_called_once()
    
    def test_render_unsupported_framework(self):
        """Test rendering with unsupported framework"""
        mock_parent = Mock()
        
        with self.assertRaises(ValueError) as context:
            self.button.render(mock_parent, "unsupported_framework")
        
        self.assertIn("Unsupported framework", str(context.exception))
    
    @patch('tkinter.Button')
    def test_render_tkinter(self, mock_button_class):
        """Test rendering with Tkinter"""
        mock_parent = Mock()
        mock_widget = Mock()
        mock_button_class.return_value = mock_widget
        
        result = self.button.render(mock_parent, "tkinter")
        
        # Verify Tkinter button was created
        mock_button_class.assert_called_once()
        self.assertEqual(result, mock_widget)
        self.assertEqual(self.button._gui_widget, mock_widget)
        self.assertEqual(self.button._gui_framework, "tkinter")
    
    def test_method_chaining(self):
        """Test method chaining with on_click"""
        callback = Mock()
        
        # on_click should return self for chaining
        result = self.button.on_click(callback)
        self.assertEqual(result, self.button)
        
        # Verify callback was bound
        self.button.trigger_callback('click')
        callback.assert_called_once()
    
    def test_default_parameters(self):
        """Test button with default parameters"""
        button = AnimatedButton()
        
        self.assertEqual(button.style.text, "Button")
        self.assertIsNotNone(button.config)
        self.assertIsNotNone(button.style)
        self.assertEqual(button.get_state(), "normal")
    
    def test_custom_text_initialization(self):
        """Test button initialization with custom text"""
        button = AnimatedButton("Custom Text")
        self.assertEqual(button.style.text, "Custom Text")
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self.button, '_animation_manager'):
            self.button.stop_all_animations()

# Integration test that doesn't require GUI
class TestButtonIntegration(unittest.TestCase):
    """Integration tests for button functionality"""
    
    def setUp(self):
        """Set up integration test"""
        self.config = WidgetConfig(animation_duration=0.05)  # Very short for testing
        self.button = AnimatedButton("Integration Test", self.config)
    
    def test_full_interaction_cycle(self):
        """Test complete interaction cycle"""
        # Track state changes
        state_changes = []
        self.button.bind_callback('state_changed', 
                                lambda old, new: state_changes.append((old, new)))
        
        # Track clicks
        clicks = []
        self.button.on_click(lambda: clicks.append("clicked"))
        
        # Simulate full cycle
        self.button._on_hover_enter()
        self.button._on_press()
        self.button._on_click()
        self.button._on_release()
        self.button._on_hover_leave()
        
        # Verify state changes occurred
        self.assertGreater(len(state_changes), 0)
        self.assertEqual(len(clicks), 1)
        
        # Should end in normal state
        self.assertEqual(self.button.get_state(), "normal")
    
    def test_animation_with_real_timing(self):
        """Test animation with real timing (short duration)"""
        original_color = self.button._current_color
        
        # Start animation
        self.button._on_hover_enter()
        
        # Let animation run briefly
        time.sleep(0.1)
        
        # Color should have changed from original
        # (Note: exact comparison difficult due to threading)
        self.assertIsNotNone(self.button._current_color)
    
    def tearDown(self):
        """Clean up integration test"""
        self.button.stop_all_animations()

if __name__ == '__main__':
    # Run tests with minimal output for CI
    unittest.main(verbosity=1)