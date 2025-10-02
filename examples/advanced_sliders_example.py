"""
advanced_sliders_example.py - Démonstration avancée des sliders animés
Montre toutes les fonctionnalités et types de sliders disponibles
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import math
import time
import threading
from typing import Dict, List, Tuple, Any

# Add library path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animated_widgets_pack import (
    AnimatedSlider, SliderStyle, SliderConfig, WidgetConfig,
    SliderOrientation, SliderType, HandleShape, TrackStyle,
    SliderPresets, ColorUtils, EasingType
)

from animated_widgets_pack.animations import AnimationConfig

class AdvancedSlidersDemo:
    """Démonstration complète des sliders animés"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AnimatedWidgetsPack - Advanced Sliders Demo")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f5f5f5")
        
        # Center window
        self.center_window()
        
        # Data for real-time updates
        self.update_thread = None
        self.is_running = True
        
        # Store all sliders for bulk operations
        self.all_sliders: Dict[str, AnimatedSlider] = {}
        
        # Audio visualization data
        self.audio_bands = [0.0] * 10
        self.audio_animation_active = False
        
        # Color mixer values
        self.color_values = {'r': 128, 'g': 128, 'b': 128}
        
        self.create_widgets()
        self.start_background_animations()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
    
    def create_widgets(self):
        """Create all demo widgets"""
        
        # Main title
        title = tk.Label(
            self.root,
            text="🎛️ Advanced Animated Sliders Showcase",
            font=("Arial", 24, "bold"),
            bg="#f5f5f5",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Create notebook for organized sections
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create different demo sections
        self.create_basic_sliders_tab(notebook)
        self.create_range_sliders_tab(notebook)
        self.create_styled_sliders_tab(notebook)
        self.create_interactive_demo_tab(notebook)
        self.create_audio_visualizer_tab(notebook)
        self.create_color_mixer_tab(notebook)
        self.create_advanced_features_tab(notebook)
        
        # Control panel at bottom
        self.create_control_panel()
    
    def create_basic_sliders_tab(self, notebook):
        """Basic sliders demonstration"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Basic Sliders")
        
        # Scrollable frame
        canvas = tk.Canvas(frame, bg="#ffffff")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Horizontal sliders section
        h_section = tk.LabelFrame(
            scrollable_frame, 
            text="Horizontal Sliders", 
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        h_section.pack(fill="x", padx=10, pady=10)
        
        # Basic horizontal slider
        self.create_slider_demo(
            h_section, "Basic Horizontal", "basic_horizontal",
            SliderConfig(orientation=SliderOrientation.HORIZONTAL),
            SliderStyle(),
            "Simple horizontal slider with default styling"
        )
        
        # Stepped slider
        self.create_slider_demo(
            h_section, "Stepped Slider (Step: 10)", "stepped",
            SliderConfig(
                orientation=SliderOrientation.HORIZONTAL,
                slider_type=SliderType.STEPPED,
                step_size=10,
                min_value=0,
                max_value=100
            ),
            SliderStyle(snap_to_steps=True, show_ticks=True, tick_count=10),
            "Slider that snaps to discrete steps"
        )
        
        # Precision slider
        self.create_slider_demo(
            h_section, "High Precision (0.01)", "precision",
            SliderConfig(
                orientation=SliderOrientation.HORIZONTAL,
                min_value=0,
                max_value=1,
                initial_value=0.5,
                step_size=0.01,
                precision=3
            ),
            SliderStyle(show_value_label=True),
            "High precision slider for fine adjustments"
        )
        
        # Large range slider
        self.create_slider_demo(
            h_section, "Large Range (0-10000)", "large_range",
            SliderConfig(
                orientation=SliderOrientation.HORIZONTAL,
                min_value=0,
                max_value=10000,
                initial_value=5000,
                step_size=100
            ),
            SliderStyle(show_min_max_labels=True),
            "Slider with large value range"
        )
        
        # Vertical sliders section
        v_section = tk.LabelFrame(
            scrollable_frame,
            text="Vertical Sliders",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        v_section.pack(fill="x", padx=10, pady=10)
        
        v_container = tk.Frame(v_section, bg="#ffffff")
        v_container.pack(fill="x")
        
        # Create vertical sliders side by side
        for i, (name, config, style, desc) in enumerate([
            ("Basic Vertical", 
             SliderConfig(orientation=SliderOrientation.VERTICAL),
             SliderStyle(),
             "Basic vertical slider"),
            ("Volume Control",
             SliderConfig(orientation=SliderOrientation.VERTICAL, initial_value=75),
             SliderStyle(
                 track_color="#e0e0e0",
                 track_active_color="#4caf50",
                 handle_color="#4caf50",
                 handle_hover_color="#45a049"
             ),
             "Volume-style slider"),
            ("Temperature",
             SliderConfig(
                 orientation=SliderOrientation.VERTICAL,
                 min_value=-20,
                 max_value=50,
                 initial_value=22,
                 precision=1
             ),
             SliderStyle(
                 track_color="#e3f2fd",
                 track_active_color="#2196f3",
                 handle_color="#1976d2"
             ),
             "Temperature control")
        ]):
            self.create_vertical_slider_demo(
                v_container, name, f"vertical_{i}", config, style, desc
            )
    
    def create_range_sliders_tab(self, notebook):
        """Range sliders demonstration"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Range Sliders")
        
        main_frame = tk.Frame(frame, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Price range slider
        price_section = tk.LabelFrame(
            main_frame,
            text="Price Range Selector",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        price_section.pack(fill="x", pady=10)
        
        price_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            slider_type=SliderType.RANGE,
            min_value=0,
            max_value=1000,
            initial_range=(200, 800),
            value_formatter=lambda x: f"${x:.0f}"
        )
        
        price_style = SliderStyle(
            track_color="#f5f5f5",
            track_active_color="#27ae60",
            handle_color="#27ae60",
            handle_hover_color="#229954",
            handle_pressed_color="#1e8449",
            show_min_max_labels=True,
            show_value_label=True
        )
        
        self.create_range_slider_demo(
            price_section, "Price Range", "price_range",
            price_config, price_style,
            "Select minimum and maximum price range"
        )
        
        # Time range slider
        time_section = tk.LabelFrame(
            main_frame,
            text="Time Range Selector",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        time_section.pack(fill="x", pady=10)
        
        time_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            slider_type=SliderType.RANGE,
            min_value=0,
            max_value=24,
            initial_range=(9, 17),
            precision=1,
            value_formatter=lambda x: f"{int(x)}:{int((x % 1) * 60):02d}"
        )
        
        time_style = SliderStyle(
            track_color="#e8eaf6",
            track_active_color="#3f51b5",
            handle_color="#3f51b5",
            handle_hover_color="#303f9f",
            handle_size=24,
            show_ticks=True,
            tick_count=24
        )
        
        self.create_range_slider_demo(
            time_section, "Working Hours", "time_range",
            time_config, time_style,
            "Select start and end time for working hours"
        )
        
        # Percentage range
        percent_section = tk.LabelFrame(
            main_frame,
            text="Percentage Range",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        percent_section.pack(fill="x", pady=10)
        
        percent_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            slider_type=SliderType.RANGE,
            min_value=0,
            max_value=100,
            initial_range=(25, 75),
            step_size=5,
            value_formatter=lambda x: f"{x:.0f}%"
        )
        
        percent_style = SliderStyle(
            track_color="#fff3e0",
            track_active_color="#ff9800",
            handle_color="#f57c00",
            handle_hover_color="#ef6c00",
            snap_to_steps=True,
            show_ticks=True,
            tick_count=20
        )
        
        self.create_range_slider_demo(
            percent_section, "Percentage Range", "percent_range",
            percent_config, percent_style,
            "Select percentage range with 5% steps"
        )
    
    def create_styled_sliders_tab(self, notebook):
        """Styled sliders with different themes"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Styled Themes")
        
        main_frame = tk.Frame(frame, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Material Design
        material_section = tk.LabelFrame(
            main_frame,
            text="Material Design Theme",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        material_section.pack(fill="x", pady=10)
        
        self.create_slider_demo(
            material_section, "Material Slider", "material",
            SliderConfig(orientation=SliderOrientation.HORIZONTAL),
            SliderPresets.material_design(),
            "Google Material Design inspired slider"
        )
        
        # Flat Design
        flat_section = tk.LabelFrame(
            main_frame,
            text="Flat Design Theme",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        flat_section.pack(fill="x", pady=10)
        
        self.create_slider_demo(
            flat_section, "Flat Slider", "flat",
            SliderConfig(orientation=SliderOrientation.HORIZONTAL),
            SliderPresets.flat_design(),
            "Minimalist flat design slider"
        )
        
        # Neumorphism
        neuro_section = tk.LabelFrame(
            main_frame,
            text="Neumorphism Theme",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        neuro_section.pack(fill="x", pady=10)
        
        self.create_slider_demo(
            neuro_section, "Neumorphic Slider", "neumorphic",
            SliderConfig(orientation=SliderOrientation.HORIZONTAL),
            SliderPresets.neumorphism(),
            "Soft UI neumorphism design"
        )
        
        # Dark Theme
        dark_section = tk.LabelFrame(
            main_frame,
            text="Dark Theme",
            font=("Arial", 14, "bold"),
            bg="#2c2c2c",
            fg="#ffffff",
            padx=15, pady=15
        )
        dark_section.pack(fill="x", pady=10)
        
        self.create_slider_demo(
            dark_section, "Dark Slider", "dark",
            SliderConfig(orientation=SliderOrientation.HORIZONTAL),
            SliderPresets.dark_theme(),
            "Dark theme for night mode interfaces"
        )
        
        # Custom gradient slider
        gradient_section = tk.LabelFrame(
            main_frame,
            text="Custom Gradient Theme",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        gradient_section.pack(fill="x", pady=10)
        
        gradient_style = SliderStyle(
            track_color="#f8f9fa",
            track_active_color="#6f42c1",
            handle_color="#6f42c1",
            handle_hover_color="#5a32a3",
            handle_pressed_color="#4c2a85",
            handle_size=26,
            track_height=10,
            handle_border_width=3,
            handle_border_color="#ffffff",
            handle_shadow=True,
            handle_shadow_color="#00000040",
            handle_shadow_offset=(0, 4),
            handle_shadow_blur=8
        )
        
        self.create_slider_demo(
            gradient_section, "Gradient Slider", "gradient",
            SliderConfig(orientation=SliderOrientation.HORIZONTAL),
            gradient_style,
            "Custom gradient theme with shadows"
        )
    
    def create_interactive_demo_tab(self, notebook):
        """Interactive demonstrations"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Interactive Demos")
        
        main_frame = tk.Frame(frame, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Real-time value display
        realtime_section = tk.LabelFrame(
            main_frame,
            text="Real-time Value Updates",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        realtime_section.pack(fill="x", pady=10)
        
        # Create multiple connected sliders
        self.realtime_values = tk.StringVar(value="Values will update in real-time...")
        realtime_label = tk.Label(
            realtime_section,
            textvariable=self.realtime_values,
            font=("Courier", 12),
            bg="#f8f9fa",
            fg="#495057",
            relief="sunken",
            padx=10, pady=5
        )
        realtime_label.pack(fill="x", pady=(0, 10))
        
        # Slider that controls others
        master_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            min_value=0,
            max_value=100,
            initial_value=50
        )
        
        master_style = SliderStyle(
            track_color="#e9ecef",
            track_active_color="#007bff",
            handle_color="#007bff",
            handle_hover_color="#0056b3",
            handle_size=28,
            show_value_label=True
        )
        
        master_slider = self.create_interactive_slider(
            realtime_section, "Master Control", "master",
            master_config, master_style
        )
        
        # Slave sliders
        slave_frame = tk.Frame(realtime_section, bg="#ffffff")
        slave_frame.pack(fill="x", pady=10)
        
        for i, color in enumerate(["#dc3545", "#28a745", "#ffc107"]):
            slave_config = SliderConfig(
                orientation=SliderOrientation.HORIZONTAL,
                min_value=0,
                max_value=100,
                initial_value=25 + i * 25
            )
            
            slave_style = SliderStyle(
                track_color="#f8f9fa",
                track_active_color=color,
                handle_color=color,
                handle_hover_color=ColorUtils.darken_color(color, 0.1).to_hex(),
                handle_size=20
            )
            
            self.create_interactive_slider(
                slave_frame, f"Slave {i+1}", f"slave_{i}",
                slave_config, slave_style
            )
        
        # Mathematical function demo
        math_section = tk.LabelFrame(
            main_frame,
            text="Mathematical Functions",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        math_section.pack(fill="x", pady=10)
        
        # Function parameters
        self.math_result = tk.StringVar(value="f(x) = sin(0.0) = 0.000")
        math_label = tk.Label(
            math_section,
            textvariable=self.math_result,
            font=("Courier", 14, "bold"),
            bg="#e8f4fd",
            fg="#0c5aa6",
            relief="sunken",
            padx=10, pady=8
        )
        math_label.pack(fill="x", pady=(0, 10))
        
        # X parameter slider
        x_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            min_value=0,
            max_value=4 * math.pi,
            initial_value=0,
            precision=3,
            value_formatter=lambda x: f"{x:.3f}"
        )
        
        x_style = SliderStyle(
            track_color="#e1f5fe",
            track_active_color="#0288d1",
            handle_color="#0277bd",
            show_value_label=True
        )
        
        x_slider = self.create_math_slider(
            math_section, "X Parameter (0 to 4π)", "math_x",
            x_config, x_style, self.update_math_function
        )
        
        # Animation demo
        animation_section = tk.LabelFrame(
            main_frame,
            text="Animation Showcase",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        animation_section.pack(fill="x", pady=10)
        
        # Animation controls
        anim_controls = tk.Frame(animation_section, bg="#ffffff")
        anim_controls.pack(fill="x", pady=(0, 10))
        
        self.create_animation_buttons(anim_controls)
        
        # Animated slider
        anim_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            min_value=0,
            max_value=100,
            initial_value=0
        )
        
        anim_style = SliderStyle(
            track_color="#f3e5f5",
            track_active_color="#9c27b0",
            handle_color="#7b1fa2",
            handle_hover_color="#6a1b9a",
            handle_size=24,
            handle_hover_scale=1.3,
            show_value_label=True
        )
        
        self.animated_slider = self.create_interactive_slider(
            animation_section, "Animated Slider", "animated",
            anim_config, anim_style
        )
    
    def create_audio_visualizer_tab(self, notebook):
        """Audio visualizer using sliders"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Audio Visualizer")
        
        main_frame = tk.Frame(frame, bg="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = tk.Label(
            main_frame,
            text="🎵 Audio Equalizer Visualizer",
            font=("Arial", 18, "bold"),
            bg="#1a1a1a",
            fg="#ffffff"
        )
        title.pack(pady=20)
        
        # Controls
        controls = tk.Frame(main_frame, bg="#1a1a1a")
        controls.pack(pady=10)
        
        self.create_audio_controls(controls)
        
        # Equalizer bands
        eq_frame = tk.Frame(main_frame, bg="#1a1a1a")
        eq_frame.pack(fill="both", expand=True, pady=20)
        
        # Create 10 frequency bands
        self.eq_sliders = []
        frequencies = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        
        for i, freq in enumerate(frequencies):
            band_frame = tk.Frame(eq_frame, bg="#1a1a1a")
            band_frame.pack(side="left", fill="both", expand=True, padx=5)
            
            # Frequency label
            freq_label = tk.Label(
                band_frame,
                text=f"{freq}Hz" if freq < 1000 else f"{freq//1000}kHz",
                font=("Arial", 10),
                bg="#1a1a1a",
                fg="#888888"
            )
            freq_label.pack()
            
            # Vertical slider for each band
            band_config = SliderConfig(
                orientation=SliderOrientation.VERTICAL,
                min_value=-12,
                max_value=12,
                initial_value=0,
                precision=1,
                value_formatter=lambda x: f"{x:+.1f}dB"
            )
            
            # Color based on frequency
            if freq < 250:
                color = "#ff4444"  # Bass - Red
            elif freq < 2000:
                color = "#44ff44"  # Mid - Green
            else:
                color = "#4444ff"  # Treble - Blue
            
            band_style = SliderStyle(
                track_color="#333333",
                track_active_color=color,
                handle_color=color,
                handle_hover_color=ColorUtils.lighten_color(color, 0.2).to_hex(),
                handle_size=18,
                track_height=6,
                show_value_label=True,
                label_color="#ffffff"
            )
            
            slider = self.create_audio_band_slider(
                band_frame, f"Band {i}", f"eq_band_{i}",
                band_config, band_style, i
            )
            
            self.eq_sliders.append(slider)
    
    def create_color_mixer_tab(self, notebook):
        """Color mixer using sliders"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Color Mixer")
        
        main_frame = tk.Frame(frame, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = tk.Label(
            main_frame,
            text="🎨 RGB Color Mixer",
            font=("Arial", 18, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Color preview
        self.color_preview = tk.Frame(
            main_frame,
            bg="#808080",
            height=150,
            relief="raised",
            bd=3
        )
        self.color_preview.pack(fill="x", pady=20)
        self.color_preview.pack_propagate(False)
        
        # Color info label
        self.color_info = tk.StringVar(value="RGB(128, 128, 128) | #808080")
        color_label = tk.Label(
            main_frame,
            textvariable=self.color_info,
            font=("Courier", 14, "bold"),
            bg="#f8f9fa",
            fg="#495057",
            relief="sunken",
            padx=10, pady=5
        )
        color_label.pack(fill="x", pady=(0, 20))
        
        # RGB sliders
        rgb_frame = tk.Frame(main_frame, bg="#ffffff")
        rgb_frame.pack(fill="x", pady=10)
        
        # Red slider
        red_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            min_value=0,
            max_value=255,
            initial_value=128,
            precision=0
        )
        
        red_style = SliderStyle(
            track_color="#ffebee",
            track_active_color="#f44336",
            handle_color="#d32f2f",
            handle_hover_color="#b71c1c",
            show_value_label=True,
            show_min_max_labels=True
        )
        
        self.red_slider = self.create_color_slider(
            rgb_frame, "Red Channel", "red",
            red_config, red_style, 'r'
        )
        
        # Green slider
        green_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            min_value=0,
            max_value=255,
            initial_value=128,
            precision=0
        )
        
        green_style = SliderStyle(
            track_color="#e8f5e8",
            track_active_color="#4caf50",
            handle_color="#388e3c",
            handle_hover_color="#2e7d32",
            show_value_label=True,
            show_min_max_labels=True
        )
        
        self.green_slider = self.create_color_slider(
            rgb_frame, "Green Channel", "green",
            green_config, green_style, 'g'
        )
        
        # Blue slider
        blue_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            min_value=0,
            max_value=255,
            initial_value=128,
            precision=0
        )
        
        blue_style = SliderStyle(
            track_color="#e3f2fd",
            track_active_color="#2196f3",
            handle_color="#1976d2",
            handle_hover_color="#1565c0",
            show_value_label=True,
            show_min_max_labels=True
        )
        
        self.blue_slider = self.create_color_slider(
            rgb_frame, "Blue Channel", "blue",
            blue_config, blue_style, 'b'
        )
        
        # Color presets
        presets_frame = tk.LabelFrame(
            main_frame,
            text="Color Presets",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=10, pady=10
        )
        presets_frame.pack(fill="x", pady=20)
        
        self.create_color_presets(presets_frame)
    
    def create_advanced_features_tab(self, notebook):
        """Advanced features demonstration"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Advanced Features")
        
        main_frame = tk.Frame(frame, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logarithmic slider
        log_section = tk.LabelFrame(
            main_frame,
            text="Logarithmic Scale Slider",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        log_section.pack(fill="x", pady=10)
        
        log_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            slider_type=SliderType.LOG_SCALE,
            min_value=1,
            max_value=10000,
            initial_value=100,
            precision=0,
            value_formatter=lambda x: f"{x:.0f}"
        )
        
        log_style = SliderStyle(
            track_color="#fff8e1",
            track_active_color="#ff8f00",
            handle_color="#ef6c00",
            show_value_label=True,
            show_min_max_labels=True
        )
        
        self.create_slider_demo(
            log_section, "Logarithmic Slider (1-10000)", "logarithmic",
            log_config, log_style,
            "Slider with logarithmic scale for wide value ranges"
        )
        
        # Custom validation slider  
        validation_section = tk.LabelFrame(
            main_frame,
            text="Validation & Constraints",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        validation_section.pack(fill="x", pady=10)
        
        # Status display for validation
        self.validation_status = tk.StringVar(value="✅ Valid")
        status_label = tk.Label(
            validation_section,
            textvariable=self.validation_status,
            font=("Arial", 12, "bold"),
            bg="#d4edda",
            fg="#155724",
            relief="sunken",
            padx=10, pady=5
        )
        status_label.pack(fill="x", pady=(0, 10))
        
        validation_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            min_value=0,
            max_value=100,
            initial_value=50
        )
        
        validation_style = SliderStyle(
            track_color="#f8f9fa",
            track_active_color="#17a2b8",
            handle_color="#138496",
            show_value_label=True
        )
        
        validation_slider = self.create_validation_slider(
            validation_section, "Validated Slider", "validation",
            validation_config, validation_style
        )
        
        # Add validation rules
        validation_slider.add_validation_rule(lambda x: x >= 20)  # Minimum 20
        validation_slider.add_validation_rule(lambda x: x <= 80)  # Maximum 80
        validation_slider.add_validation_rule(lambda x: x % 5 == 0)  # Multiple of 5
        
        # Performance test slider
        performance_section = tk.LabelFrame(
            main_frame,
            text="Performance Test",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            padx=15, pady=15
        )
        performance_section.pack(fill="x", pady=10)
        
        # Performance metrics
        self.perf_metrics = tk.StringVar(value="Updates: 0 | FPS: 0 | Avg: 0ms")
        perf_label = tk.Label(
            performance_section,
            textvariable=self.perf_metrics,
            font=("Courier", 10),
            bg="#f8f9fa",
            fg="#6c757d",
            relief="sunken",
            padx=10, pady=5
        )
        perf_label.pack(fill="x", pady=(0, 10))
        
        performance_config = SliderConfig(
            orientation=SliderOrientation.HORIZONTAL,
            min_value=0,
            max_value=1000,
            initial_value=500,
            precision=0
        )
        
        performance_style = SliderStyle(
            track_color="#e9ecef",
            track_active_color="#6c757d",
            handle_color="#495057",
            show_value_label=True
        )
        
        self.perf_slider = self.create_performance_slider(
            performance_section, "Performance Test Slider", "performance",
            performance_config, performance_style
        )
        
        # Start performance monitoring
        self.start_performance_monitoring()
    
    def create_slider_demo(self, parent, title, slider_id, config, style, description):
        """Create a slider demonstration"""
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(fill="x", pady=15)
        
        # Title and description
        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 12, "bold"),
            bg=parent.cget("bg"),
            fg="#2c3e50"
        )
        title_label.pack(anchor="w")
        
        desc_label = tk.Label(
            container,
            text=description,
            font=("Arial", 10),
            bg=parent.cget("bg"),
            fg="#6c757d"
        )
        desc_label.pack(anchor="w", pady=(0, 5))
        
        # Create and render slider
        widget_config = WidgetConfig(width=400, height=60)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(container, "tkinter")
        slider_widget.pack(pady=5)
        
        # Store slider reference
        self.all_sliders[slider_id] = slider
        
        # Value display
        value_var = tk.StringVar()
        self.update_slider_display(slider, value_var)
        
        value_label = tk.Label(
            container,
            textvariable=value_var,
            font=("Courier", 10),
            bg=parent.cget("bg"),
            fg="#495057"
        )
        value_label.pack(anchor="w")
        
        # Bind value change callback
        slider.on_value_changed(lambda val: self.update_slider_display(slider, value_var))
        
        return slider
    
    def create_vertical_slider_demo(self, parent, title, slider_id, config, style, description):
        """Create a vertical slider demonstration"""
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(side="left", padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 11, "bold"),
            bg=parent.cget("bg"),
            fg="#2c3e50"
        )
        title_label.pack()
        
        # Create slider
        widget_config = WidgetConfig(width=80, height=200)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(container, "tkinter")
        slider_widget.pack(pady=10)
        
        # Store slider
        self.all_sliders[slider_id] = slider
        
        # Value display
        value_var = tk.StringVar()
        self.update_slider_display(slider, value_var)
        
        value_label = tk.Label(
            container,
            textvariable=value_var,
            font=("Courier", 9),
            bg=parent.cget("bg"),
            fg="#495057"
        )
        value_label.pack()
        
        # Description
        desc_label = tk.Label(
            container,
            text=description,
            font=("Arial", 8),
            bg=parent.cget("bg"),
            fg="#6c757d",
            wraplength=100,
            justify="center"
        )
        desc_label.pack(pady=(5, 0))
        
        slider.on_value_changed(lambda val: self.update_slider_display(slider, value_var))
        
        return slider
    
    def create_range_slider_demo(self, parent, title, slider_id, config, style, description):
        """Create a range slider demonstration"""
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(fill="x", pady=10)
        
        # Title and description
        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 12, "bold"),
            bg=parent.cget("bg"),
            fg="#2c3e50"
        )
        title_label.pack(anchor="w")
        
        desc_label = tk.Label(
            container,
            text=description,
            font=("Arial", 10),
            bg=parent.cget("bg"),
            fg="#6c757d"
        )
        desc_label.pack(anchor="w", pady=(0, 5))
        
        # Create slider
        widget_config = WidgetConfig(width=500, height=60)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(container, "tkinter")
        slider_widget.pack(pady=5)
        
        # Store slider
        self.all_sliders[slider_id] = slider
        
        # Value display
        value_var = tk.StringVar()
        self.update_range_slider_display(slider, value_var)
        
        value_label = tk.Label(
            container,
            textvariable=value_var,
            font=("Courier", 11, "bold"),
            bg="#f8f9fa",
            fg="#495057",
            relief="sunken",
            padx=10, pady=3
        )
        value_label.pack(anchor="w", pady=(5, 0))
        
        slider.on_value_changed(lambda val: self.update_range_slider_display(slider, value_var))
        
        return slider
    
    def create_interactive_slider(self, parent, title, slider_id, config, style):
        """Create an interactive slider"""
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(fill="x", pady=5)
        
        # Title
        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 11, "bold"),
            bg=parent.cget("bg"),
            fg="#2c3e50"
        )
        title_label.pack(side="left", padx=(0, 10))
        
        # Create slider
        widget_config = WidgetConfig(width=300, height=50)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(container, "tkinter")
        slider_widget.pack(side="left", padx=5)
        
        # Store slider
        self.all_sliders[slider_id] = slider
        
        # Real-time callbacks
        slider.on_value_changed(self.update_realtime_display)
        
        return slider
    
    def create_math_slider(self, parent, title, slider_id, config, style, callback):
        """Create a mathematical function slider"""
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(fill="x", pady=5)
        
        # Title
        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 11, "bold"),
            bg=parent.cget("bg"),
            fg="#2c3e50"
        )
        title_label.pack(anchor="w")
        
        # Create slider
        widget_config = WidgetConfig(width=400, height=50)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(container, "tkinter")
        slider_widget.pack(pady=5)
        
        # Store slider
        self.all_sliders[slider_id] = slider
        
        # Bind callback
        slider.on_value_changed(callback)
        
        return slider
    
    def create_audio_band_slider(self, parent, title, slider_id, config, style, band_index):
        """Create an audio equalizer band slider"""
        widget_config = WidgetConfig(width=60, height=200)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(parent, "tkinter")
        slider_widget.pack(expand=True, fill="y")
        
        # Store slider
        self.all_sliders[slider_id] = slider
        
        # Bind audio band callback
        slider.on_value_changed(lambda val: self.update_audio_band(band_index, val))
        
        return slider
    
    def create_color_slider(self, parent, title, slider_id, config, style, channel):
        """Create a color channel slider"""
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(fill="x", pady=10)
        
        # Title
        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 12, "bold"),
            bg=parent.cget("bg"),
            fg="#2c3e50"
        )
        title_label.pack(anchor="w")
        
        # Create slider
        widget_config = WidgetConfig(width=400, height=50)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(container, "tkinter")
        slider_widget.pack(pady=5)
        
        # Store slider
        self.all_sliders[slider_id] = slider
        
        # Bind color update callback
        slider.on_value_changed(lambda val: self.update_color_channel(channel, val))
        
        return slider
    
    def create_validation_slider(self, parent, title, slider_id, config, style):
        """Create a validation slider"""
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(fill="x", pady=5)
        
        # Title
        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 11, "bold"),
            bg=parent.cget("bg"),
            fg="#2c3e50"
        )
        title_label.pack(anchor="w")
        
        # Create slider
        widget_config = WidgetConfig(width=400, height=50)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(container, "tkinter")
        slider_widget.pack(pady=5)
        
        # Store slider
        self.all_sliders[slider_id] = slider
        
        # Bind validation callback
        slider.on_value_changed(self.validate_slider_value)
        
        return slider
    
    def create_performance_slider(self, parent, title, slider_id, config, style):
        """Create a performance test slider"""
        container = tk.Frame(parent, bg=parent.cget("bg"))
        container.pack(fill="x", pady=5)
        
        # Title
        title_label = tk.Label(
            container,
            text=title,
            font=("Arial", 11, "bold"),
            bg=parent.cget("bg"),
            fg="#2c3e50"
        )
        title_label.pack(anchor="w")
        
        # Create slider
        widget_config = WidgetConfig(width=400, height=50)
        slider = AnimatedSlider(config=widget_config, config_slider=config, style=style)
        
        slider_widget = slider.render(container, "tkinter")
        slider_widget.pack(pady=5)
        
        # Store slider
        self.all_sliders[slider_id] = slider
        
        # Performance tracking
        self.perf_updates = 0
        self.perf_times = []
        self.perf_start_time = time.time()
        
        # Bind performance callback
        slider.on_value_changed(self.track_performance)
        
        return slider
    
    def create_animation_buttons(self, parent):
        """Create animation control buttons"""
        # Smooth animation button
        smooth_btn = tk.Button(
            parent,
            text="Smooth Slide to 25",
            bg="#28a745",
            fg="white",
            font=("Arial", 10),
            command=lambda: self.animate_slider_to_value(25, 1.0)
        )
        smooth_btn.pack(side="left", padx=5)
        
        # Bounce animation
        bounce_btn = tk.Button(
            parent,
            text="Bounce to 75",
            bg="#17a2b8",
            fg="white",
            font=("Arial", 10),
            command=lambda: self.animate_slider_bounce(75)
        )
        bounce_btn.pack(side="left", padx=5)
        
        # Elastic animation
        elastic_btn = tk.Button(
            parent,
            text="Elastic to 50",
            bg="#6f42c1",
            fg="white",
            font=("Arial", 10),
            command=lambda: self.animate_slider_elastic(50)
        )
        elastic_btn.pack(side="left", padx=5)
        
        # Random animation
        random_btn = tk.Button(
            parent,
            text="Random Value",
            bg="#fd7e14",
            fg="white",
            font=("Arial", 10),
            command=self.animate_slider_random
        )
        random_btn.pack(side="left", padx=5)
        
        # Reset button
        reset_btn = tk.Button(
            parent,
            text="Reset",
            bg="#6c757d",
            fg="white",
            font=("Arial", 10),
            command=lambda: self.animate_slider_to_value(0, 0.5)
        )
        reset_btn.pack(side="left", padx=5)
    
    def create_audio_controls(self, parent):
        """Create audio visualizer controls"""
        # Start/Stop animation
        self.audio_btn_text = tk.StringVar(value="▶ Start Animation")
        audio_btn = tk.Button(
            parent,
            textvariable=self.audio_btn_text,
            bg="#28a745",
            fg="white",
            font=("Arial", 12),
            command=self.toggle_audio_animation
        )
        audio_btn.pack(side="left", padx=10)
        
        # Preset buttons
        presets = [
            ("🎵 Bass Boost", self.apply_bass_boost),
            ("🎤 Vocal", self.apply_vocal_preset),
            ("🎸 Rock", self.apply_rock_preset),
            ("🌊 Reset", self.reset_equalizer)
        ]
        
        for text, command in presets:
            btn = tk.Button(
                parent,
                text=text,
                bg="#17a2b8",
                fg="white",
                font=("Arial", 10),
                command=command
            )
            btn.pack(side="left", padx=5)
    
    def create_color_presets(self, parent):
        """Create color preset buttons"""
        presets = [
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("Yellow", (255, 255, 0)),
            ("Magenta", (255, 0, 255)),
            ("Cyan", (0, 255, 255)),
            ("White", (255, 255, 255)),
            ("Black", (0, 0, 0))
        ]
        
        for name, (r, g, b) in presets:
            btn = tk.Button(
                parent,
                text=name,
                bg=f"#{r:02x}{g:02x}{b:02x}",
                fg="white" if r + g + b < 384 else "black",
                font=("Arial", 10),
                command=lambda r=r, g=g, b=b: self.apply_color_preset(r, g, b)
            )
            btn.pack(side="left", padx=5, pady=5)
    
    def create_control_panel(self):
        """Create bottom control panel"""
        control_frame = tk.Frame(self.root, bg="#e9ecef", height=80)
        control_frame.pack(fill="x", side="bottom")
        control_frame.pack_propagate(False)
        
        # Global controls
        controls_container = tk.Frame(control_frame, bg="#e9ecef")
        controls_container.pack(expand=True, fill="both", pady=10)
        
        # Stop all animations
        stop_btn = tk.Button(
            controls_container,
            text="⏹ Stop All Animations",
            bg="#dc3545",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.stop_all_animations
        )
        stop_btn.pack(side="left", padx=20)
        
        # Reset all sliders
        reset_btn = tk.Button(
            controls_container,
            text="🔄 Reset All Sliders",
            bg="#6c757d",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.reset_all_sliders
        )
        reset_btn.pack(side="left", padx=10)
        
        # Performance info
        self.global_info = tk.StringVar(value=f"Total Sliders: {len(self.all_sliders)}")
        info_label = tk.Label(
            controls_container,
            textvariable=self.global_info,
            font=("Arial", 10),
            bg="#e9ecef",
            fg="#495057"
        )
        info_label.pack(side="right", padx=20)
    
    # Callback methods
    def update_slider_display(self, slider, value_var):
        """Update slider value display"""
        try:
            if slider.config_slider.slider_type == SliderType.RANGE:
                start, end = slider.get_values()
                if slider.config_slider.value_formatter:
                    start_str = slider.config_slider.value_formatter(start)
                    end_str = slider.config_slider.value_formatter(end)
                    value_var.set(f"Range: {start_str} - {end_str}")
                else:
                    value_var.set(f"Range: {start:.{slider.config_slider.precision}f} - {end:.{slider.config_slider.precision}f}")
            else:
                value = slider.get_value()
                if slider.config_slider.value_formatter:
                    value_str = slider.config_slider.value_formatter(value)
                    value_var.set(f"Value: {value_str}")
                else:
                    value_var.set(f"Value: {value:.{slider.config_slider.precision}f}")
        except Exception as e:
            value_var.set(f"Error: {str(e)}")
    
    def update_range_slider_display(self, slider, value_var):
        """Update range slider display"""
        try:
            start, end = slider.get_values()
            if slider.config_slider.value_formatter:
                start_str = slider.config_slider.value_formatter(start)
                end_str = slider.config_slider.value_formatter(end)
            else:
                start_str = f"{start:.{slider.config_slider.precision}f}"
                end_str = f"{end:.{slider.config_slider.precision}f}"
            
            value_var.set(f"Range: {start_str} to {end_str} | Width: {end - start:.1f}")
        except Exception as e:
            value_var.set(f"Error: {str(e)}")
    
    def update_realtime_display(self, value):
        """Update real-time values display"""
        try:
            values = []
            for name, slider in self.all_sliders.items():
                if name.startswith(('master', 'slave')):
                    if slider.config_slider.slider_type == SliderType.RANGE:
                        start, end = slider.get_values()
                        values.append(f"{name}: ({start:.1f}, {end:.1f})")
                    else:
                        val = slider.get_value()
                        values.append(f"{name}: {val:.1f}")
            
            self.realtime_values.set(" | ".join(values))
            
            # Update slave sliders based on master
            if 'master' in self.all_sliders:
                master_value = self.all_sliders['master'].get_value()
                for i in range(3):
                    slave_key = f"slave_{i}"
                    if slave_key in self.all_sliders:
                        # Create some relationship between master and slaves
                        target = master_value * (0.5 + i * 0.25)
                        self.all_sliders[slave_key].set_value(target, animate=True)
        except Exception as e:
            self.realtime_values.set(f"Error: {str(e)}")
    
    def update_math_function(self, x_value):
        """Update mathematical function display"""
        try:
            result = math.sin(x_value)
            self.math_result.set(f"f(x) = sin({x_value:.3f}) = {result:.3f}")
        except Exception as e:
            self.math_result.set(f"Error: {str(e)}")
    
    def update_audio_band(self, band_index, value):
        """Update audio equalizer band"""
        self.audio_bands[band_index] = value
        # Here you would typically apply the EQ settings to audio processing
    
    def update_color_channel(self, channel, value):
        """Update color channel"""
        self.color_values[channel] = int(value)
        self.update_color_preview()
    
    def update_color_preview(self):
        """Update color preview display"""
        r, g, b = self.color_values['r'], self.color_values['g'], self.color_values['b']
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        self.color_preview.configure(bg=hex_color)
        self.color_info.set(f"RGB({r}, {g}, {b}) | {hex_color.upper()}")
    
    def validate_slider_value(self, value):
        """Validate slider value"""
        if 'validation' in self.all_sliders:
            slider = self.all_sliders['validation']
            is_valid = slider.validate_values()
            
            if is_valid:
                self.validation_status.set("✅ Valid")
                # Update status label appearance for valid state
            else:
                self.validation_status.set("❌ Invalid (20-80, multiple of 5)")
                # Update status label appearance for invalid state
    
    def track_performance(self, value):
        """Track performance metrics"""
        current_time = time.time()
        self.perf_updates += 1
        self.perf_times.append(current_time)
        
        # Keep only recent times (last 100 updates)
        if len(self.perf_times) > 100:
            self.perf_times = self.perf_times[-100:]
        
        # Calculate FPS and average time
        if len(self.perf_times) > 1:
            time_span = self.perf_times[-1] - self.perf_times[0]
            fps = len(self.perf_times) / time_span if time_span > 0 else 0
            avg_time = (time_span / len(self.perf_times)) * 1000  # ms
        else:
            fps = 0
            avg_time = 0
        
        self.perf_metrics.set(f"Updates: {self.perf_updates} | FPS: {fps:.1f} | Avg: {avg_time:.1f}ms")
    
    # Animation methods
    def animate_slider_to_value(self, target_value, duration):
        """Animate slider to specific value"""
        if 'animated' in self.all_sliders:
            self.all_sliders['animated'].set_value(target_value, animate=True)
    
    def animate_slider_bounce(self, target_value):
        """Animate with bounce effect"""
        # This would require custom animation implementation
        self.animate_slider_to_value(target_value, 0.6)
    
    def animate_slider_elastic(self, target_value):
        """Animate with elastic effect"""
        # This would require custom animation implementation
        self.animate_slider_to_value(target_value, 0.8)
    
    def animate_slider_random(self):
        """Animate to random value"""
        import random
        target = random.randint(0, 100)
        self.animate_slider_to_value(target, 0.5)
    
    def toggle_audio_animation(self):
        """Toggle audio visualizer animation"""
        self.audio_animation_active = not self.audio_animation_active
        
        if self.audio_animation_active:
            self.audio_btn_text.set("⏸ Stop Animation")
            self.start_audio_animation()
        else:
            self.audio_btn_text.set("▶ Start Animation")
    
    def start_audio_animation(self):
        """Start audio visualization animation"""
        if not self.audio_animation_active:
            return
        
        # Simulate audio data
        import random
        for i, slider in enumerate(self.eq_sliders):
            # Create some realistic audio movement
            current_value = slider.get_value()
            # Bass frequencies move more slowly
            if i < 3:
                change = random.uniform(-1, 1)
            # Mid frequencies are more active
            elif i < 7:
                change = random.uniform(-2, 2)
            # High frequencies are very active
            else:
                change = random.uniform(-3, 3)
            
            new_value = max(-12, min(12, current_value + change))
            slider.set_value(new_value, animate=True)
        
        # Schedule next update
        if self.audio_animation_active:
            self.root.after(100, self.start_audio_animation)
    
    def apply_bass_boost(self):
        """Apply bass boost EQ preset"""
        bass_values = [6, 4, 2, 0, -1, -1, 0, 1, 2, 3]
        for i, value in enumerate(bass_values):
            if i < len(self.eq_sliders):
                self.eq_sliders[i].set_value(value, animate=True)
    
    def apply_vocal_preset(self):
        """Apply vocal EQ preset"""
        vocal_values = [-2, -1, 0, 2, 4, 3, 2, 1, 0, -1]
        for i, value in enumerate(vocal_values):
            if i < len(self.eq_sliders):
                self.eq_sliders[i].set_value(value, animate=True)
    
    def apply_rock_preset(self):
        """Apply rock EQ preset"""
        rock_values = [3, 2, 1, -1, -2, 0, 2, 4, 5, 3]
        for i, value in enumerate(rock_values):
            if i < len(self.eq_sliders):
                self.eq_sliders[i].set_value(value, animate=True)
    
    def reset_equalizer(self):
        """Reset equalizer to flat"""
        for slider in self.eq_sliders:
            slider.set_value(0, animate=True)
    
    def apply_color_preset(self, r, g, b):
        """Apply color preset"""
        self.red_slider.set_value(r, animate=True)
        self.green_slider.set_value(g, animate=True)
        self.blue_slider.set_value(b, animate=True)
    
    def stop_all_animations(self):
        """Stop all animations"""
        for slider in self.all_sliders.values():
            slider.stop_all_animations()
        
        self.audio_animation_active = False
        self.audio_btn_text.set("▶ Start Animation")
    
    def reset_all_sliders(self):
        """Reset all sliders to default values"""
        for slider in self.all_sliders.values():
            slider.reset_to_defaults(animate=True)
    
    def start_background_animations(self):
        """Start background animations and updates"""
        self.update_global_info()
        self.root.after(1000, self.start_background_animations)
    
    def start_performance_monitoring(self):
        """Start performance monitoring"""
        # This runs continuously to update performance metrics
        pass
    
    def update_global_info(self):
        """Update global information display"""
        active_animations = sum(1 for slider in self.all_sliders.values() 
                              if slider.is_animating())
        self.global_info.set(f"Total Sliders: {len(self.all_sliders)} | Active Animations: {active_animations}")
    
    def run(self):
        """Start the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Handle application closing"""
        self.is_running = False
        self.audio_animation_active = False
        
        # Stop all animations
        self.stop_all_animations()
        
        # Clean up
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
        
        self.root.destroy()

def main():
    """Main entry point"""
    try:
        print("🎛️ Starting Advanced Sliders Demo...")
        app = AdvancedSlidersDemo()
        app.run()
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()