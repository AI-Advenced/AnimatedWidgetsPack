# examples/simple_example_ScrollView_ProgressBar_ToggleButton.py
"""
Exemple simple des nouveaux widgets : ScrollView, ProgressBar, ToggleButton
Démontre l'utilisation basique de chaque widget
"""

import tkinter as tk
import threading
import time
import random

from animated_widgets_pack.ToggleButton import AnimatedToggle, ToggleStyle
from animated_widgets_pack.ProgressBar import AnimatedProgressBar, ProgressBarStyle
from animated_widgets_pack.ScrollView import AnimatedScrollView, ScrollViewStyle, ScrollBarStyle
from animated_widgets_pack.core import WidgetConfig
from animated_widgets_pack.buttons import AnimatedButton, ButtonStyle

class SimpleWidgetExample:
    """Exemple simple des nouveaux widgets"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Exemple Simple - Nouveaux Widgets")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f2f5")
        
        # Variables
        self.auto_progress = False
        self.progress_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configuration de l'interface"""
        # Title
        title = tk.Label(
            self.root,
            text="🎮 Exemples Simples - Nouveaux Widgets",
            font=("Arial", 18, "bold"),
            bg="#f0f2f5",
            fg="#1a202c"
        )
        title.pack(pady=20)
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left column - Toggle & Progress
        left_column = tk.Frame(main_frame, bg="#f0f2f5")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.create_toggle_section(left_column)
        self.create_progress_section(left_column)
        
        # Right column - ScrollView
        right_column = tk.Frame(main_frame, bg="#f0f2f5")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.create_scroll_section(right_column)
    
    def create_toggle_section(self, parent):
        """Section des boutons toggle"""
        frame = tk.LabelFrame(
            parent, 
            text="🔘 Boutons Toggle",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=15,
            pady=10
        )
        frame.pack(fill="x", pady=(0, 20))
        
        # Description
        desc = tk.Label(
            frame,
            text="Cliquez sur les toggles pour changer leur état",
            bg="#ffffff",
            fg="#666666",
            font=("Arial", 10)
        )
        desc.pack(pady=(0, 15))
        
        # Toggle 1 - Simple
        toggle1_frame = tk.Frame(frame, bg="#ffffff")
        toggle1_frame.pack(fill="x", pady=5)
        
        tk.Label(toggle1_frame, text="Mode Sombre:", 
                bg="#ffffff", font=("Arial", 11)).pack(side="left")
        
        self.toggle1 = AnimatedToggle(
            initial_state=False,
            style=ToggleStyle(
                track_color_off="#e2e8f0",
                track_color_on="#4299e1",
                track_width=50,
                track_height=25,
                transition_duration=0.3
            )
        )
        self.toggle1.on_toggle(lambda state: self.on_dark_mode_change(state))
        self.toggle1.render(toggle1_frame, "tkinter").pack(side="right")
        
        # Toggle 2 - Notifications
        toggle2_frame = tk.Frame(frame, bg="#ffffff")
        toggle2_frame.pack(fill="x", pady=5)
        
        tk.Label(toggle2_frame, text="Notifications:", 
                bg="#ffffff", font=("Arial", 11)).pack(side="left")
        
        self.toggle2 = AnimatedToggle(
            initial_state=True,
            style=ToggleStyle(
                track_color_off="#fed7d7",
                track_color_on="#48bb78",
                track_width=50,
                track_height=25,
                bounce_effect=True
            )
        )
        self.toggle2.on_toggle(lambda state: self.on_notifications_change(state))
        self.toggle2.render(toggle2_frame, "tkinter").pack(side="right")
        
        # Toggle 3 - Auto-save
        toggle3_frame = tk.Frame(frame, bg="#ffffff")
        toggle3_frame.pack(fill="x", pady=5)
        
        tk.Label(toggle3_frame, text="Sauvegarde Auto:", 
                bg="#ffffff", font=("Arial", 11)).pack(side="left")
        
        self.toggle3 = AnimatedToggle(
            initial_state=True,
            style=ToggleStyle(
                track_color_off="#e2e8f0",
                track_color_on="#9f7aea",
                glow_enabled=True,
                glow_color="#9f7aea",
                track_width=50,
                track_height=25
            )
        )
        self.toggle3.on_toggle(lambda state: self.on_autosave_change(state))
        self.toggle3.render(toggle3_frame, "tkinter").pack(side="right")
        
        # Status display
        self.toggle_status = tk.Label(
            frame,
            text="État: Mode Sombre: OFF, Notifications: ON, Auto-save: ON",
            bg="#f7fafc",
            fg="#4a5568",
            font=("Arial", 10),
            relief="solid",
            bd=1,
            padx=10,
            pady=5
        )
        self.toggle_status.pack(fill="x", pady=(15, 0))
    
    def create_progress_section(self, parent):
        """Section des barres de progression"""
        frame = tk.LabelFrame(
            parent,
            text="📊 Barres de Progression",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=15,
            pady=10
        )
        frame.pack(fill="both", expand=True)
        
        # Description
        desc = tk.Label(
            frame,
            text="Différents types de barres de progression",
            bg="#ffffff",
            fg="#666666",
            font=("Arial", 10)
        )
        desc.pack(pady=(0, 15))
        
        # Progress 1 - Simple
        progress1_frame = tk.Frame(frame, bg="#ffffff")
        progress1_frame.pack(fill="x", pady=10)
        
        tk.Label(progress1_frame, text="Téléchargement:", 
                bg="#ffffff", font=("Arial", 10)).pack(anchor="w")
        
        self.progress1 = AnimatedProgressBar(
            initial_value=35,
            config=WidgetConfig(width=300, height=22),
            style=ProgressBarStyle(
                background_color="#e2e8f0",
                fill_color="#4299e1",
                text_format="{value}%"
            )
        )
        self.progress1.render(progress1_frame, "tkinter").pack(anchor="w", pady=5)
        
        # Progress 2 - Gradient
        progress2_frame = tk.Frame(frame, bg="#ffffff")
        progress2_frame.pack(fill="x", pady=10)
        
        tk.Label(progress2_frame, text="Installation:", 
                bg="#ffffff", font=("Arial", 10)).pack(anchor="w")
        
        self.progress2 = AnimatedProgressBar(
            initial_value=78,
            config=WidgetConfig(width=300, height=22),
            style=ProgressBarStyle(
                fill_gradient_enabled=True,
                fill_gradient_colors=["#48bb78", "#38a169"],
                text_format="{value}%"
            )
        )
        self.progress2.render(progress2_frame, "tkinter").pack(anchor="w", pady=5)
        
        # Progress 3 - Indeterminate
        progress3_frame = tk.Frame(frame, bg="#ffffff")
        progress3_frame.pack(fill="x", pady=10)
        
        tk.Label(progress3_frame, text="Analyse en cours:", 
                bg="#ffffff", font=("Arial", 10)).pack(anchor="w")
        
        self.progress3 = AnimatedProgressBar(
            config=WidgetConfig(width=300, height=22),
            style=ProgressBarStyle(
                fill_color="#9f7aea",
                background_color="#e2e8f0",
                show_text=False
            )
        )
        self.progress3.set_indeterminate(True)
        self.progress3.render(progress3_frame, "tkinter").pack(anchor="w", pady=5)
        
        # Controls
        controls_frame = tk.Frame(frame, bg="#ffffff")
        controls_frame.pack(fill="x", pady=20)
        
        # Start/Stop auto-progress
        self.auto_progress_btn = AnimatedButton(
            "▶️ Démarrer Auto",
            config=WidgetConfig(width=130, height=30),
            style=ButtonStyle(
                normal_color="#48bb78",
                hover_color="#38a169",
                pressed_color="#2f855a"
            )
        )
        self.auto_progress_btn.on_click(self.toggle_auto_progress)
        self.auto_progress_btn.render(controls_frame, "tkinter").pack(side="left", padx=5)
        
        # Reset progress
        reset_btn = AnimatedButton(
            "🔄 Reset",
            config=WidgetConfig(width=100, height=30),
            style=ButtonStyle(
                normal_color="#a0aec0",
                hover_color="#718096",
                pressed_color="#4a5568"
            )
        )
        reset_btn.on_click(self.reset_progress)
        reset_btn.render(controls_frame, "tkinter").pack(side="left", padx=5)
        
        # Random values
        random_btn = AnimatedButton(
            "🎲 Aléatoire",
            config=WidgetConfig(width=110, height=30),
            style=ButtonStyle(
                normal_color="#ed8936",
                hover_color="#dd6b20",
                pressed_color="#c05621"
            )
        )
        random_btn.on_click(self.randomize_progress)
        random_btn.render(controls_frame, "tkinter").pack(side="left", padx=5)
    
    def create_scroll_section(self, parent):
        """Section de la vue défilante"""
        frame = tk.LabelFrame(
            parent,
            text="📜 Vue Défilante",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            padx=15,
            pady=10
        )
        frame.pack(fill="both", expand=True)
        
        # Description
        desc = tk.Label(
            frame,
            text="Contenu scrollable avec barres de défilement personnalisées",
            bg="#ffffff",
            fg="#666666",
            font=("Arial", 10)
        )
        desc.pack(pady=(0, 15))
        
        # ScrollView container
        scroll_container = tk.Frame(frame, bg="#ffffff")
        scroll_container.pack(fill="both", expand=True)
        
        # Create ScrollView
        self.scroll_view = AnimatedScrollView(
            config=WidgetConfig(width=380, height=300),
            style=ScrollViewStyle(
                background_color="#f7fafc",
                border_color="#e2e8f0",
                border_width=2,
                content_padding=10,
                momentum_enabled=True,
                elastic_enabled=True
            ),
            scrollbar_style=ScrollBarStyle(
                auto_hide=True,
                thumb_color="#cbd5e0",
                thumb_hover_color="#a0aec0",
                track_color="#f7fafc"
            )
        )
        
        scroll_widget = self.scroll_view.render(scroll_container, "tkinter")
        scroll_widget.pack(pady=10)
        
        # Populate with content
        self.populate_scroll_content()
        
        # Scroll controls
        scroll_controls = tk.Frame(frame, bg="#ffffff")
        scroll_controls.pack(fill="x", pady=10)
        
        # Navigation buttons
        top_btn = AnimatedButton(
            "⬆️ Haut",
            config=WidgetConfig(width=80, height=25),
            style=ButtonStyle(normal_color="#4299e1", hover_color="#3182ce")
        )
        top_btn.on_click(lambda: self.scroll_view.scroll_to(0, 0))
        top_btn.render(scroll_controls, "tkinter").pack(side="left", padx=2)
        
        middle_btn = AnimatedButton(
            "🎯 Milieu",
            config=WidgetConfig(width=80, height=25),
            style=ButtonStyle(normal_color="#48bb78", hover_color="#38a169")
        )
        middle_btn.on_click(self.scroll_to_middle)
        middle_btn.render(scroll_controls, "tkinter").pack(side="left", padx=2)
        
        bottom_btn = AnimatedButton(
            "⬇️ Bas",
            config=WidgetConfig(width=80, height=25),
            style=ButtonStyle(normal_color="#ed8936", hover_color="#dd6b20")
        )
        bottom_btn.on_click(self.scroll_to_bottom)
        bottom_btn.render(scroll_controls, "tkinter").pack(side="left", padx=2)
        
        # Add content button
        add_btn = AnimatedButton(
            "➕ Ajouter",
            config=WidgetConfig(width=90, height=25),
            style=ButtonStyle(normal_color="#9f7aea", hover_color="#805ad5")
        )
        add_btn.on_click(self.add_scroll_item)
        add_btn.render(scroll_controls, "tkinter").pack(side="left", padx=2)
    
    def populate_scroll_content(self):
        """Remplir le contenu scrollable"""
        content_types = [
            ("📝", "Document", "Fichier texte important"),
            ("🖼️", "Image", "Photo de vacances"),
            ("🎵", "Musique", "Chanson préférée"),
            ("📊", "Graphique", "Données mensuelles"),
            ("📧", "Email", "Message important"),
            ("📅", "Calendrier", "Événement programmé"),
            ("🗂️", "Dossier", "Documents classés"),
            ("🔗", "Lien", "Site web utile"),
            ("📱", "App", "Application mobile"),
            ("🎮", "Jeu", "Jeu vidéo amusant")
        ]
        
        for i, (icon, title, desc) in enumerate(content_types):
            self.create_scroll_item(icon, f"{title} {i+1}", desc)
    
    def create_scroll_item(self, icon, title, description):
        """Créer un élément pour la vue scrollable"""
        item_frame = tk.Frame(
            self.scroll_view._content_frame,
            bg="#ffffff",
            relief="solid",
            bd=1
        )
        item_frame.pack(fill="x", pady=3, padx=5)
        
        # Content
        content_frame = tk.Frame(item_frame, bg="#ffffff")
        content_frame.pack(fill="x", padx=10, pady=8)
        
        # Header with icon and title
        header_frame = tk.Frame(content_frame, bg="#ffffff")
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame,
            text=f"{icon} {title}",
            bg="#ffffff",
            font=("Arial", 11, "bold"),
            fg="#2d3748"
        ).pack(side="left")
        
        # Description
        tk.Label(
            content_frame,
            text=description,
            bg="#ffffff",
            font=("Arial", 9),
            fg="#718096"
        ).pack(anchor="w", pady=(3, 0))
    
    # Event handlers
    def on_dark_mode_change(self, state):
        """Gérer le changement de mode sombre"""
        mode = "ON" if state else "OFF"
        print(f"🌙 Mode Sombre: {mode}")
        self.update_toggle_status()
        
        # Visual feedback
        if state:
            self.root.configure(bg="#2d3748")
        else:
            self.root.configure(bg="#f0f2f5")
    
    def on_notifications_change(self, state):
        """Gérer le changement de notifications"""
        mode = "ON" if state else "OFF"
        print(f"🔔 Notifications: {mode}")
        self.update_toggle_status()
    
    def on_autosave_change(self, state):
        """Gérer le changement de sauvegarde automatique"""
        mode = "ON" if state else "OFF"
        print(f"💾 Sauvegarde Auto: {mode}")
        self.update_toggle_status()
        
        if state:
            self.toggle3.pulse_animation(duration=1.0, intensity=0.5)
    
    def update_toggle_status(self):
        """Mettre à jour l'affichage du statut des toggles"""
        dark_mode = "ON" if self.toggle1.get_value() else "OFF"
        notifications = "ON" if self.toggle2.get_value() else "OFF"
        autosave = "ON" if self.toggle3.get_value() else "OFF"
        
        status_text = f"État: Mode Sombre: {dark_mode}, Notifications: {notifications}, Auto-save: {autosave}"
        self.toggle_status.configure(text=status_text)
    
    def toggle_auto_progress(self):
        """Démarrer/arrêter la progression automatique"""
        if not self.auto_progress:
            self.start_auto_progress()
        else:
            self.stop_auto_progress()
    
    def start_auto_progress(self):
        """Démarrer la progression automatique"""
        self.auto_progress = True
        self.auto_progress_btn.set_text("⏸️ Arrêter Auto")
        self.auto_progress_btn.set_colors(normal="#f56565")
        
        def progress_loop():
            current_val = 0
            direction = 1
            
            while self.auto_progress:
                current_val += direction * 2
                
                if current_val >= 100:
                    current_val = 100
                    direction = -1
                elif current_val <= 0:
                    current_val = 0
                    direction = 1
                
                # Update progress bars
                self.progress1.set_value(current_val)
                self.progress2.set_value(min(100, current_val * 1.2))
                
                time.sleep(0.1)
        
        self.progress_thread = threading.Thread(target=progress_loop, daemon=True)
        self.progress_thread.start()
    
    def stop_auto_progress(self):
        """Arrêter la progression automatique"""
        self.auto_progress = False
        self.auto_progress_btn.set_text("▶️ Démarrer Auto")
        self.auto_progress_btn.set_colors(normal="#48bb78")
    
    def reset_progress(self):
        """Remettre à zéro les barres de progression"""
        self.stop_auto_progress()
        self.progress1.set_value(0)
        self.progress2.set_value(0)
        print("🔄 Progression remise à zéro")
    
    def randomize_progress(self):
        """Valeurs aléatoires pour les barres de progression"""
        val1 = random.randint(10, 95)
        val2 = random.randint(15, 90)
        
        self.progress1.set_value(val1)
        self.progress2.set_value(val2)
        
        print(f"🎲 Valeurs aléatoires: {val1}%, {val2}%")
    
    def scroll_to_middle(self):
        """Défiler vers le milieu du contenu"""
        content_height = self.scroll_view.get_content_size()[1]
        middle_y = content_height / 2 - self.scroll_view.config.height / 2
        self.scroll_view.scroll_to(0, middle_y)
    
    def scroll_to_bottom(self):
        """Défiler vers le bas du contenu"""
        content_height = self.scroll_view.get_content_size()[1]
        bottom_y = content_height - self.scroll_view.config.height
        self.scroll_view.scroll_to(0, bottom_y)
    
    def add_scroll_item(self):
        """Ajouter un nouvel élément au contenu scrollable"""
        import random
        
        icons = ["⭐", "🎉", "🚀", "💎", "🌟", "🎁", "🏆", "🎯"]
        icon = random.choice(icons)
        
        item_count = len(self.scroll_view._child_widgets) + 1
        title = f"Nouvel élément {item_count}"
        desc = "Ajouté dynamiquement par l'utilisateur"
        
        self.create_scroll_item(icon, title, desc)
        
        # Auto-scroll to new item
        self.scroll_to_bottom()
        
        print(f"➕ Nouvel élément ajouté: {title}")
    
    def run(self):
        """Lancer l'application"""
        print("🚀 Lancement de l'exemple simple...")
        print("💡 Conseils:")
        print("   • Cliquez sur les toggles pour changer leur état")
        print("   • Utilisez les boutons pour contrôler les barres de progression")
        print("   • Faites défiler le contenu avec la souris ou les boutons")
        print("   • Ajoutez du contenu dynamiquement")
        
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    try:
        app = SimpleWidgetExample()
        app.run()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()