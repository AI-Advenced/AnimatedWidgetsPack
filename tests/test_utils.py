"""
Unit tests for the utils module
"""

import unittest
import math
import sys
import os

# Add library path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from animated_widgets_pack.utils import (
    Color, ColorUtils, Point, Rectangle, GeometryUtils, ColorPalettes
)

class TestColor(unittest.TestCase):
    """Tests for Color dataclass"""
    
    def test_color_initialization(self):
        """Test color initialization"""
        # Default alpha
        color = Color(255, 128, 64)
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 128)
        self.assertEqual(color.b, 64)
        self.assertEqual(color.a, 1.0)
        
        # Custom alpha
        color_alpha = Color(255, 128, 64, 0.5)
        self.assertEqual(color_alpha.a, 0.5)
    
    def test_color_to_hex(self):
        """Test color to hex conversion"""
        color = Color(255, 128, 64)
        self.assertEqual(color.to_hex(), "#ff8040")
        
        # Test with zero values
        black = Color(0, 0, 0)
        self.assertEqual(black.to_hex(), "#000000")
        
        # Test with max values
        white = Color(255, 255, 255)
        self.assertEqual(white.to_hex(), "#ffffff")
    
    def test_color_to_rgba_string(self):
        """Test color to RGBA string conversion"""
        color = Color(255, 128, 64, 0.8)
        self.assertEqual(color.to_rgba_string(), "rgba(255, 128, 64, 0.8)")
        
        # Test with default alpha
        color_default = Color(255, 128, 64)
        self.assertEqual(color_default.to_rgba_string(), "rgba(255, 128, 64, 1.0)")
    
    def test_color_tuples(self):
        """Test color tuple conversions"""
        color = Color(255, 128, 64, 0.8)
        
        self.assertEqual(color.to_rgb_tuple(), (255, 128, 64))
        self.assertEqual(color.to_rgba_tuple(), (255, 128, 64, 0.8))

