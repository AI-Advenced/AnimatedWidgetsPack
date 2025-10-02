# examples/complete_demo_2.py
"""
Démonstration complète avec tous les nouveaux widgets
ToggleButton, ProgressBar, ScrollView
"""

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

class CompleteDemo2:
    """Démonstration complète des nouveaux widgets"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AnimatedWidgetsPack - Demo 2 : Nouveaux Widgets")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f6fa")
        
        # Variables de contrôle
        self.progress_value = 0
        self.is_progress_running = False
        self.progress_thread = None
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_ui()
    
    def center_window(self):
        """Centrer la fenêtre"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
    
    def create_ui(self):
        """Créer l'interface utilisateur"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2f3542", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_title = tk.Label(
            header_frame,
            text="🎛️ AnimatedWidgetsPack - Nouveaux Widgets",
            font=("Arial", 18, "bold"),
            bg="#2f3542",
            fg="white"
        )
        header_title.pack(side="left", padx=20, pady=20)
        
        # Main container with notebook-style tabs (simplified)
        main_frame = tk.Frame(self.root, bg="#f5f6fa")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tab buttons
        tab_frame = tk.Frame(main_frame, bg="#f5f6fa")
        tab_frame.pack(fill="x", pady=(0, 20))
        
        self.current_tab = "toggle"
        self.tab_frames = {}
        
        # Tab buttons
        self.create_tab_button(tab_frame, "Toggle Buttons", "toggle")
        self.create_tab_button(tab_frame, "Progress Bars", "progress")
        self.create_tab_button(tab_frame, "Scroll Views", "scroll")
        self.create_tab_button(tab_frame, "Combinations", "combo")
        
        # Content area
        self.content_frame = tk.Frame(main_frame, bg="#ffffff", relief="solid", bd=1)
        self.content_frame.pack(fill="both", expand=True)
        
        # Create all tab content
        self.create_toggle_tab()
        self.create_progress_tab()
        self.create_scroll_tab()
        self.create_combo_tab()
        
        # Show initial tab
        self.show_tab("toggle")
    
    def create_tab_button(self, parent, text, tab_id):
        """Créer un bouton d'onglet"""
        btn = AnimatedButton(
            text,
            config=WidgetConfig(width=150, height=35),
            style=ButtonStyle(
                normal_color="#ddd6fe" if tab_id == self.current_tab else "#e2e8f0",
                hover_color="#c4b5fd",
                pressed_color="#a78bfa"
            )
        )
        btn.on_click(lambda: self.show_tab(tab_id))
        btn.render(parent, "tkinter").pack(side="left", padx=5)
        
        # Store reference for styling updates
        setattr(self, f"{tab_id}_tab_btn", btn)
    
    def show_tab(self, tab_id):
        """Afficher un onglet spécifique"""
        # Hide all tabs
        for frame in self.tab_frames.values():
            frame.pack_forget()
        
        # Show selected tab
        if tab_id in self.tab_frames:
            self.tab_frames[tab_id].pack(fill="both", expand=True, padx=20, pady=20)
        
        # Update tab button colors
        tabs = ["toggle", "progress", "scroll", "combo"]
        for tab in tabs:
            btn = getattr(self, f"{tab}_tab_btn", None)
            if btn:
                if tab == tab_id:
                    btn.set_colors(normal="#ddd6fe")
                else:
                    btn.set_colors(normal="#e2e8f0")
        
        self.current_tab = tab_id
    
    def create_toggle_tab(self):
        """Créer l'onglet des toggle buttons"""
        frame = tk.Frame(self.content_frame, bg="#ffffff")
        self.tab_frames["toggle"] = frame
        
        # Title
        title = tk.Label(
            frame,
            text="🔘 Toggle Buttons & Switches",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2d3748"
        )
        title.pack(pady=(0, 20))
        
        # Basic toggles section
        basic_frame = tk.LabelFrame(frame, text="Toggles Basiques", padx=20, pady=15, bg="#ffffff")
        basic_frame.pack(fill="x", pady=10)
        
        toggles_row1 = tk.Frame(basic_frame, bg="#ffffff")
        toggles_row1.pack(fill="x", pady=10)
        
        # Standard toggle
        self.toggle1 = AnimatedToggle(
            initial_state=False,
            style=ToggleStyle(
                track_color_off="#cbd5e0",
                track_color_on="#48bb78",
                thumb_color_off="#ffffff",
                thumb_color_on="#ffffff",
                track_width=60,
                track_height=30
            )
        )
        toggle1_widget = self.toggle1.render(toggles_row1, "tkinter")
        toggle1_widget.pack(side="left", padx=20)
        
        toggle1_label = tk.Label(toggles_row1, text="Toggle Standard", bg="#ffffff")
        toggle1_label.pack(side="left", padx=(5, 40))
        
        # Colored toggle
        self.toggle2 = AnimatedToggle(
            initial_state=True,
            style=ToggleStyle(
                track_color_off="#fed7d7",
                track_color_on="#f56565",
                thumb_color_off="#ffffff",
                thumb_color_on="#ffffff",
                track_width=80,
                track_height=35
            )
        )
        toggle2_widget = self.toggle2.render(toggles_row1, "tkinter")
        toggle2_widget.pack(side="left", padx=20)
        
        toggle2_label = tk.Label(toggles_row1, text="Toggle Coloré", bg="#ffffff")
        toggle2_label.pack(side="left", padx=(5, 40))
        
        # Advanced toggles section
        advanced_frame = tk.LabelFrame(frame, text="Toggles Avancés", padx=20, pady=15, bg="#ffffff")
        advanced_frame.pack(fill="x", pady=10)
        
        toggles_row2 = tk.Frame(advanced_frame, bg="#ffffff")
        toggles_row2.pack(fill="x", pady=10)
        
        # Toggle with glow
        self.toggle3 = AnimatedToggle(
            initial_state=False,
            style=ToggleStyle(
                track_color_off="#e2e8f0",
                track_color_on="#667eea",
                glow_enabled=True,
                glow_color="#667eea",
                glow_size=8,
                track_width=70,
                track_height=32
            )
        )
        toggle3_widget = self.toggle3.render(toggles_row2, "tkinter")
        toggle3_widget.pack(side="left", padx=20)
        
        toggle3_label = tk.Label(toggles_row2, text="Toggle avec Glow", bg="#ffffff")
        toggle3_label.pack(side="left", padx=(5, 40))
        
        # Toggle with labels
        self.toggle4 = AnimatedToggle(
            initial_state=False,
            style=ToggleStyle(
                track_color_off="#fbb6ce",
                track_color_on="#f687b3",
                label_on="ON",
                label_off="OFF",
                show_labels=True,
                track_width=90,
                track_height=35
            )
        )
        toggle4_widget = self.toggle4.render(toggles_row2, "tkinter")
        toggle4_widget.pack(side="left", padx=20)
        
        toggle4_label = tk.Label(toggles_row2, text="Toggle avec Labels", bg="#ffffff")
        toggle4_label.pack(side="left", padx=(5, 40))
        
        # Control buttons
        control_frame = tk.Frame(advanced_frame, bg="#ffffff")
        control_frame.pack(fill="x", pady=20)
        
        # Animation controls
        pulse_btn = AnimatedButton(
            "Pulse Animation",
            config=WidgetConfig(width=140, height=35),
            style=ButtonStyle(normal_color="#805ad5", hover_color="#6b46c1")
        )
        pulse_btn.on_click(self.trigger_toggle_pulse)
        pulse_btn.render(control_frame, "tkinter").pack(side="left", padx=10)
        
        flash_btn = AnimatedButton(
            "Flash Animation",
            config=WidgetConfig(width=140, height=35),
            style=ButtonStyle(normal_color="#38b2ac", hover_color="#319795")
        )
        flash_btn.on_click(self.trigger_toggle_flash)
        flash_btn.render(control_frame, "tkinter").pack(side="left", padx=10)
        
        shake_btn = AnimatedButton(
            "Shake Animation",
            config=WidgetConfig(width=140, height=35),
            style=ButtonStyle(normal_color="#ed8936", hover_color="#dd6b20")
        )
        shake_btn.on_click(self.trigger_toggle_shake)
        shake_btn.render(control_frame, "tkinter").pack(side="left", padx=10)
        
        # Status display
        self.toggle_status = tk.Text(frame, height=6, bg="#f7fafc", relief="solid", bd=1)
        self.toggle_status.pack(fill="x", pady=20)
        self.toggle_status.insert("1.0", "État des toggles:\n")
        
        # Bind callbacks
        self.toggle1.on_toggle(lambda state: self.update_toggle_status(1, state))
        self.toggle2.on_toggle(lambda state: self.update_toggle_status(2, state))
        self.toggle3.on_toggle(lambda state: self.update_toggle_status(3, state))
        self.toggle4.on_toggle(lambda state: self.update_toggle_status(4, state))
    
    def create_progress_tab(self):
        """Créer l'onglet des barres de progression"""
        frame = tk.Frame(self.content_frame, bg="#ffffff")
        self.tab_frames["progress"] = frame
        
        # Title
        title = tk.Label(
            frame,
            text="📊 Barres de Progression",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2d3748"
        )
        title.pack(pady=(0, 20))
        
        # Basic progress bars
        basic_frame = tk.LabelFrame(frame, text="Barres Basiques", padx=20, pady=15, bg="#ffffff")
        basic_frame.pack(fill="x", pady=10)
        
        # Standard progress bar
        progress_row1 = tk.Frame(basic_frame, bg="#ffffff")
        progress_row1.pack(fill="x", pady=10)
        
        tk.Label(progress_row1, text="Standard:", bg="#ffffff").pack(anchor="w")
        self.progress1 = AnimatedProgressBar(
            initial_value=65,
            config=WidgetConfig(width=350, height=25),
            style=ProgressBarStyle(
                background_color="#e2e8f0",
                fill_color="#48bb78"
            )
        )
        self.progress1.render(progress_row1, "tkinter").pack(anchor="w", pady=5)
        
        # Gradient progress bar
        progress_row2 = tk.Frame(basic_frame, bg="#ffffff")
        progress_row2.pack(fill="x", pady=10)
        
        tk.Label(progress_row2, text="Dégradé:", bg="#ffffff").pack(anchor="w")
        self.progress2 = AnimatedProgressBar(
            initial_value=40,
            config=WidgetConfig(width=350, height=25),
            style=ProgressBarStyle(
                fill_gradient_enabled=True,
                fill_gradient_colors=["#667eea", "#764ba2"],
                background_color="#f7fafc"
            )
        )
        self.progress2.render(progress_row2, "tkinter").pack(anchor="w", pady=5)
        
        # Advanced progress bars
        advanced_frame = tk.LabelFrame(frame, text="Barres Avancées", padx=20, pady=15, bg="#ffffff")
        advanced_frame.pack(fill="x", pady=10)
        
        # Striped progress bar
        progress_row3 = tk.Frame(advanced_frame, bg="#ffffff")
        progress_row3.pack(fill="x", pady=10)
        
        tk.Label(progress_row3, text="Rayures animées:", bg="#ffffff").pack(anchor="w")
        self.progress3 = AnimatedProgressBar(
            initial_value=80,
            config=WidgetConfig(width=350, height=30),
            style=ProgressBarStyle(
                fill_color="#f56565",
                stripes_enabled=True,
                stripe_color="#ffffff",
                stripe_opacity=0.3
            )
        )
        self.progress3.render(progress_row3, "tkinter").pack(anchor="w", pady=5)
        
        # Pulse progress bar
        progress_row4 = tk.Frame(advanced_frame, bg="#ffffff")
        progress_row4.pack(fill="x", pady=10)
        
        tk.Label(progress_row4, text="Avec pulse:", bg="#ffffff").pack(anchor="w")
        self.progress4 = AnimatedProgressBar(
            initial_value=55,
            config=WidgetConfig(width=350, height=25),
            style=ProgressBarStyle(
                fill_color="#9f7aea",
                pulse_enabled=True,
                pulse_color="#ffffff",
                pulse_opacity=0.4
            )
        )
        self.progress4.render(progress_row4, "tkinter").pack(anchor="w", pady=5)
        
        # Indeterminate progress bar
        progress_row5 = tk.Frame(advanced_frame, bg="#ffffff")
        progress_row5.pack(fill="x", pady=10)
        
        tk.Label(progress_row5, text="Indéterminée:", bg="#ffffff").pack(anchor="w")
        self.progress5 = AnimatedProgressBar(
            config=WidgetConfig(width=350, height=25),
            style=ProgressBarStyle(
                fill_color="#38b2ac",
                background_color="#e2e8f0"
            )
        )
        self.progress5.set_indeterminate(True)
        self.progress5.render(progress_row5, "tkinter").pack(anchor="w", pady=5)
        
        # Controls
        control_frame = tk.Frame(advanced_frame, bg="#ffffff")
        control_frame.pack(fill="x", pady=20)
        
        # Progress control buttons
        start_btn = AnimatedButton(
            "Démarrer Simulation",
            config=WidgetConfig(width=150, height=35),
            style=ButtonStyle(normal_color="#48bb78", hover_color="#38a169")
        )
        start_btn.on_click(self.start_progress_simulation)
        start_btn.render(control_frame, "tkinter").pack(side="left", padx=5)
        
        stop_btn = AnimatedButton(
            "Arrêter",
            config=WidgetConfig(width=100, height=35),
            style=ButtonStyle(normal_color="#f56565", hover_color="#e53e3e")  
        )
        stop_btn.on_click(self.stop_progress_simulation)
        stop_btn.render(control_frame, "tkinter").pack(side="left", padx=5)
        
        reset_btn = AnimatedButton(
            "Reset",
            config=WidgetConfig(width=100, height=35),
            style=ButtonStyle(normal_color="#a0aec0", hover_color="#718096")
        )
        reset_btn.on_click(self.reset_progress)
        reset_btn.render(control_frame, "tkinter").pack(side="left", padx=5)
        
        flash_progress_btn = AnimatedButton(
            "Flash Effect",
            config=WidgetConfig(width=120, height=35),
            style=ButtonStyle(normal_color="#ed8936", hover_color="#dd6b20")
        )
        flash_progress_btn.on_click(self.flash_progress)
        flash_progress_btn.render(control_frame, "tkinter").pack(side="left", padx=5)
        
        # Progress status
        self.progress_status = tk.Label(
            frame,
            text="Progression: 0% - Prêt",
            bg="#ffffff",
            font=("Arial", 12),
            fg="#4a5568"
        )
        self.progress_status.pack(pady=10)
    
    def create_scroll_tab(self):
        """Créer l'onglet des vues défilantes"""
        frame = tk.Frame(self.content_frame, bg="#ffffff")
        self.tab_frames["scroll"] = frame
        
        # Title
        title = tk.Label(
            frame,
            text="📜 Vues Défilantes",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2d3748"
        )
        title.pack(pady=(0, 20))
        
        # Scroll view demo
        scroll_demo_frame = tk.LabelFrame(frame, text="ScrollView avec contenu dynamique", 
                                        padx=20, pady=15, bg="#ffffff")
        scroll_demo_frame.pack(fill="both", expand=True, pady=10)
        
        # Create scroll view
        self.scroll_view = AnimatedScrollView(
            config=WidgetConfig(width=400, height=300),
            style=ScrollViewStyle(
                background_color="#f7fafc",
                border_color="#e2e8f0",
                content_padding=15,
                momentum_enabled=True,
                elastic_enabled=True
            ),
            scrollbar_style=ScrollBarStyle(
                auto_hide=True,
                thumb_color="#a0aec0",
                thumb_hover_color="#718096"
            )
        )
        
        scroll_container = tk.Frame(scroll_demo_frame, bg="#ffffff")
        scroll_container.pack(side="left", fill="both", expand=True)
        
        scroll_widget = self.scroll_view.render(scroll_container, "tkinter")
        scroll_widget.pack(side="left", padx=20, pady=10)
        
        # Populate scroll view with content
        self.populate_scroll_view()
        
        # Scroll controls
        scroll_controls = tk.Frame(scroll_demo_frame, bg="#ffffff")
        scroll_controls.pack(side="right", fill="y", padx=20)
        
        tk.Label(scroll_controls, text="Contrôles de défilement:", 
                bg="#ffffff", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Scroll buttons
        scroll_top_btn = AnimatedButton(
            "↑ Haut",
            config=WidgetConfig(width=120, height=30),
            style=ButtonStyle(normal_color="#4299e1", hover_color="#3182ce")
        )
        scroll_top_btn.on_click(lambda: self.scroll_view.scroll_to(0, 0))
        scroll_top_btn.render(scroll_controls, "tkinter").pack(pady=5)
        
        scroll_middle_btn = AnimatedButton(
            "◉ Milieu",
            config=WidgetConfig(width=120, height=30),
            style=ButtonStyle(normal_color="#48bb78", hover_color="#38a169")
        )
        scroll_middle_btn.on_click(self.scroll_to_middle)
        scroll_middle_btn.render(scroll_controls, "tkinter").pack(pady=5)
        
        scroll_bottom_btn = AnimatedButton(
            "↓ Bas",
            config=WidgetConfig(width=120, height=30),
            style=ButtonStyle(normal_color="#ed8936", hover_color="#dd6b20")
        )
        scroll_bottom_btn.on_click(self.scroll_to_bottom)
        scroll_bottom_btn.render(scroll_controls, "tkinter").pack(pady=5)
        
        # Add content button
        add_content_btn = AnimatedButton(
            "➕ Ajouter Contenu",
            config=WidgetConfig(width=120, height=30),
            style=ButtonStyle(normal_color="#9f7aea", hover_color="#805ad5")
        )
        add_content_btn.on_click(self.add_scroll_content)
        add_content_btn.render(scroll_controls, "tkinter").pack(pady=15)
        
        # Clear content button
        clear_content_btn = AnimatedButton(
            "🗑️ Vider",
            config=WidgetConfig(width=120, height=30),
            style=ButtonStyle(normal_color="#f56565", hover_color="#e53e3e")
        )
        clear_content_btn.on_click(self.clear_scroll_content)
        clear_content_btn.render(scroll_controls, "tkinter").pack(pady=5)
        
        # Scroll info
        self.scroll_info = tk.Label(
            scroll_controls,
            text="Position: (0, 0)\nTaille: (0, 0)",
            bg="#ffffff",
            font=("Arial", 10),
            fg="#4a5568",
            justify="left"
        )
        self.scroll_info.pack(pady=20, anchor="w")
        
        # Update scroll info periodically
        self.update_scroll_info()
    
    def create_combo_tab(self):
        """Créer l'onglet des combinaisons"""
        frame = tk.Frame(self.content_frame, bg="#ffffff")
        self.tab_frames["combo"] = frame
        
        # Title
        title = tk.Label(
            frame,
            text="🎯 Combinaisons & Exemples Pratiques",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#2d3748"
        )
        title.pack(pady=(0, 20))
        
        # Settings panel example
        settings_frame = tk.LabelFrame(frame, text="Panneau de Paramètres", 
                                     padx=20, pady=15, bg="#ffffff")
        settings_frame.pack(fill="x", pady=10)
        
        # Create a scroll view for settings
        settings_scroll = AnimatedScrollView(
            config=WidgetConfig(width=500, height=200),
            style=ScrollViewStyle(background_color="#fafafa")
        )
        settings_scroll_widget = settings_scroll.render(settings_frame, "tkinter")
        settings_scroll_widget.pack(side="left")
        
        # Add various settings
        self.create_settings_content(settings_scroll)
        
        # Control panel
        control_panel = tk.Frame(settings_frame, bg="#ffffff")
        control_panel.pack(side="right", fill="y", padx=20)
        
        tk.Label(control_panel, text="Actions:", bg="#ffffff", 
                font=("Arial", 12, "bold")).pack(anchor="w")
        
        save_btn = AnimatedButton(
            "💾 Sauvegarder",
            config=WidgetConfig(width=130, height=35),
            style=ButtonStyle(normal_color="#48bb78", hover_color="#38a169")
        )
        save_btn.on_click(self.save_settings)
        save_btn.render(control_panel, "tkinter").pack(pady=5)
        
        load_btn = AnimatedButton(
            "📂 Charger",
            config=WidgetConfig(width=130, height=35),
            style=ButtonStyle(normal_color="#4299e1", hover_color="#3182ce")
        )
        load_btn.on_click(self.load_settings)
        load_btn.render(control_panel, "tkinter").pack(pady=5)
        
        reset_settings_btn = AnimatedButton(
            "🔄 Reset",
            config=WidgetConfig(width=130, height=35),
            style=ButtonStyle(normal_color="#a0aec0", hover_color="#718096")
        )
        reset_settings_btn.on_click(self.reset_settings)
        reset_settings_btn.render(control_panel, "tkinter").pack(pady=5)
        
        # Dashboard example
        dashboard_frame = tk.LabelFrame(frame, text="Mini Dashboard", 
                                      padx=20, pady=15, bg="#ffffff")
        dashboard_frame.pack(fill="both", expand=True, pady=10)
        
        # Dashboard content
        dashboard_row1 = tk.Frame(dashboard_frame, bg="#ffffff")
        dashboard_row1.pack(fill="x", pady=10)
        
        # CPU Usage (fake)
        cpu_frame = tk.Frame(dashboard_row1, bg="#ffffff")
        cpu_frame.pack(side="left", padx=20)
        
        tk.Label(cpu_frame, text="CPU Usage", bg="#ffffff", font=("Arial", 10, "bold")).pack()
        self.cpu_progress = AnimatedProgressBar(
            initial_value=45,
            config=WidgetConfig(width=150, height=20),
            style=ProgressBarStyle(
                fill_color="#4299e1",
                text_format="{value}%"
            )
        )
        self.cpu_progress.render(cpu_frame, "tkinter").pack(pady=5)
        
        # Memory Usage (fake)
        memory_frame = tk.Frame(dashboard_row1, bg="#ffffff")
        memory_frame.pack(side="left", padx=20)
        
        tk.Label(memory_frame, text="Memory", bg="#ffffff", font=("Arial", 10, "bold")).pack()
        self.memory_progress = AnimatedProgressBar(
            initial_value=67,
            config=WidgetConfig(width=150, height=20),
            style=ProgressBarStyle(
                fill_color="#48bb78",
                text_format="{value}%"
            )
        )
        self.memory_progress.render(memory_frame, "tkinter").pack(pady=5)
        
        # Disk Usage (fake)
        disk_frame = tk.Frame(dashboard_row1, bg="#ffffff")
        disk_frame.pack(side="left", padx=20)
        
        tk.Label(disk_frame, text="Disk Space", bg="#ffffff", font=("Arial", 10, "bold")).pack()
        self.disk_progress = AnimatedProgressBar(
            initial_value=23,
            config=WidgetConfig(width=150, height=20),
            style=ProgressBarStyle(
                fill_color="#ed8936",
                text_format="{value}%"
            )
        )
        self.disk_progress.render(disk_frame, "tkinter").pack(pady=5)
        
        # Dashboard controls
        dashboard_row2 = tk.Frame(dashboard_frame, bg="#ffffff")
        dashboard_row2.pack(fill="x", pady=20)
        
        # System toggles
        toggles_frame = tk.Frame(dashboard_row2, bg="#ffffff")
        toggles_frame.pack(side="left")
        
        tk.Label(toggles_frame, text="Système:", bg="#ffffff", 
                font=("Arial", 10, "bold")).pack(anchor="w")
        
        # WiFi toggle
        wifi_frame = tk.Frame(toggles_frame, bg="#ffffff")
        wifi_frame.pack(anchor="w", pady=2)
        
        self.wifi_toggle = AnimatedToggle(
            initial_state=True,
            style=ToggleStyle(
                track_color_off="#e2e8f0",
                track_color_on="#48bb78",
                track_width=50,
                track_height=25
            )
        )
        self.wifi_toggle.render(wifi_frame, "tkinter").pack(side="left")
        tk.Label(wifi_frame, text=" WiFi", bg="#ffffff").pack(side="left")
        
        # Bluetooth toggle
        bt_frame = tk.Frame(toggles_frame, bg="#ffffff")
        bt_frame.pack(anchor="w", pady=2)
        
        self.bt_toggle = AnimatedToggle(
            initial_state=False,
            style=ToggleStyle(
                track_color_off="#e2e8f0",
                track_color_on="#4299e1",
                track_width=50,
                track_height=25
            )
        )
        self.bt_toggle.render(bt_frame, "tkinter").pack(side="left")
        tk.Label(bt_frame, text=" Bluetooth", bg="#ffffff").pack(side="left")
        
        # Notifications toggle  
        notif_frame = tk.Frame(toggles_frame, bg="#ffffff")
        notif_frame.pack(anchor="w", pady=2)
        
        self.notif_toggle = AnimatedToggle(
            initial_state=True,
            style=ToggleStyle(
                track_color_off="#e2e8f0",
                track_color_on="#9f7aea",
                track_width=50,
                track_height=25
            )
        )
        self.notif_toggle.render(notif_frame, "tkinter").pack(side="left")
        tk.Label(notif_frame, text=" Notifications", bg="#ffffff").pack(side="left")
        
        # Dashboard update button
        update_frame = tk.Frame(dashboard_row2, bg="#ffffff")
        update_frame.pack(side="right")
        
        update_dashboard_btn = AnimatedButton(
            "🔄 Actualiser Dashboard",
            config=WidgetConfig(width=180, height=35),
            style=ButtonStyle(normal_color="#805ad5", hover_color="#6b46c1")
        )
        update_dashboard_btn.on_click(self.update_dashboard)
        update_dashboard_btn.render(update_frame, "tkinter").pack()
        
        # Start dashboard updates
        self.start_dashboard_updates()
    
    def create_settings_content(self, scroll_view):
        """Créer le contenu du panneau de paramètres"""
        # Video settings
        video_section = tk.Label(
            scroll_view._content_frame,
            text="🎥 Paramètres Vidéo",
            font=("Arial", 11, "bold"),
            bg="#fafafa"
        )
        video_section.pack(anchor="w", pady=(10, 5))
        
        # Quality toggle
        quality_frame = tk.Frame(scroll_view._content_frame, bg="#fafafa")
        quality_frame.pack(anchor="w", pady=2)
        
        self.quality_toggle = AnimatedToggle(
            initial_state=True,
            style=ToggleStyle(track_width=45, track_height=22)
        )
        self.quality_toggle.render(quality_frame, "tkinter").pack(side="left")
        tk.Label(quality_frame, text=" Haute Qualité", bg="#fafafa").pack(side="left")
        
        # Fullscreen toggle
        fullscreen_frame = tk.Frame(scroll_view._content_frame, bg="#fafafa")
        fullscreen_frame.pack(anchor="w", pady=2)
        
        self.fullscreen_toggle = AnimatedToggle(
            initial_state=False,
            style=ToggleStyle(track_width=45, track_height=22)
        )
        self.fullscreen_toggle.render(fullscreen_frame, "tkinter").pack(side="left")
        tk.Label(fullscreen_frame, text=" Plein Écran", bg="#fafafa").pack(side="left")
        
        # Audio settings
        audio_section = tk.Label(
            scroll_view._content_frame,
            text="🔊 Paramètres Audio",
            font=("Arial", 11, "bold"),
            bg="#fafafa"
        )
        audio_section.pack(anchor="w", pady=(15, 5))
        
        # Volume
        volume_frame = tk.Frame(scroll_view._content_frame, bg="#fafafa")
        volume_frame.pack(anchor="w", pady=5, fill="x")
        
        tk.Label(volume_frame, text="Volume:", bg="#fafafa").pack(anchor="w")
        self.volume_progress = AnimatedProgressBar(
            initial_value=75,
            config=WidgetConfig(width=200, height=18),
            style=ProgressBarStyle(
                fill_color="#48bb78",
                text_format="{value}%",
                text_font_size=10
            )
        )
        self.volume_progress.render(volume_frame, "tkinter").pack(anchor="w", pady=2)
        
        # Mute toggle
        mute_frame = tk.Frame(scroll_view._content_frame, bg="#fafafa")
        mute_frame.pack(anchor="w", pady=2)
        
        self.mute_toggle = AnimatedToggle(
            initial_state=False,
            style=ToggleStyle(
                track_color_on="#f56565",
                track_width=45,
                track_height=22
            )
        )
        self.mute_toggle.render(mute_frame, "tkinter").pack(side="left")
        tk.Label(mute_frame, text=" Muet", bg="#fafafa").pack(side="left")
        
        # Network settings
        network_section = tk.Label(
            scroll_view._content_frame,
            text="🌐 Paramètres Réseau",
            font=("Arial", 11, "bold"),
            bg="#fafafa"
        )
        network_section.pack(anchor="w", pady=(15, 5))
        
        # Auto-connect toggle
        autoconnect_frame = tk.Frame(scroll_view._content_frame, bg="#fafafa")
        autoconnect_frame.pack(anchor="w", pady=2)
        
        self.autoconnect_toggle = AnimatedToggle(
            initial_state=True,
            style=ToggleStyle(track_width=45, track_height=22)
        )
        self.autoconnect_toggle.render(autoconnect_frame, "tkinter").pack(side="left")
        tk.Label(autoconnect_frame, text=" Connexion Auto", bg="#fafafa").pack(side="left")
        
        # VPN toggle
        vpn_frame = tk.Frame(scroll_view._content_frame, bg="#fafafa")
        vpn_frame.pack(anchor="w", pady=2)
        
        self.vpn_toggle = AnimatedToggle(
            initial_state=False,
            style=ToggleStyle(
                track_color_on="#9f7aea",
                track_width=45,
                track_height=22
            )
        )
        self.vpn_toggle.render(vpn_frame, "tkinter").pack(side="left")
        tk.Label(vpn_frame, text=" VPN", bg="#fafafa").pack(side="left")
        
        # Bandwidth usage
        bandwidth_frame = tk.Frame(scroll_view._content_frame, bg="#fafafa")
        bandwidth_frame.pack(anchor="w", pady=5, fill="x")
        
        tk.Label(bandwidth_frame, text="Utilisation Bande Passante:", bg="#fafafa").pack(anchor="w")
        self.bandwidth_progress = AnimatedProgressBar(
            initial_value=34,
            config=WidgetConfig(width=200, height=18),
            style=ProgressBarStyle(
                fill_color="#4299e1",
                text_format="{value}%",
                text_font_size=10
            )
        )
        self.bandwidth_progress.render(bandwidth_frame, "tkinter").pack(anchor="w", pady=2)
    
    def populate_scroll_view(self):
        """Remplir la vue défilante avec du contenu"""
        for i in range(15):
            item_frame = tk.Frame(self.scroll_view._content_frame, 
                                bg="#ffffff", relief="solid", bd=1)
            item_frame.pack(fill="x", pady=2, padx=5)
            
            # Item content
            content_frame = tk.Frame(item_frame, bg="#ffffff")
            content_frame.pack(fill="x", padx=10, pady=8)
            
            # Icon and title
            title_frame = tk.Frame(content_frame, bg="#ffffff")
            title_frame.pack(fill="x")
            
            icon = "📄" if i % 3 == 0 else "📁" if i % 3 == 1 else "🖼️"
            tk.Label(title_frame, text=f"{icon} Élément {i+1}", 
                    bg="#ffffff", font=("Arial", 11, "bold")).pack(side="left")
            
            # Description
            desc = f"Description de l'élément {i+1}. Ceci est un exemple de contenu scrollable."
            tk.Label(content_frame, text=desc, bg="#ffffff", 
                    font=("Arial", 9), fg="#666666").pack(anchor="w", pady=(2, 0))
    
    # Event handlers
    def update_toggle_status(self, toggle_id, state):
        """Mettre à jour le statut des toggles"""
        status_text = self.toggle_status.get("1.0", "end")
        lines = status_text.split('\n')
        
        # Update or add status line
        status_line = f"Toggle {toggle_id}: {'ON' if state else 'OFF'}"
        found = False
        
        for i, line in enumerate(lines):
            if line.startswith(f"Toggle {toggle_id}:"):
                lines[i] = status_line
                found = True
                break
        
        if not found:
            lines.append(status_line)
        
        # Update text widget
        self.toggle_status.delete("1.0", "end")
        self.toggle_status.insert("1.0", '\n'.join(lines))
    
    def trigger_toggle_pulse(self):
        """Déclencher l'animation pulse sur les toggles"""
        self.toggle1.pulse_animation(duration=1.2, intensity=0.8)
        self.toggle2.pulse_animation(duration=1.0, intensity=1.0)
    
    def trigger_toggle_flash(self):
        """Déclencher l'animation flash sur les toggles"""
        self.toggle3.flash_animation("#ffffff", duration=0.5)
        self.toggle4.flash_animation("#ffff00", duration=0.6)
    
    def trigger_toggle_shake(self):
        """Déclencher l'animation shake sur les toggles"""
        self.toggle1.shake_animation(duration=0.6, intensity=8.0)
        self.toggle2.shake_animation(duration=0.5, intensity=6.0)
    
    def start_progress_simulation(self):
        """Démarrer la simulation de progression"""
        if self.is_progress_running:
            return
        
        self.is_progress_running = True
        self.progress_value = 0
        
        def update_progress():
            while self.is_progress_running and self.progress_value < 100:
                self.progress_value += 1
                
                # Update progress bars
                self.progress1.set_value(self.progress_value)
                self.progress2.set_value(self.progress_value * 0.8)
                self.progress3.set_value(self.progress_value * 1.2 if self.progress_value * 1.2 <= 100 else 100)
                self.progress4.set_value(self.progress_value * 0.9)
                
                # Update status
                self.progress_status.configure(text=f"Progression: {self.progress_value}% - En cours...")
                
                time.sleep(0.1)
            
            if self.progress_value >= 100:
                self.progress_status.configure(text="Progression: 100% - Terminé!")
                self.is_progress_running = False
        
        self.progress_thread = threading.Thread(target=update_progress, daemon=True)
        self.progress_thread.start()
    
    def stop_progress_simulation(self):
        """Arrêter la simulation de progression"""
        self.is_progress_running = False
        self.progress_status.configure(text=f"Progression: {self.progress_value}% - Arrêté")
    
    def reset_progress(self):
        """Remettre à zéro les barres de progression"""
        self.is_progress_running = False
        self.progress_value = 0
        
        self.progress1.set_value(0)
        self.progress2.set_value(0)
        self.progress3.set_value(0)
        self.progress4.set_value(0)
        
        self.progress_status.configure(text="Progression: 0% - Reset")
    
    def flash_progress(self):
        """Effet flash sur les barres de progression"""
        self.progress1.flash_animation("#ffffff", 0.4)
        self.progress2.flash_animation("#ffff00", 0.5)
        self.progress3.flash_animation("#ff69b4", 0.3)
        self.progress4.flash_animation("#00ffff", 0.6)
    
    def scroll_to_middle(self):
        """Défiler vers le milieu"""
        content_height = self.scroll_view.get_content_size()[1]
        middle_y = content_height / 2 - self.scroll_view.config.height / 2
        self.scroll_view.scroll_to(0, middle_y)
    
    def scroll_to_bottom(self):
        """Défiler vers le bas"""
        content_height = self.scroll_view.get_content_size()[1]
        bottom_y = content_height - self.scroll_view.config.height
        self.scroll_view.scroll_to(0, bottom_y)
    
    def add_scroll_content(self):
        """Ajouter du contenu à la vue défilante"""
        import random
        
        item_frame = tk.Frame(self.scroll_view._content_frame, 
                            bg="#e6fffa", relief="solid", bd=1)
        item_frame.pack(fill="x", pady=2, padx=5)
        
        content_frame = tk.Frame(item_frame, bg="#e6fffa")
        content_frame.pack(fill="x", padx=10, pady=8)
        
        icons = ["🆕", "⭐", "🎉", "🚀", "💫"]
        icon = random.choice(icons)
        
        tk.Label(content_frame, text=f"{icon} Nouvel élément ajouté!", 
                bg="#e6fffa", font=("Arial", 11, "bold")).pack(anchor="w")
        
        tk.Label(content_frame, text="Contenu ajouté dynamiquement avec scroll automatique.", 
                bg="#e6fffa", font=("Arial", 9), fg="#2d5a4a").pack(anchor="w", pady=(2, 0))
        
        # Auto-scroll to new content
        self.scroll_view.scroll_to_widget(item_frame)
    
    def clear_scroll_content(self):
        """Vider le contenu de la vue défilante"""
        self.scroll_view.clear_widgets()
        self.scroll_view.scroll_to(0, 0)
    
    def update_scroll_info(self):
        """Mettre à jour les informations de défilement"""
        try:
            pos_x, pos_y = self.scroll_view.get_scroll_position()
            size_w, size_h = self.scroll_view.get_content_size()
            
            self.scroll_info.configure(
                text=f"Position: ({int(pos_x)}, {int(pos_y)})\nTaille: ({size_w}, {size_h})"
            )
        except:
            pass
        
        # Schedule next update
        self.root.after(500, self.update_scroll_info)
    
    def save_settings(self):
        """Sauvegarder les paramètres (simulation)"""
        print("💾 Paramètres sauvegardés!")
        # Flash effect on save
        if hasattr(self, 'quality_toggle'):
            self.quality_toggle.flash_animation("#00ff00", 0.3)
        
    def load_settings(self):
        """Charger les paramètres (simulation)"""
        print("📂 Paramètres chargés!")
        # Random settings for demo
        import random
        if hasattr(self, 'volume_progress'):
            self.volume_progress.set_value(random.randint(30, 90))
        
    def reset_settings(self):
        """Remettre à zéro les paramètres"""
        print("🔄 Paramètres remis à zéro!")
        if hasattr(self, 'volume_progress'):
            self.volume_progress.set_value(50)
    
    def update_dashboard(self):
        """Mettre à jour le dashboard"""
        import random
        
        # Update fake system stats
        cpu_val = random.randint(20, 80)
        memory_val = random.randint(40, 85)
        disk_val = random.randint(15, 60)
        
        self.cpu_progress.set_value(cpu_val)
        self.memory_progress.set_value(memory_val)
        self.disk_progress.set_value(disk_val)
        
        print(f"📊 Dashboard mis à jour - CPU: {cpu_val}%, RAM: {memory_val}%, Disk: {disk_val}%")
    
    def start_dashboard_updates(self):
        """Démarrer les mises à jour automatiques du dashboard"""
        def auto_update():
            self.update_dashboard()
            self.root.after(5000, auto_update)  # Update every 5 seconds
        
        # Start first update
        self.root.after(2000, auto_update)
    
    def run(self):
        """Lancer l'application"""
        print("🚀 Lancement de la démonstration complète...")
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    try:
        app = CompleteDemo2()
        app.run()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()