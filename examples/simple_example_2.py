#!/usr/bin/env python3
"""
simple_example_2.py - Advanced example with new widgets
"""

import tkinter as tk
import sys
import os

# Add library path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import tkinter as tk
import time
import threading
from animated_widgets_pack.ToggleButton import AnimatedToggle, ToggleStyle
from animated_widgets_pack.ProgressBar import AnimatedProgressBar, ProgressBarStyle
from animated_widgets_pack.ScrollView import AnimatedScrollView, ScrollViewStyle, ScrollBarStyle
from animated_widgets_pack.core import WidgetConfig
from animated_widgets_pack.buttons import AnimatedButton, ButtonStyle
from animated_widgets_pack.TextInput import AnimatedTextInput, TextInputStyle, TextInputType
from animated_widgets_pack.CheckBox import AnimatedCheckbox, CheckboxStyle

# في أعلى simple_example_2.py (قبل AdvancedDemo)

import colorsys

class ColorUtils:
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex string (#RRGGBB) to RGB tuple (0-255)."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb):
        """Convert RGB tuple (0-255) to hex string (#RRGGBB)."""
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    @staticmethod
    def darken_color(hex_color, factor=0.1):
        """Darken a hex color by a factor (0.1 = 10% darker)."""
        r, g, b = ColorUtils.hex_to_rgb(hex_color)
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return DarkenedColor((r, g, b))

class DarkenedColor:
    """Helper to allow .to_hex() calls after darken_color."""
    def __init__(self, rgb):
        self.rgb = rgb

    def to_hex(self):
        return ColorUtils.rgb_to_hex(self.rgb)


class AdvancedDemo:
    """Advanced demonstration of all animated widgets"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AnimatedWidgetsPack - Widgets Avancés")
        self.root.geometry("1200x800")
        self.root.configure(bg="#ecf0f1")
        
        # Center window
        self.center_window()
        
        # Current values for demo
        self.progress_value = 0
        self.toggle_states = {}
        
        self.create_widgets()
    
    def center_window(self):
        """Center window on screen"""
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
            text="🎨 AnimatedWidgetsPack - Widgets Avancés",
            font=("Arial", 18, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Create main scroll view
        self.create_scroll_demo()
        
        # Create control panel
        self.create_control_panel()
    
    def create_scroll_demo(self):
        """Create scrollable demo area"""
        # Configure scroll view
        scroll_config = WidgetConfig(width=800, height=500)
        scroll_style = ScrollViewStyle(
            background_color="#ffffff",
            border_color="#bdc3c7",
            border_width=2,
            border_radius=10,
            content_padding=20,
            momentum_enabled=True,
            elastic_enabled=True
        )
        
        scrollbar_style = ScrollBarStyle(
            auto_hide=True,
            track_color="#f8f9fa",
            thumb_color="#6c757d",
            thumb_hover_color="#495057"
        )
        
        # Create scroll view
        self.scroll_view = AnimatedScrollView(
            config=scroll_config,
            style=scroll_style,
            scrollbar_style=scrollbar_style
        )
        
        scroll_widget = self.scroll_view.render(self.root, "tkinter")
        scroll_widget.pack(pady=20)
        
        # Add content to scroll view
        self.populate_scroll_content()
    
    def populate_scroll_content(self):
        """Add content to the scroll view"""
        
        # Section 1: Toggle Switches
        self.create_toggle_section()
        
        # Section 2: Progress Bars
        self.create_progress_section()
        
        # Section 3: Advanced Buttons
        self.create_advanced_buttons_section()
        
        # Section 4: Interactive Elements
        self.create_interactive_section()
        
        # Add some spacing at the bottom
        spacer = tk.Frame(self.scroll_view._content_frame, height=100, bg="#ffffff")
        self.scroll_view.add_widget(spacer, fill="x", pady=20)
    
    def create_toggle_section(self):
        """Create toggle switches section"""
        # Section title
        section_frame = tk.Frame(self.scroll_view._content_frame, bg="#ffffff")
        self.scroll_view.add_widget(section_frame, fill="x", pady=10)
        
        title = tk.Label(
            section_frame,
            text="🔘 Commutateurs Animés",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        title.pack(anchor="w")
        
        # Toggle container
        toggle_frame = tk.Frame(self.scroll_view._content_frame, bg="#f8f9fa", relief="raised", bd=1)
        self.scroll_view.add_widget(toggle_frame, fill="x", pady=10, padx=20)
        
        # Create different toggle styles
        toggle_configs = [
            {
                'name': 'Mode Sombre',
                'style': ToggleStyle(
                    track_color_off="#95a5a6",
                    track_color_on="#2c3e50",
                    thumb_color_off="#ecf0f1",
                    thumb_color_on="#ffffff",
                    glow_enabled=True,
                    glow_color="#3498db"
                )
            },
            {
                'name': 'Notifications',
                'style': ToggleStyle(
                    track_color_off="#e74c3c",
                    track_color_on="#27ae60",
                    bounce_effect=True,
                    show_labels=True,
                    label_on="ON",
                    label_off="OFF"
                )
            },
            {
                'name': 'Synchronisation',
                'style': ToggleStyle(
                    track_color_off="#95a5a6",
                    track_color_on="#3498db",
                    track_width=80,
                    track_height=40,
                    thumb_size=35,
                    shadow_enabled=True
                )
            }
        ]
        
        for i, config in enumerate(toggle_configs):
            row_frame = tk.Frame(toggle_frame, bg="#f8f9fa")
            row_frame.pack(fill="x", pady=10, padx=20)
            
            # Label
            label = tk.Label(
                row_frame,
                text=config['name'],
                font=("Arial", 11),
                bg="#f8f9fa",
                fg="#2c3e50"
            )
            label.pack(side="left")
            
            # Toggle switch
            toggle = AnimatedToggle(
                initial_state=i % 2 == 0,  # Alternate initial states
                style=config['style']
            )
            
            toggle_widget = toggle.render(row_frame, "tkinter")
            toggle_widget.pack(side="right")
            
            # Store reference and bind callback
            self.toggle_states[config['name']] = toggle
            toggle.on_toggle(lambda state, name=config['name']: self.on_toggle_changed(name, state))
    
    def create_progress_section(self):
        """Create progress bars section"""
        # Section title
        section_frame = tk.Frame(self.scroll_view._content_frame, bg="#ffffff")
        self.scroll_view.add_widget(section_frame, fill="x", pady=10)
        
        title = tk.Label(
            section_frame,
            text="📊 Barres de Progression Animées",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        title.pack(anchor="w")
        
        # Progress container
        progress_frame = tk.Frame(self.scroll_view._content_frame, bg="#f8f9fa", relief="raised", bd=1)
        self.scroll_view.add_widget(progress_frame, fill="x", pady=10, padx=20)
        
        # Standard progress bar
        self.create_progress_bar(
            progress_frame,
            "Téléchargement",
            ProgressBarStyle(
                fill_color="#3498db",
                fill_gradient_enabled=True,
                fill_gradient_colors=["#3498db", "#2980b9"],
                pulse_enabled=True,
                show_text=True,
                text_format="{value}%"
            ),
            initial_value=65
        )
        
        # Striped progress bar
        self.create_progress_bar(
            progress_frame,
            "Installation",
            ProgressBarStyle(
                fill_color="#27ae60",
                stripes_enabled=True,
                stripe_color="#ffffff",
                stripe_opacity=0.3,
                show_text=True,
                text_format="Étape {value}/100"
            ),
            initial_value=45
        )
        
        # Gradient progress bar
        self.create_progress_bar(
            progress_frame,
            "Traitement",
            ProgressBarStyle(
                fill_gradient_enabled=True,
                fill_gradient_colors=["#e74c3c", "#f39c12", "#f1c40f", "#27ae60"],
                glow_enabled=True,
                glow_color="#f39c12",
                show_text=True,
                text_position="outside"
            ),
            initial_value=78
        )
        
        # Indeterminate progress bar
        indeterminate_frame = tk.Frame(progress_frame, bg="#f8f9fa")
        indeterminate_frame.pack(fill="x", pady=10, padx=20)
        
        ind_label = tk.Label(
            indeterminate_frame,
            text="Chargement...",
            font=("Arial", 11),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        ind_label.pack(anchor="w")
        
        ind_progress = AnimatedProgressBar(
            config=WidgetConfig(width=300, height=25),
            style=ProgressBarStyle(
                fill_color="#9b59b6",
                show_text=False,
                fill_animation_duration=0.3
            )
        )
        
        ind_widget = ind_progress.render(indeterminate_frame, "tkinter")
        ind_widget.pack(pady=5)
        
        # Set to indeterminate mode
        ind_progress.set_indeterminate(True)
        
        self.indeterminate_progress = ind_progress
    
    def create_progress_bar(self, parent, label_text, style, initial_value=0):
        """Helper to create a progress bar with label"""
        container = tk.Frame(parent, bg="#f8f9fa")
        container.pack(fill="x", pady=10, padx=20)
        
        # Label
        label = tk.Label(
            container,
            text=label_text,
            font=("Arial", 11),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        label.pack(anchor="w")
        
        # Progress bar
        progress = AnimatedProgressBar(
            initial_value=initial_value,
            min_value=0,
            max_value=100,
            config=WidgetConfig(width=400, height=25),
            style=style
        )
        
        progress_widget = progress.render(container, "tkinter")
        progress_widget.pack(pady=5)
        
        return progress
    
    def create_advanced_buttons_section(self):
        """Create advanced buttons section"""
        # Section title
        section_frame = tk.Frame(self.scroll_view._content_frame, bg="#ffffff")
        self.scroll_view.add_widget(section_frame, fill="x", pady=10)
        
        title = tk.Label(
            section_frame,
            text="🎛️ Boutons Avancés",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        title.pack(anchor="w")
        
        # Buttons container
        buttons_frame = tk.Frame(self.scroll_view._content_frame, bg="#f8f9fa", relief="raised", bd=1)
        self.scroll_view.add_widget(buttons_frame, fill="x", pady=10, padx=20)
        
        # Create button grid
        button_grid = tk.Frame(buttons_frame, bg="#f8f9fa")
        button_grid.pack(pady=20)
        
        # Row 1: Different styles
        row1 = tk.Frame(button_grid, bg="#f8f9fa")
        row1.pack(pady=10)
        
        # Gradient button
        gradient_btn = AnimatedButton(
            "Dégradé ✨",
            config=WidgetConfig(width=140, height=45, border_radius=15),
            style=ButtonStyle(
                normal_color="#667eea",
                hover_color="#764ba2",
                pressed_color="#5a4fcf",
                hover_lift=5.0,
                click_scale=0.9
            )
        )
        gradient_widget = gradient_btn.render(row1, "tkinter")
        gradient_widget.pack(side="left", padx=10)
        gradient_btn.on_click(lambda: gradient_btn.pulse_animation(1.0, 1.3))
        
        # Neon button
        neon_btn = AnimatedButton(
            "Néon 💡",
            config=WidgetConfig(width=140, height=45, border_radius=15),
            style=ButtonStyle(
                normal_color="#ff006e",
                hover_color="#ff1188",
                pressed_color="#cc0057",
                hover_lift=3.0
            )
        )
        neon_widget = neon_btn.render(row1, "tkinter")
        neon_widget.pack(side="left", padx=10)
        neon_btn.on_click(lambda: neon_btn.flash_animation("#ffffff", 0.5))
        
        # Glass button
        glass_btn = AnimatedButton(
            "Verre 🪟",
            config=WidgetConfig(width=140, height=45, border_radius=15),
            style=ButtonStyle(
                normal_color="#ffffff",
                hover_color="#f8f9fa",
                pressed_color="#e9ecef",
                hover_lift=2.0
            )
        )
        glass_widget = glass_btn.render(row1, "tkinter")
        glass_widget.pack(side="left", padx=10)
        glass_btn.on_click(lambda: glass_btn.bounce_animation(0.6))
        
        # Row 2: Action buttons
        row2 = tk.Frame(button_grid, bg="#f8f9fa")
        row2.pack(pady=10)
        
        # Download button
        download_btn = AnimatedButton(
            "Télécharger 📥",
            config=WidgetConfig(width=160, height=50),
            style=ButtonStyle(
                normal_color="#28a745",
                hover_color="#218838",
                pressed_color="#1e7e34"
            )
        )
        download_widget = download_btn.render(row2, "tkinter")
        download_widget.pack(side="left", padx=10)
        download_btn.on_click(lambda: self.simulate_download())
        
        # Settings button
        settings_btn = AnimatedButton(
            "Paramètres ⚙️",
            config=WidgetConfig(width=160, height=50),
            style=ButtonStyle(
                normal_color="#6c757d",
                hover_color="#5a6268",
                pressed_color="#545b62"
            )
        )
        settings_widget = settings_btn.render(row2, "tkinter")
        settings_widget.pack(side="left", padx=10)
        settings_btn.on_click(lambda: self.show_settings())
        
        self.download_btn = download_btn
        self.settings_btn = settings_btn
    
    def create_interactive_section(self):
        """Create interactive demo section"""
        # Section title
        section_frame = tk.Frame(self.scroll_view._content_frame, bg="#ffffff")
        self.scroll_view.add_widget(section_frame, fill="x", pady=10)
        
        title = tk.Label(
            section_frame,
            text="🎮 Éléments Interactifs",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        title.pack(anchor="w")
        
        # Interactive container
        interactive_frame = tk.Frame(self.scroll_view._content_frame, bg="#f8f9fa", relief="raised", bd=1)
        self.scroll_view.add_widget(interactive_frame, fill="x", pady=10, padx=20)
        
        # Create color palette demo
        self.create_color_palette_demo(interactive_frame)
        
        # Create animation demo
        self.create_animation_demo(interactive_frame)
    
    def create_color_palette_demo(self, parent):
        """Create color palette demonstration"""
        palette_frame = tk.Frame(parent, bg="#f8f9fa")
        palette_frame.pack(fill="x", pady=15, padx=20)
        
        palette_label = tk.Label(
            palette_frame,
            text="Palette de Couleurs Interactive",
            font=("Arial", 12, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        palette_label.pack(anchor="w", pady=(0, 10))
        
        # Color buttons
        colors_frame = tk.Frame(palette_frame, bg="#f8f9fa")
        colors_frame.pack()
        
        colors = [
            ("#e74c3c", "Rouge"),
            ("#3498db", "Bleu"),
            ("#2ecc71", "Vert"),
            ("#f39c12", "Orange"),
            ("#9b59b6", "Violet"),
            ("#1abc9c", "Turquoise")
        ]
        
        self.color_buttons = []
        
        for i, (color, name) in enumerate(colors):
            color_btn = AnimatedButton(
                name,
                config=WidgetConfig(width=100, height=35, border_radius=8),
                style=ButtonStyle(
                    normal_color=color,
                    hover_color=ColorUtils.darken_color(color, 0.1).to_hex(),
                    pressed_color=ColorUtils.darken_color(color, 0.2).to_hex(),
                    hover_lift=3.0
                )
            )
            
            color_widget = color_btn.render(colors_frame, "tkinter")
            color_widget.grid(row=i//3, column=i%3, padx=5, pady=5)
            
            color_btn.on_click(lambda c=color: self.change_theme_color(c))
            self.color_buttons.append(color_btn)
    
    def create_animation_demo(self, parent):
        """Create animation demonstration"""
        anim_frame = tk.Frame(parent, bg="#f8f9fa")
        anim_frame.pack(fill="x", pady=15, padx=20)
        
        anim_label = tk.Label(
            anim_frame,
            text="Démonstration d'Animations",
            font=("Arial", 12, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        anim_label.pack(anchor="w", pady=(0, 10))
        
        # Animation control buttons
        anim_controls = tk.Frame(anim_frame, bg="#f8f9fa")
        anim_controls.pack()
        
        animations = [
            ("Impulsion", self.demo_pulse),
            ("Secousse", self.demo_shake),
            ("Flash", self.demo_flash),
            ("Rebond", self.demo_bounce)
        ]
        
        for name, callback in animations:
            anim_btn = AnimatedButton(
                name,
                config=WidgetConfig(width=120, height=35),
                style=ButtonStyle(
                    normal_color="#34495e",
                    hover_color="#2c3e50",
                    pressed_color="#1b2631"
                )
            )
            
            anim_widget = anim_btn.render(anim_controls, "tkinter")
            anim_widget.pack(side="left", padx=5)
            
            anim_btn.on_click(callback)
    
    def create_control_panel(self):
        """Create control panel at bottom"""
        control_frame = tk.Frame(self.root, bg="#34495e", height=80)
        control_frame.pack(fill="x", side="bottom")
        control_frame.pack_propagate(False)
        
        # Control buttons
        controls_container = tk.Frame(control_frame, bg="#34495e")
        controls_container.pack(expand=True)
        
        # Reset button
        reset_btn = AnimatedButton(
            "🔄 Réinitialiser",
            config=WidgetConfig(width=140, height=40),
            style=ButtonStyle(
                normal_color="#e67e22",
                hover_color="#d35400",
                pressed_color="#a04000"
            )
        )
        reset_widget = reset_btn.render(controls_container, "tkinter")
        reset_widget.pack(side="left", padx=10, pady=20)
        reset_btn.on_click(self.reset_demo)
        
        # Progress control
        progress_control = tk.Frame(controls_container, bg="#34495e")
        progress_control.pack(side="left", padx=20, pady=20)
        
        progress_label = tk.Label(
            progress_control,
            text="Contrôle du Progrès:",
            font=("Arial", 10),
            bg="#34495e",
            fg="#ecf0f1"
        )
        progress_label.pack()
        
        progress_buttons = tk.Frame(progress_control, bg="#34495e")
        progress_buttons.pack()
        
        # Progress increment buttons
        for label, increment in [("-10", -10), ("+10", 10), ("+25", 25), ("Complete", 100)]:
            btn = AnimatedButton(
                label,
                config=WidgetConfig(width=60, height=30),
                style=ButtonStyle(
                    normal_color="#3498db",
                    hover_color="#2980b9",
                    pressed_color="#21618c"
                )
            )
            btn_widget = btn.render(progress_buttons, "tkinter")
            btn_widget.pack(side="left", padx=2)
            
            if label == "Complete":
                btn.on_click(lambda: self.set_all_progress(100))
            else:
                btn.on_click(lambda inc=increment: self.increment_progress(inc))
        
        # Status display
        self.status_label = tk.Label(
            controls_container,
            text="Prêt",
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="#ecf0f1"
        )
        self.status_label.pack(side="right", padx=20, pady=20)
    
    def on_toggle_changed(self, name, state):
        """Handle toggle state changes"""
        status = "ON" if state else "OFF"
        self.update_status(f"{name}: {status}")
        
        # Special actions for certain toggles
        if name == "Mode Sombre" and state:
            self.apply_dark_theme()
        elif name == "Mode Sombre" and not state:
            self.apply_light_theme()
    
    def simulate_download(self):
        """Simulate download progress"""
        self.update_status("Téléchargement en cours...")
        
        # Animate download button
        self.download_btn.flash_animation("#27ae60", 0.3)
        
        # Update progress (this would be replaced with real download logic)
        self.increment_progress(15)
        
        # Simulate completion after delay
        self.root.after(2000, lambda: self.update_status("Téléchargement terminé!"))
    
    def show_settings(self):
        """Show settings dialog"""
        self.update_status("Ouverture des paramètres...")
        self.settings_btn.pulse_animation(0.8, 1.2)
        
        # In a real app, this would open a settings dialog
        self.root.after(1000, lambda: self.update_status("Paramètres mis à jour"))
    
    def change_theme_color(self, color):
        """Change theme color"""
        self.update_status(f"Couleur du thème changée: {color}")
        
        # Update download button color
        self.download_btn.set_colors(normal=color)
        
        # Animate color buttons
        for btn in self.color_buttons:
            btn.flash_animation("#ffffff", 0.2)
    
    def demo_pulse(self):
        """Demonstrate pulse animation"""
        self.update_status("Animation d'impulsion...")
        for btn in self.color_buttons[:3]:
            btn.pulse_animation(1.2, 1.4)
    
    def demo_shake(self):
        """Demonstrate shake animation"""
        self.update_status("Animation de secousse...")
        for btn in self.color_buttons[3:]:
            btn.shake_animation(0.5, 5.0)
    
    def demo_flash(self):
        """Demonstrate flash animation"""
        self.update_status("Animation de flash...")
        for btn in self.color_buttons:
            btn.flash_animation("#ffffff", 0.4)
    
    def demo_bounce(self):
        """Demonstrate bounce animation"""
        self.update_status("Animation de rebond...")
        self.download_btn.bounce_animation(0.8)
        self.settings_btn.bounce_animation(0.8)
    
    def increment_progress(self, amount):
        """Increment all progress bars"""
        self.progress_value = max(0, min(100, self.progress_value + amount))
        self.update_status(f"Progrès: {self.progress_value}%")
        
        # Update progress bars (in a real implementation, 
        # you'd store references to all progress bars)
    
    def set_all_progress(self, value):
        """Set all progress bars to specific value"""
        self.progress_value = value
        self.update_status(f"Progrès défini à: {value}%")
    
    def apply_dark_theme(self):
        """Apply dark theme"""
        self.update_status("Thème sombre appliqué")
        # In a real app, this would change all widget colors
    
    def apply_light_theme(self):
        """Apply light theme"""
        self.update_status("Thème clair appliqué")
        # In a real app, this would change all widget colors
    
    def reset_demo(self):
        """Reset all demo elements"""
        self.update_status("Démonstration réinitialisée")
        
        # Reset toggles
        for toggle in self.toggle_states.values():
            toggle.set_value(False, animate=True)
        
        # Reset progress
        self.progress_value = 0
        
        # Flash reset button
        self.root.after(100, lambda: self.update_status("Prêt"))
    
    def update_status(self, message):
        """Update status display"""
        self.status_label.configure(text=message)
        print(f"[STATUS] {message}")  # Also log to console
    
    def run(self):
        """Start the application"""
        self.update_status("Application démarrée - Explorez les widgets!")
        
        # Add some demo content to showcase scrolling
        self.add_demo_content()
        
        self.root.mainloop()
    
    def add_demo_content(self):
        """Add additional demo content for scrolling"""
        # Add some cards to demonstrate scrolling
        for i in range(5):
            card_frame = tk.Frame(
                self.scroll_view._content_frame, 
                bg="#ffffff", 
                relief="raised", 
                bd=1
            )
            self.scroll_view.add_widget(card_frame, fill="x", pady=10, padx=20)
            
            card_title = tk.Label(
                card_frame,
                text=f"📋 Carte de Démonstration #{i+1}",
                font=("Arial", 12, "bold"),
                bg="#ffffff",
                fg="#2c3e50"
            )
            card_title.pack(pady=10)
            
            card_content = tk.Label(
                card_frame,
                text=f"Ceci est le contenu de la carte {i+1}. "
                     f"Cette section démontre les capacités de défilement "
                     f"du ScrollView animé avec des barres de défilement personnalisées.",
                font=("Arial", 10),
                bg="#ffffff",
                fg="#7f8c8d",
                wraplength=700,
                justify="left"
            )
            card_content.pack(pady=(0, 15), padx=20)
            
            # Add some interactive elements to each card
            card_buttons = tk.Frame(card_frame, bg="#ffffff")
            card_buttons.pack(pady=(0, 15))
            
            for j, (btn_text, btn_color) in enumerate([
                ("Action", "#3498db"),
                ("Info", "#2ecc71"), 
                ("Alerte", "#e74c3c")
            ]):
                card_btn = AnimatedButton(
                    btn_text,
                    config=WidgetConfig(width=80, height=30),
                    style=ButtonStyle(
                        normal_color=btn_color,
                        hover_color=ColorUtils.darken_color(btn_color, 0.1).to_hex(),
                        pressed_color=ColorUtils.darken_color(btn_color, 0.2).to_hex()
                    )
                )
                
                card_btn_widget = card_btn.render(card_buttons, "tkinter")
                card_btn_widget.pack(side="left", padx=5)
                
                card_btn.on_click(
                    lambda t=btn_text, c=i+1: self.update_status(f"Carte {c}: {t} cliqué")
                )

def main():
    """Main entry point"""
    try:
        print("🚀 Démarrage de la démonstration avancée...")
        app = AdvancedDemo()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Démonstration arrêtée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()