class TestColorUtils(unittest.TestCase):
    """Tests for ColorUtils class"""
    
    def test_hex_to_rgb(self):
        """Test hex to RGB conversion"""
        # Standard hex
        self.assertEqual(ColorUtils.hex_to_rgb("#ff8040"), (255, 128, 64))
        self.assertEqual(ColorUtils.hex_to_rgb("ff8040"), (255, 128, 64))
        
        # Short hex
        self.assertEqual(ColorUtils.hex_to_rgb("#f80"), (255, 136, 0))
        self.assertEqual(ColorUtils.hex_to_rgb("f80"), (255, 136, 0))
        
        # Black and white
        self.assertEqual(ColorUtils.hex_to_rgb("#000000"), (0, 0, 0))
        self.assertEqual(ColorUtils.hex_to_rgb("#ffffff"), (255, 255, 255))
    
    def test_rgb_to_hex(self):
        """Test RGB to hex conversion"""
        self.assertEqual(ColorUtils.rgb_to_hex(255, 128, 64), "#ff8040")
        self.assertEqual(ColorUtils.rgb_to_hex(0, 0, 0), "#000000")
        self.assertEqual(ColorUtils.rgb_to_hex(255, 255, 255), "#ffffff")
    
    def test_parse_color_hex(self):
        """Test parsing hex colors"""
        color = ColorUtils.parse_color("#ff8040")
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 128)
        self.assertEqual(color.b, 64)
        self.assertEqual(color.a, 1.0)
    
    def test_parse_color_rgb_string(self):
        """Test parsing RGB string colors"""
        # RGB format
        color = ColorUtils.parse_color("rgb(255, 128, 64)")
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 128)
        self.assertEqual(color.b, 64)
        self.assertEqual(color.a, 1.0)
        
        # RGBA format
        color_rgba = ColorUtils.parse_color("rgba(255, 128, 64, 0.5)")
        self.assertEqual(color_rgba.r, 255)
        self.assertEqual(color_rgba.g, 128)
        self.assertEqual(color_rgba.b, 64)
        self.assertEqual(color_rgba.a, 0.5)
    
    def test_parse_color_named(self):
        """Test parsing named colors"""
        red = ColorUtils.parse_color("red")
        self.assertEqual(red.to_hex(), "#ff0000")
        
        blue = ColorUtils.parse_color("blue")
        self.assertEqual(blue.to_hex(), "#0000ff")
        
        # Case insensitive
        green = ColorUtils.parse_color("GREEN")
        self.assertEqual(green.to_hex(), "#008000")
    
    def test_parse_color_tuple(self):
        """Test parsing tuple colors"""
        # RGB tuple
        color = ColorUtils.parse_color((255, 128, 64))
        self.assertEqual(color.r, 255)
        self.assertEqual(color.g, 128)
        self.assertEqual(color.b, 64)
        self.assertEqual(color.a, 1.0)
        
        # RGBA tuple
        color_rgba = ColorUtils.parse_color((255, 128, 64, 0.5))
        self.assertEqual(color_rgba.a, 0.5)
    
    def test_parse_color_object(self):
        """Test parsing Color object"""
        original = Color(255, 128, 64, 0.8)
        parsed = ColorUtils.parse_color(original)
        
        self.assertEqual(parsed.r, original.r)
        self.assertEqual(parsed.g, original.g)
        self.assertEqual(parsed.b, original.b)
        self.assertEqual(parsed.a, original.a)
        self.assertIs(parsed, original)  # Should return same object
    
    def test_parse_color_invalid(self):
        """Test parsing invalid colors returns default"""
        default = ColorUtils.parse_color("invalid_color")
        self.assertEqual(default.r, 52)  # Default blue
        self.assertEqual(default.g, 152)
        self.assertEqual(default.b, 219)
    
    def test_lighten_color(self):
        """Test color lightening"""
        dark_blue = Color(52, 152, 219)
        light_blue = ColorUtils.lighten_color(dark_blue, 0.2)
        
        self.assertGreater(light_blue.r, dark_blue.r)
        self.assertGreater(light_blue.g, dark_blue.g)
        self.assertGreater(light_blue.b, dark_blue.b)
        
        # Test with hex string
        light_from_hex = ColorUtils.lighten_color("#3498db", 0.2)
        self.assertIsInstance(light_from_hex, Color)
    
    def test_darken_color(self):
        """Test color darkening"""
        light_blue = Color(52, 152, 219)
        dark_blue = ColorUtils.darken_color(light_blue, 0.2)
        
        self.assertLess(dark_blue.r, light_blue.r)
        self.assertLess(dark_blue.g, light_blue.g)
        self.assertLess(dark_blue.b, light_blue.b)
    
    def test_interpolate_colors(self):
        """Test color interpolation"""
        red = Color(255, 0, 0)
        blue = Color(0, 0, 255)
        
        # Midpoint should be purple
        midpoint = ColorUtils.interpolate_colors(red, blue, 0.5)
        self.assertEqual(midpoint.r, 127)  # (255 + 0) / 2
        self.assertEqual(midpoint.g, 0)
        self.assertEqual(midpoint.b, 127)  # (0 + 255) / 2
        
        # Start point
        start = ColorUtils.interpolate_colors(red, blue, 0.0)
        self.assertEqual(start.r, red.r)
        self.assertEqual(start.g, red.g)
        self.assertEqual(start.b, red.b)
        
        # End point
        end = ColorUtils.interpolate_colors(red, blue, 1.0)
        self.assertEqual(end.r, blue.r)
        self.assertEqual(end.g, blue.g)
        self.assertEqual(end.b, blue.b)
    
    def test_get_contrast_color(self):
        """Test contrast color calculation"""
        # Light color should return black
        white = Color(255, 255, 255)
        contrast_white = ColorUtils.get_contrast_color(white)
        self.assertEqual(contrast_white.to_hex(), "#000000")
        
        # Dark color should return white
        black = Color(0, 0, 0)
        contrast_black = ColorUtils.get_contrast_color(black)
        self.assertEqual(contrast_black.to_hex(), "#ffffff")
        
        # Test with hex string
        contrast_from_hex = ColorUtils.get_contrast_color("#ffffff")
        self.assertEqual(contrast_from_hex.to_hex(), "#000000")

