"""
Module utils - Shared utilities for the library
"""

import re
import math
from typing import Tuple, List, Optional, Union
from dataclasses import dataclass
from typing import Callable
import time


@dataclass
class Color:
    """RGBA color representation"""
    r: int
    g: int  
    b: int
    a: float = 1.0
    
    def to_hex(self) -> str:
        """Convert to hexadecimal format"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"
    
    def to_rgba_string(self) -> str:
        """Convert to rgba() string"""
        return f"rgba({self.r}, {self.g}, {self.b}, {self.a})"
    
    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple"""
        return (self.r, self.g, self.b)
    
    def to_rgba_tuple(self) -> Tuple[int, int, int, float]:
        """Convert to RGBA tuple"""
        return (self.r, self.g, self.b, self.a)

class ColorUtils:
    """Utilities for color manipulation"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB to hex"""
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def parse_color(color_input: Union[str, Tuple, Color]) -> Color:
        """Parse different color formats"""
        if isinstance(color_input, Color):
            return color_input
        elif isinstance(color_input, str):
            if color_input.startswith('#'):
                r, g, b = ColorUtils.hex_to_rgb(color_input)
                return Color(r, g, b)
            elif color_input.startswith('rgb'):
                # Parse rgba(r, g, b, a) or rgb(r, g, b)
                numbers = re.findall(r'\d+\.?\d*', color_input)
                r, g, b = int(numbers[0]), int(numbers[1]), int(numbers[2])
                a = float(numbers[3]) if len(numbers) > 3 else 1.0
                return Color(r, g, b, a)
            else:
                # Handle named colors (basic set)
                named_colors = {
                    'red': '#ff0000', 'green': '#008000', 'blue': '#0000ff',
                    'white': '#ffffff', 'black': '#000000', 'gray': '#808080',
                    'yellow': '#ffff00', 'cyan': '#00ffff', 'magenta': '#ff00ff'
                }
                if color_input.lower() in named_colors:
                    return ColorUtils.parse_color(named_colors[color_input.lower()])
        elif isinstance(color_input, (tuple, list)):
            if len(color_input) >= 3:
                r, g, b = color_input[:3]
                a = color_input[3] if len(color_input) > 3 else 1.0
                return Color(int(r), int(g), int(b), float(a))
        
        # Default color
        return Color(52, 152, 219)  # Default blue
    
    @staticmethod
    def lighten_color(color: Union[str, Color], factor: float = 0.2) -> Color:
        """Lighten a color"""
        if isinstance(color, str):
            color = ColorUtils.parse_color(color)
        
        r = min(255, int(color.r + (255 - color.r) * factor))
        g = min(255, int(color.g + (255 - color.g) * factor))
        b = min(255, int(color.b + (255 - color.b) * factor))
        
        return Color(r, g, b, color.a)
    
    @staticmethod
    def darken_color(color: Union[str, Color], factor: float = 0.2) -> Color:
        """Darken a color"""
        if isinstance(color, str):
            color = ColorUtils.parse_color(color)
        
        r = max(0, int(color.r * (1 - factor)))
        g = max(0, int(color.g * (1 - factor)))
        b = max(0, int(color.b * (1 - factor)))
        
        return Color(r, g, b, color.a)
    
    @staticmethod
    def interpolate_colors(color1: Color, color2: Color, factor: float) -> Color:
        """Interpolate between two colors"""
        r = int(color1.r + (color2.r - color1.r) * factor)
        g = int(color1.g + (color2.g - color1.g) * factor)
        b = int(color1.b + (color2.b - color1.b) * factor)
        a = color1.a + (color2.a - color1.a) * factor
        
        return Color(r, g, b, a)
    
    @staticmethod
    def get_contrast_color(color: Union[str, Color]) -> Color:
        """Get a contrasting color (black or white)"""
        if isinstance(color, str):
            color = ColorUtils.parse_color(color)
        
        # Calculate luminance
        luminance = (0.299 * color.r + 0.587 * color.g + 0.114 * color.b) / 255
        
        # Return black or white based on luminance
        return Color(0, 0, 0) if luminance > 0.5 else Color(255, 255, 255)

@dataclass
class Point:
    """2D Point"""
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """Calculate distance to another point"""
        return math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)
    
    def translate(self, dx: float, dy: float) -> 'Point':
        """Create a new point translated by dx, dy"""
        return Point(self.x + dx, self.y + dy)

