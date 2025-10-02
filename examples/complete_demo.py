# examples/complete_demo.py
"""
Démonstration complète avec tous les widgets
"""

import tkinter as tk
import math

from animated_widgets_pack.TextInput import TextInputStyle, TextInputType, AnimatedTextInput
from animated_widgets_pack.CheckBox import AnimatedCheckbox, CheckboxStyle
from animated_widgets_pack.Switch import AnimatedSwitch, SwitchAppearance
from animated_widgets_pack.core import WidgetConfig
from animated_widgets_pack.buttons import AnimatedButton, ButtonStyle

def create_complete_demo():
    root = tk.Tk()
    root.title("AnimatedWidgetsPack - Démonstration complète")
    root.geometry("800x600")
    root.configure(bg="#f8f9fa")
    
    # Configuration commune
    config = WidgetConfig(
        width=200,
        height=40,
        font_family="Arial",  # Changed from Segoe UI for better compatibility
        animation_duration=0.3
    )
    
    # Section boutons
    btn_frame = tk.LabelFrame(root, text="Boutons animés", padx=10, pady=10, bg="#f8f9fa")
    btn_frame.pack(fill="x", padx=20, pady=10)
    
    primary_btn = AnimatedButton(
        "Bouton Principal",
        config=config,
        style=ButtonStyle(normal_color="#007bff", hover_color="#0056b3")
    )
    primary_btn.render(btn_frame, "tkinter").pack(side="left", padx=5)
    
    # Section champs de texte
    input_frame = tk.LabelFrame(root, text="Champs de texte", padx=10, pady=10, bg="#f8f9fa")
    input_frame.pack(fill="x", padx=20, pady=10)
    
    email_input = AnimatedTextInput(
        placeholder="Entrez votre email",
        input_type=TextInputType.EMAIL,
        config=config,
        style=TextInputStyle(label_text="Email", floating_label=False)  # Disabled floating for simplicity
    )
    email_input.set_required().render(input_frame, "tkinter").pack(pady=5, fill="x")
    
    # Section checkboxes
    checkbox_frame = tk.LabelFrame(root, text="Cases à cocher", padx=10, pady=10, bg="#f8f9fa")
    checkbox_frame.pack(fill="x", padx=20, pady=10)
    
    checkbox = AnimatedCheckbox(
        label="J'accepte les conditions",
        style=CheckboxStyle(tri_state=False)
    )
    checkbox.render(checkbox_frame, "tkinter").pack(anchor="w", pady=5)
    
    # Section switches (simplified to avoid stipple issues)
    switch_frame = tk.LabelFrame(root, text="Interrupteurs", padx=10, pady=10, bg="#f8f9fa")
    switch_frame.pack(fill="x", padx=20, pady=10)
    
    # Create a simplified switch without shadow effects for compatibility
    switch = SimplifiedSwitch(
        label="Notifications",
        parent=switch_frame
    )
    
    # Log section
    log_frame = tk.LabelFrame(root, text="Journal d'événements", padx=10, pady=10, bg="#f8f9fa")
    log_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    log_text = tk.Text(log_frame, height=8, bg="white", wrap="word")
    scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
    log_text.configure(yscrollcommand=scrollbar.set)
    
    log_text.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def log_message(message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_text.insert("end", f"[{timestamp}] {message}\n")
        log_text.see("end")
    
    # Callbacks
    def on_form_submit():
        if email_input.is_valid() and checkbox.is_checked():
            log_message("✅ Formulaire valide !")
            # Animations de succès
            primary_btn.flash_animation("#27ae60")
            if hasattr(email_input, 'highlight_animation'):
                email_input.highlight_animation("#27ae60")
        else:
            log_message("❌ Formulaire invalide")
            # Animations d'erreur
            if not email_input.is_valid():
                log_message(f"   Email invalide: {email_input.get_validation_message()}")
                if hasattr(email_input, 'shake_animation'):
                    email_input.shake_animation()
            if not checkbox.is_checked():
                log_message("   Veuillez accepter les conditions")
                if hasattr(checkbox, 'shake_animation'):
                    checkbox.shake_animation()
    
    def on_email_change(old_value, new_value):
        if new_value:
            log_message(f"📝 Email modifié: {new_value}")
    
    def on_checkbox_change(state):
        status = "coché" if checkbox.is_checked() else "décoché"
        log_message(f"☐ Case à cocher {status}")
    
    def on_switch_change(is_on):
        status = "activé" if is_on else "désactivé"
        log_message(f"🔘 Notifications {status}")
    
    # Bind callbacks
    primary_btn.on_click(on_form_submit)
    email_input.on_value_changed(on_email_change)
    checkbox.on_state_changed(on_checkbox_change)
    switch.on_change(on_switch_change)
    
    # Initial log message
    log_message("🚀 Application démarrée - Testez les widgets !")
    
    root.mainloop()

class SimplifiedSwitch:
    """Simplified switch implementation to avoid Tkinter compatibility issues"""
    
    def __init__(self, label="", parent=None):
        self.label = label
        self.parent = parent
        self.is_on = False
        self.callbacks = []
        
        # Create the switch UI
        self.frame = tk.Frame(parent, bg=parent.cget('bg'))
        self.frame.pack(anchor="w", pady=5)
        
        # Switch canvas (simplified)
        self.canvas = tk.Canvas(
            self.frame, 
            width=60, 
            height=30, 
            bg=parent.cget('bg'),
            highlightthickness=0
        )
        self.canvas.pack(side="left", padx=(0, 10))
        
        # Label
        if label:
            self.label_widget = tk.Label(
                self.frame,
                text=label,
                bg=parent.cget('bg'),
                font=("Arial", 10)
            )
            self.label_widget.pack(side="left")
            self.label_widget.bind("<Button-1>", self.toggle)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.toggle)
        
        # Draw initial state
        self.draw()
    
    def draw(self):
        """Draw the switch"""
        self.canvas.delete("all")
        
        # Track
        track_color = "#4299e1" if self.is_on else "#cbd5e0"
        self.canvas.create_oval(
            5, 5, 55, 25,
            fill=track_color,
            outline="#e2e8f0",
            width=1,
            tags="track"
        )
        
        # Thumb
        thumb_x = 35 if self.is_on else 15
        self.canvas.create_oval(
            thumb_x - 8, 7, thumb_x + 8, 23,
            fill="#ffffff",
            outline="#e2e8f0",
            width=1,
            tags="thumb"
        )
    
    def toggle(self, event=None):
        """Toggle the switch state"""
        self.is_on = not self.is_on
        self.draw()
        
        # Trigger callbacks
        for callback in self.callbacks:
            try:
                callback(self.is_on)
            except Exception as e:
                print(f"Error in switch callback: {e}")
    
    def on_change(self, callback):
        """Add a callback for state changes"""
        self.callbacks.append(callback)
        return self
    
    def set_state(self, is_on):
        """Set switch state programmatically"""
        if self.is_on != is_on:
            self.is_on = is_on
            self.draw()
            
            # Trigger callbacks
            for callback in self.callbacks:
                try:
                    callback(self.is_on)
                except Exception as e:
                    print(f"Error in switch callback: {e}")

if __name__ == "__main__":
    create_complete_demo()