class TestPoint(unittest.TestCase):
    """Tests for Point dataclass"""
    
    def test_point_initialization(self):
        """Test point initialization"""
        point = Point(10.5, 20.3)
        self.assertEqual(point.x, 10.5)
        self.assertEqual(point.y, 20.3)
    
    def test_distance_to(self):
        """Test distance calculation"""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        
        # Should be 5 (3-4-5 triangle)
        distance = p1.distance_to(p2)
        self.assertEqual(distance, 5.0)
        
        # Distance to self should be 0
        self.assertEqual(p1.distance_to(p1), 0.0)
    
    def test_translate(self):
        """Test point translation"""
        point = Point(10, 20)
        translated = point.translate(5, -3)
        
        self.assertEqual(translated.x, 15)
        self.assertEqual(translated.y, 17)
        
        # Original should be unchanged
        self.assertEqual(point.x, 10)
        self.assertEqual(point.y, 20)

class TestRectangle(unittest.TestCase):
    """Tests for Rectangle dataclass"""
    
    def test_rectangle_initialization(self):
        """Test rectangle initialization"""
        rect = Rectangle(10, 20, 100, 50)
        self.assertEqual(rect.x, 10)
        self.assertEqual(rect.y, 20)
        self.assertEqual(rect.width, 100)
        self.assertEqual(rect.height, 50)
    
    def test_contains_point(self):
        """Test point containment"""
        rect = Rectangle(10, 20, 100, 50)
        
        # Point inside
        self.assertTrue(rect.contains_point(Point(50, 40)))
        
        # Point on border
        self.assertTrue(rect.contains_point(Point(10, 20)))
        self.assertTrue(rect.contains_point(Point(110, 70)))
        
        # Point outside
        self.assertFalse(rect.contains_point(Point(5, 15)))
        self.assertFalse(rect.contains_point(Point(120, 80)))
    
    def test_center(self):
        """Test center calculation"""
        rect = Rectangle(10, 20, 100, 50)
        center = rect.center()
        
        self.assertEqual(center.x, 60)  # 10 + 100/2
        self.assertEqual(center.y, 45)  # 20 + 50/2
    
    def test_area(self):
        """Test area calculation"""
        rect = Rectangle(10, 20, 100, 50)
        self.assertEqual(rect.area(), 5000)  # 100 * 50
    
    def test_intersects(self):
        """Test rectangle intersection"""
        rect1 = Rectangle(10, 10, 50, 50)  # 10,10 to 60,60
        rect2 = Rectangle(30, 30, 50, 50)  # 30,30 to 80,80
        rect3 = Rectangle(70, 70, 50, 50)  # 70,70 to 120,120
        
        # Should intersect
        self.assertTrue(rect1.intersects(rect2))
        self.assertTrue(rect2.intersects(rect1))
        
        # Should not intersect
        self.assertFalse(rect1.intersects(rect3))
        self.assertFalse(rect3.intersects(rect1))