@dataclass  
class Rectangle:
    """Rectangle with position and dimensions"""
    x: float
    y: float
    width: float
    height: float
    
    def contains_point(self, point: Point) -> bool:
        """Check if a point is inside the rectangle"""
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)
    
    def center(self) -> Point:
        """Get the center point of the rectangle"""
        return Point(self.x + self.width / 2, self.y + self.height / 2)
    
    def area(self) -> float:
        """Calculate the area of the rectangle"""
        return self.width * self.height
    
    def intersects(self, other: 'Rectangle') -> bool:
        """Check if this rectangle intersects with another"""
        return not (other.x > self.x + self.width or
                   other.x + other.width < self.x or
                   other.y > self.y + self.height or
                   other.y + other.height < self.y)

class GeometryUtils:
    """Utilities for geometric calculations"""
    
    @staticmethod
    def distance(p1: Point, p2: Point) -> float:
        """Calculate distance between two points"""
        return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
    
    @staticmethod
    def clamp(value: float, min_value: float, max_value: float) -> float:
        """Clamp a value between min and max"""
        return max(min_value, min(value, max_value))
    
    @staticmethod
    def lerp(start: float, end: float, factor: float) -> float:
        """Linear interpolation"""
        return start + (end - start) * factor
    
    @staticmethod
    def map_range(value: float, from_min: float, from_max: float,
                  to_min: float, to_max: float) -> float:
        """Map a value from one range to another"""
        return to_min + (value - from_min) * (to_max - to_min) / (from_max - from_min)
    
    # Ajouter dans GeometryUtils
    @staticmethod
    def calculate_slider_track_bounds(orientation: str, widget_size: Tuple[int, int], 
                                    handle_size: int) -> Rectangle:
        """Calculate slider track boundaries"""
        width, height = widget_size
        
        if orientation == "horizontal":
            return Rectangle(
                handle_size // 2,
                height // 2 - 4,
                width - handle_size,
    
            )
        else:
            return Rectangle(
                width // 2 - 4,
                handle_size // 2,
    
                height - handle_size
            )
    
    @staticmethod
    def interpolate_along_path(points: List[Point], t: float) -> Point:
        """Interpolate position along a path of points"""
        if not points or t <= 0:
            return points[0] if points else Point(0, 0)
        if t >= 1:
            return points[-1] if points else Point(0, 0)
        
        # Find segment
        segment_length = 1.0 / (len(points) - 1)
        segment_index = int(t / segment_length)
        local_t = (t % segment_length) / segment_length
        
        if segment_index >= len(points) - 1:
            return points[-1]
        
        start_point = points[segment_index]
        end_point = points[segment_index + 1]
        
        return Point(
            GeometryUtils.lerp(start_point.x, end_point.x, local_t),
            GeometryUtils.lerp(start_point.y, end_point.y, local_t)
        )

    
    @staticmethod
    def round_rectangle_path(rect: Rectangle, radius: float) -> List[Point]:
        """Generate points for a rounded rectangle"""
        points = []
        
        # Limit radius
        max_radius = min(rect.width / 2, rect.height / 2)
        radius = min(radius, max_radius)
        
        if radius <= 0:
            # Normal rectangle
            points.extend([
                Point(rect.x, rect.y),
                Point(rect.x + rect.width, rect.y),
                Point(rect.x + rect.width, rect.y + rect.height),
                Point(rect.x, rect.y + rect.height)
            ])
        else:
            # Rounded rectangle - approximation with segments
            segments = 8  # Number of segments per corner
            
            # Top-left corner
            for i in range(segments + 1):
                angle = math.pi + i * (math.pi / 2) / segments
                x = rect.x + radius + radius * math.cos(angle)
                y = rect.y + radius + radius * math.sin(angle)
                points.append(Point(x, y))
            
            # Top-right corner
            for i in range(segments + 1):
                angle = 1.5 * math.pi + i * (math.pi / 2) / segments
                x = rect.x + rect.width - radius + radius * math.cos(angle)
                y = rect.y + radius + radius * math.sin(angle)
                points.append(Point(x, y))
            
            # Bottom-right corner
            for i in range(segments + 1):
                angle = 2 * math.pi + i * (math.pi / 2) / segments
                x = rect.x + rect.width - radius + radius * math.cos(angle)
                y = rect.y + rect.height - radius + radius * math.sin(angle)
                points.append(Point(x, y))
            
            # Bottom-left corner
            for i in range(segments + 1):
                angle = 0.5 * math.pi + i * (math.pi / 2) / segments
                x = rect.x + radius + radius * math.cos(angle)
                y = rect.y + rect.height - radius + radius * math.sin(angle)
                points.append(Point(x, y))
        
        return points
    
    @staticmethod
    def calculate_bezier_point(t: float, p0: Point, p1: Point, p2: Point, p3: Point) -> Point:
        """Calculate a point on a cubic Bezier curve"""
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t
        
        x = uuu * p0.x + 3 * uu * t * p1.x + 3 * u * tt * p2.x + ttt * p3.x
        y = uuu * p0.y + 3 * uu * t * p1.y + 3 * u * tt * p2.y + ttt * p3.y
        
        return Point(x, y)
    
    @staticmethod
    def normalize_angle(angle: float) -> float:
        """Normalize an angle to [0, 2π)"""
        while angle < 0:
            angle += 2 * math.pi
        while angle >= 2 * math.pi:
            angle -= 2 * math.pi
        return angle
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convert degrees to radians"""
        return degrees * math.pi / 180
    
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """Convert radians to degrees"""
        return radians * 180 / math.pi

# Common color palettes
class ColorPalettes:
    """Predefined color palettes"""
    
    MATERIAL_DESIGN = {
        'blue': '#2196F3',
        'red': '#F44336',
        'green': '#4CAF50',
        'orange': '#FF9800',
        'purple': '#9C27B0',
        'teal': '#009688',
        'indigo': '#3F51B5',
        'pink': '#E91E63'
    }
    
    FLAT_UI = {
        'turquoise': '#1ABC9C',
        'emerland': '#2ECC71',
        'peter_river': '#3498DB',
        'amethyst': '#9B59B6',
        'wet_asphalt': '#34495E',
        'green_sea': '#16A085',
        'nephritis': '#27AE60',
        'belize_hole': '#2980B9',
        'wisteria': '#8E44AD',
        'midnight_blue': '#2C3E50'
    }
    
    BOOTSTRAP = {
        'primary': '#007bff',
        'secondary': '#6c757d',
        'success': '#28a745',
        'danger': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40'
    }
    
# Nouvelles classes pour les sliders
@dataclass
class SliderGeometry:
    """Geometry calculations specific to sliders"""
    track_rect: Rectangle
    handle_positions: List[Point]
    interaction_zones: List[Rectangle]
    
    def get_handle_at_point(self, point: Point) -> Optional[int]:
        """Get handle index at given point"""
        for i, zone in enumerate(self.interaction_zones):
            if zone.contains_point(point):
                return i
        return None

class SliderMath:
    """Mathematical utilities for slider calculations"""
    
    @staticmethod
    def linear_to_log(value: float, min_val: float, max_val: float, 
                     log_min: float, log_max: float) -> float:
        """Convert linear value to logarithmic scale"""
        if value <= 0:
            return log_min
        
        linear_pos = (value - min_val) / (max_val - min_val)
        log_range = math.log10(log_max) - math.log10(log_min)
        log_value = math.log10(log_min) + linear_pos * log_range
        return math.pow(10, log_value)
    
    @staticmethod
    def log_to_linear(log_value: float, min_val: float, max_val: float,
                     log_min: float, log_max: float) -> float:
        """Convert logarithmic value to linear scale"""
        if log_value <= 0:
            return min_val
        
        log_pos = (math.log10(log_value) - math.log10(log_min)) / (math.log10(log_max) - math.log10(log_min))
        return min_val + log_pos * (max_val - min_val)
    
    @staticmethod
    def snap_to_grid(value: float, grid_size: float) -> float:
        """Snap value to grid"""
        return round(value / grid_size) * grid_size
    
    @staticmethod
    def calculate_handle_collision(handle1_pos: Point, handle2_pos: Point,
                                 handle_size: float, min_distance: float) -> Tuple[Point, Point]:
        """Calculate positions to avoid handle collision"""
        distance = GeometryUtils.distance(handle1_pos, handle2_pos)
        
        if distance < min_distance:
            # Push handles apart
            direction_x = handle2_pos.x - handle1_pos.x
            direction_y = handle2_pos.y - handle1_pos.y
            
            if distance > 0:
                direction_x /= distance
                direction_y /= distance
            else:
                direction_x, direction_y = 1, 0
            
            push_distance = (min_distance - distance) / 2
            
            new_pos1 = Point(
                handle1_pos.x - direction_x * push_distance,
                handle1_pos.y - direction_y * push_distance
            )
            new_pos2 = Point(
                handle2_pos.x + direction_x * push_distance,
                handle2_pos.y + direction_y * push_distance
            )
            
            return new_pos1, new_pos2
        
        return handle1_pos, handle2_pos



# Ajouter ces nouvelles classes utilitaires à la fin du fichier

class ValidationUtils:
    """Utilities for input validation"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Quick email validation check"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Quick phone validation check"""
        import re
        clean_phone = re.sub(r'[^\d+]', '', phone)
        return len(clean_phone) >= 10
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Quick URL validation check"""
        import re
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input text"""
        import html
        return html.escape(text.strip())

class InteractionUtils:
    """Utilities for user interaction handling"""
    
    @staticmethod
    def calculate_drag_velocity(positions: list, times: list) -> float:
        """Calculate drag velocity from position history"""
        if len(positions) < 2 or len(times) < 2:
            return 0.0
        
        # Use last few points for velocity calculation
        recent_positions = positions[-3:]
        recent_times = times[-3:]
        
        if len(recent_positions) < 2:
            return 0.0
        
        total_distance = sum(
            abs(recent_positions[i] - recent_positions[i-1]) 
            for i in range(1, len(recent_positions))
        )
        
        total_time = recent_times[-1] - recent_times[0]
        
        return total_distance / total_time if total_time > 0 else 0.0
    
    @staticmethod
    def smooth_value_transition(current: float, target: float, smoothing: float = 0.1) -> float:
        """Smooth value transition using linear interpolation"""
        return current + (target - current) * smoothing
    
    @staticmethod
    def detect_swipe_gesture(start_pos: Point, end_pos: Point, min_distance: float = 50.0) -> str:
        """Detect swipe gesture direction"""
        dx = end_pos.x - start_pos.x
        dy = end_pos.y - start_pos.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < min_distance:
            return "none"
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"

class RenderUtils:
    """Utilities for rendering and drawing"""
    
    @staticmethod
    def create_gradient_points(start_color: Color, end_color: Color, steps: int = 10) -> List[Color]:
        """Create gradient color points"""
        colors = []
        for i in range(steps):
            factor = i / (steps - 1) if steps > 1 else 0
            color = ColorUtils.interpolate_colors(start_color, end_color, factor)
            colors.append(color)
        return colors
    
    @staticmethod
    def calculate_text_bounds(text: str, font_size: int, font_family: str = "Arial") -> Rectangle:
        """Calculate approximate text bounds"""
        # Rough approximation - actual implementation would depend on GUI framework
        char_width = font_size * 0.6  # Approximate character width
        char_height = font_size * 1.2  # Approximate character height
        
        lines = text.split('\n')
        max_width = max(len(line) for line in lines) * char_width
        height = len(lines) * char_height
        
        return Rectangle(0, 0, max_width, height)
    
    @staticmethod
    def create_drop_shadow_points(rect: Rectangle, offset: Point, blur: float) -> List[Point]:
        """Create points for drop shadow effect"""
        points = []
        
        # Create shadow outline with blur approximation
        blur_steps = max(1, int(blur))
        
        for i in range(blur_steps):
            alpha = 1.0 - (i / blur_steps)
            shadow_rect = Rectangle(
                rect.x + offset.x + i,
                rect.y + offset.y + i,
                rect.width,
                rect.height
            )
            
            # Add corner points
            points.extend([
                Point(shadow_rect.x, shadow_rect.y),
                Point(shadow_rect.x + shadow_rect.width, shadow_rect.y),
                Point(shadow_rect.x + shadow_rect.width, shadow_rect.y + shadow_rect.height),
                Point(shadow_rect.x, shadow_rect.y + shadow_rect.height)
            ])
        
        return points

# Ajouter ces palettes de couleurs spécialisées
class WidgetColorPalettes:
    """Specialized color palettes for different widget types"""
    
    TEXT_INPUT = {
        'normal': '#f8f9fa',
        'focus': '#ffffff',
        'error': '#fee',
        'success': '#f0fff4',
        'disabled': '#e9ecef'
    }
    
    CHECKBOX = {
        'unchecked': '#e2e8f0',
        'checked': '#4299e1',
        'indeterminate': '#ed8936',
        'hover': '#3182ce',
        'disabled': '#f7fafc'
    }
    
    SWITCH = {
        'track_off': '#cbd5e0',
        'track_on': '#4299e1',
        'thumb': '#ffffff',
        'shadow': '#1a202c'
    }
    
    VALIDATION = {
        'success': '#38a169',
        'warning': '#d69e2e',
        'error': '#e53e3e',
        'info': '#3182ce'
    }

# Ajouter des constantes utiles
class WidgetConstants:
    """Constants for widget styling and behavior"""
    
    # Animation durations (in seconds)
    FAST_ANIMATION = 0.15
    NORMAL_ANIMATION = 0.3
    SLOW_ANIMATION = 0.6
    
    # Common dimensions
    SMALL_WIDGET_HEIGHT = 32
    NORMAL_WIDGET_HEIGHT = 40
    LARGE_WIDGET_HEIGHT = 48
    
    # Border radius values
    SMALL_RADIUS = 4
    NORMAL_RADIUS = 8
    LARGE_RADIUS = 12
    
    # Spacing values
    TIGHT_SPACING = 4
    NORMAL_SPACING = 8
    LOOSE_SPACING = 16
    
    # Shadow values
    LIGHT_SHADOW = 2
    NORMAL_SHADOW = 4
    HEAVY_SHADOW = 8
    
    # Validation patterns
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^\+?[1-9]\d{1,14}$'  # International format
    URL_PATTERN = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    
    # Drag and gesture thresholds
    DRAG_THRESHOLD = 5  # pixels
    SWIPE_THRESHOLD = 50  # pixels
    VELOCITY_THRESHOLD = 100  # pixels per second
    
    # Debounce timers (in seconds)
    VALIDATION_DEBOUNCE = 0.5
    SEARCH_DEBOUNCE = 0.3
    RESIZE_DEBOUNCE = 0.1


# Ajouter ces nouvelles fonctions utilitaires

class AnimationUtils:
    """Utilities for animation calculations"""
    
    @staticmethod
    def calculate_bezier_curve(t: float, points: List[Point]) -> Point:
        """Calculate point on Bezier curve of any degree"""
        n = len(points) - 1
        result_x = 0
        result_y = 0
        
        for i, point in enumerate(points):
            # Binomial coefficient
            binomial = math.comb(n, i)
            # Bernstein polynomial
            bernstein = binomial * (t ** i) * ((1 - t) ** (n - i))
            
            result_x += point.x * bernstein
            result_y += point.y * bernstein
        
        return Point(result_x, result_y)
    
    @staticmethod
    def create_spring_animation(stiffness: float = 100, damping: float = 10) -> Callable:
        """Create spring-based easing function"""
        def spring_easing(t: float) -> float:
            # Spring physics simulation
            if t <= 0:
                return 0
            if t >= 1:
                return 1
            
            # Simplified spring equation
            omega = math.sqrt(stiffness)
            zeta = damping / (2 * math.sqrt(stiffness))
            
            if zeta < 1:  # Underdamped
                omega_d = omega * math.sqrt(1 - zeta * zeta)
                envelope = math.exp(-zeta * omega * t)
                oscillation = math.cos(omega_d * t - math.acos(zeta))
                return 1 - envelope * oscillation
            else:  # Overdamped or critically damped
                return 1 - math.exp(-omega * t)
        
        return spring_easing
    
    @staticmethod
    def interpolate_points(p1: Point, p2: Point, factor: float) -> Point:
        """Interpolate between two points"""
        return Point(
            p1.x + (p2.x - p1.x) * factor,
            p1.y + (p2.y - p1.y) * factor
        )
    
    @staticmethod
    def calculate_arc_points(center: Point, radius: float, 
                           start_angle: float, end_angle: float, 
                           num_points: int = 50) -> List[Point]:
        """Calculate points along an arc"""
        points = []
        angle_step = (end_angle - start_angle) / (num_points - 1)
        
        for i in range(num_points):
            angle = start_angle + i * angle_step
            x = center.x + radius * math.cos(math.radians(angle))
            y = center.y + radius * math.sin(math.radians(angle))
            points.append(Point(x, y))
        
        return points

class PerformanceUtils:
    """Performance optimization utilities"""
    
    @staticmethod
    def debounce(func: Callable, delay: float) -> Callable:
        """Debounce function calls"""
        from threading import Timer
        timer = None
        
        def debounced(*args, **kwargs):
            nonlocal timer
            if timer:
                timer.cancel()
            timer = Timer(delay, lambda: func(*args, **kwargs))
            timer.start()
        return debounced
    

    
    @staticmethod
    def throttle(func: Callable, limit: float) -> Callable:
        """Throttle function calls"""
        last_called = [0]
        
        def throttled(*args, **kwargs):
            current_time = time.time()
            if current_time - last_called[0] >= limit:
                last_called[0] = current_time
                return func(*args, **kwargs)
        
        return throttled
    
    @staticmethod
    def create_render_cache(max_size: int = 100) -> dict:
        """Create a simple LRU cache for rendering optimization"""
        cache = {}
        access_order = []
        
        def get(key):
            if key in cache:
                # Move to end (most recently used)
                access_order.remove(key)
                access_order.append(key)
                return cache[key]
            return None
        
        def set(key, value):
            if key in cache:
                # Update existing
                cache[key] = value
                access_order.remove(key)
                access_order.append(key)
            else:
                # Add new
                if len(cache) >= max_size:
                    # Remove least recently used
                    lru_key = access_order.pop(0)
                    del cache[lru_key]
                
                cache[key] = value
                access_order.append(key)
        
        return {'get': get, 'set': set, 'clear': lambda: cache.clear()}

# Ajouter de nouveaux patterns de couleurs
class ColorPalettes:
    # ... existing palettes ...
    
    MODERN_DARK = {
        'background': '#1a1a1a',
        'surface': '#2d2d2d', 
        'primary': '#bb86fc',
        'secondary': '#03dac6',
        'accent': '#ff6b6b',
        'text': '#ffffff',
        'text_secondary': '#b3b3b3',
        'border': '#404040'
    }
    
    NATURE = {
        'forest': '#2d5016',
        'grass': '#7fb069',
        'sky': '#87ceeb',
        'earth': '#8b4513',
        'water': '#4682b4',
        'sun': '#ffd700',
        'flower': '#ff69b4',
        'leaf': '#90ee90'
    }
    
    NEON = {
        'electric_blue': '#00ffff',
        'neon_green': '#39ff14',
        'hot_pink': '#ff1493',
        'bright_yellow': '#ffff00',
        'purple': '#bf00ff',
        'orange': '#ff4500',
        'red': '#ff0000',
        'white': '#ffffff'
    }

class ThemeManager:
    """Manage application themes"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": {
                "background": "#ffffff",
                "text": "#000000",
                "primary": "#3498db",
                "secondary": "#95a5a6"
            },
            "dark": {
                "background": "#2c3e50",
                "text": "#ecf0f1", 
                "primary": "#3498db",
                "secondary": "#95a5a6"
            }
        }
    
    def add_theme(self, name: str, colors: dict):
        """Add a new theme"""
        self.themes[name] = colors
    
    def set_theme(self, name: str):
        """Set current theme"""
        if name in self.themes:
            self.current_theme = name
    
    def get_color(self, color_name: str) -> str:
        """Get color from current theme"""
        return self.themes[self.current_theme].get(color_name, "#000000")
    
    def get_theme_colors(self) -> dict:
        """Get all colors from current theme"""
        return self.themes[self.current_theme].copy()

# Nouvelles palettes de couleurs pour sliders
class SliderColorPalettes:
    """Color palettes specifically for sliders"""
    
    BLUE_GRADIENT = {
        'track': '#e3f2fd',
        'active': '#2196f3',
        'handle': '#1976d2',
        'hover': '#1565c0',
        'pressed': '#0d47a1'
    }
    
    GREEN_NATURE = {
        'track': '#e8f5e8',
        'active': '#4caf50',
        'handle': '#388e3c',
        'hover': '#2e7d32',
        'pressed': '#1b5e20'
    }
    
    ORANGE_WARM = {
        'track': '#fff3e0',
        'active': '#ff9800',
        'handle': '#f57c00',
        'hover': '#ef6c00',
        'pressed': '#e65100'
    }
    
    PURPLE_ROYAL = {
        'track': '#f3e5f5',
        'active': '#9c27b0',
        'handle': '#7b1fa2',
        'hover': '#6a1b9a',
        'pressed': '#4a148c'
    }