class TestGeometryUtils(unittest.TestCase):
    """Tests for GeometryUtils class"""
    
    def test_distance(self):
        """Test distance calculation"""
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        
        distance = GeometryUtils.distance(p1, p2)
        self.assertEqual(distance, 5.0)
    
    def test_clamp(self):
        """Test value clamping"""
        self.assertEqual(GeometryUtils.clamp(5, 0, 10), 5)
        self.assertEqual(GeometryUtils.clamp(-5, 0, 10), 0)
        self.assertEqual(GeometryUtils.clamp(15, 0, 10), 10)
    
    def test_lerp(self):
        """Test linear interpolation"""
        self.assertEqual(GeometryUtils.lerp(0, 10, 0.5), 5)
        self.assertEqual(GeometryUtils.lerp(0, 10, 0), 0)
        self.assertEqual(GeometryUtils.lerp(0, 10, 1), 10)
    
    def test_map_range(self):
        """Test range mapping"""
        # Map 5 from range [0,10] to range [0,100]
        result = GeometryUtils.map_range(5, 0, 10, 0, 100)
        self.assertEqual(result, 50)
        
        # Map 2 from range [0,4] to range [10,20]
        result = GeometryUtils.map_range(2, 0, 4, 10, 20)
        self.assertEqual(result, 15)
    
    def test_round_rectangle_path_zero_radius(self):
        """Test rounded rectangle with zero radius"""
        rect = Rectangle(10, 20, 100, 50)
        points = GeometryUtils.round_rectangle_path(rect, 0)
        
        # Should have 4 corners
        self.assertEqual(len(points), 4)
        
        # Check corners
        self.assertEqual(points[0].x, 10)
        self.assertEqual(points[0].y, 20)
    
    def test_round_rectangle_path_with_radius(self):
        """Test rounded rectangle with radius"""
        rect = Rectangle(10, 20, 100, 50)
        points = GeometryUtils.round_rectangle_path(rect, 10)
        
        # Should have multiple points for rounded corners
        self.assertGreater(len(points), 4)
    
    def test_calculate_bezier_point(self):
        """Test Bezier curve calculation"""
        p0 = Point(0, 0)
        p1 = Point(0, 10)
        p2 = Point(10, 10)
        p3 = Point(10, 0)
        
        # At t=0, should be at p0
        start = GeometryUtils.calculate_bezier_point(0, p0, p1, p2, p3)
        self.assertEqual(start.x, p0.x)
        self.assertEqual(start.y, p0.y)
        
        # At t=1, should be at p3
        end = GeometryUtils.calculate_bezier_point(1, p0, p1, p2, p3)
        self.assertEqual(end.x, p3.x)
        self.assertEqual(end.y, p3.y)
    
    def test_normalize_angle(self):
        """Test angle normalization"""
        # Normal angle
        self.assertEqual(GeometryUtils.normalize_angle(math.pi), math.pi)
        
        # Negative angle
        normalized = GeometryUtils.normalize_angle(-math.pi)
        self.assertAlmostEqual(normalized, math.pi, places=10)
        
        # Angle > 2π
        normalized = GeometryUtils.normalize_angle(3 * math.pi)
        self.assertAlmostEqual(normalized, math.pi, places=10)
    
    def test_degrees_radians_conversion(self):
        """Test angle conversion"""
        # 180 degrees = π radians
        radians = GeometryUtils.degrees_to_radians(180)
        self.assertAlmostEqual(radians, math.pi, places=10)
        
        # π radians = 180 degrees
        degrees = GeometryUtils.radians_to_degrees(math.pi)
        self.assertAlmostEqual(degrees, 180, places=10)

class TestColorPalettes(unittest.TestCase):
    """Tests for ColorPalettes class"""
    
    def test_palette_contents(self):
        """Test that palettes contain expected colors"""
        # Material Design palette
        self.assertIn('blue', ColorPalettes.MATERIAL_DESIGN)
        self.assertEqual(ColorPalettes.MATERIAL_DESIGN['blue'], '#2196F3')
        
        # Flat UI palette
        self.assertIn('turquoise', ColorPalettes.FLAT_UI)
        self.assertEqual(ColorPalettes.FLAT_UI['turquoise'], '#1ABC9C')
        
        # Bootstrap palette
        self.assertIn('primary', ColorPalettes.BOOTSTRAP)
        self.assertEqual(ColorPalettes.BOOTSTRAP['primary'], '#007bff')

if __name__ == '__main__':
    unittest.main()