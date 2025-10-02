"""
demo_tkinter.py - Complete demonstration with Tkinter
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add library path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animated_widgets_pack import AnimatedButton, WidgetConfig, ButtonStyle
from animated_widgets_pack import ColorUtils, AnimationManager, EasingType

class AnimatedWidgetsDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AnimatedWidgetsPack - Tkinter Demo")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Center the window
        self.center_window()
        
        self.create_widgets()
    
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
        
        # Title
        title = tk.Label(
            self.root,
            text="AnimatedWidgetsPack Demo",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(
            self.root,
            text="Interactive Animated Widgets for Python",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        subtitle.pack(pady=(0, 30))
        
        # Button demos
        self.create_buttons_section()
        
        # Animation demos
        self.create_animation_section()
        
        # Log section
        self.create_log_section()
    
    def create_buttons_section(self):
        """Create button demonstration section"""
        frame = tk.LabelFrame(
            self.root, 
            text="Animated Buttons", 
            font=("Arial", 14, "bold"), 
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        frame.pack(pady=10, padx=20, fill="x")
        
        # Button configuration
        btn_config = WidgetConfig(
            width=160, height=50,
            border_radius=8,
            animation_duration=0.3,
            font_size=11
        )
        
        # Primary button
        primary_style = ButtonStyle(
            normal_color="#3498db",
            hover_color="#2980b9",
            pressed_color="#21618c",
            hover_lift=3.0,
            click_scale=0.92
        )
        
        self.primary_btn = AnimatedButton(
            text="Primary Button",
            config=btn_config,
            style=primary_style
        )
        
        primary_widget = self.primary_btn.render(frame, "tkinter")
        primary_widget.pack(side="left", padx=10, pady=10)
        
        self.primary_btn.on_click(
            lambda: self.log_message("Primary Button clicked! 🎯")
        )
        
        # Success button
        success_style = ButtonStyle(
            normal_color="#27ae60",
            hover_color="#229954",
            pressed_color="#1e8449"
        )
        
        self.success_btn = AnimatedButton(
            text="Success",
            config=btn_config,
            style=success_style
        )
        
        success_widget = self.success_btn.render(frame, "tkinter")
        success_widget.pack(side="left", padx=10, pady=10)
        
        self.success_btn.on_click(
            lambda: self.log_message("Success! Operation completed ✅")
        )
        
        # Warning button
        warning_style = ButtonStyle(
            normal_color="#f39c12",
            hover_color="#e67e22",
            pressed_color="#d35400"
        )
        
        self.warning_btn = AnimatedButton(
            text="Warning",
            config=btn_config,
            style=warning_style
        )
        
        warning_widget = self.warning_btn.render(frame, "tkinter")
        warning_widget.pack(side="left", padx=10, pady=10)
        
        self.warning_btn.on_click(
            lambda: self.log_message("Warning: Please check your input ⚠️")
        )
        
        # Danger button
        danger_style = ButtonStyle(
            normal_color="#e74c3c",
            hover_color="#c0392b",
            pressed_color="#a93226"
        )
        
        self.danger_btn = AnimatedButton(
            text="Danger",
            config=btn_config,
            style=danger_style
        )
        
        danger_widget = self.danger_btn.render(frame, "tkinter")
        danger_widget.pack(side="left", padx=10, pady=10)
        
        self.danger_btn.on_click(
            lambda: self.log_message("Danger: Destructive action triggered! 🚨")
        )
    
    def create_animation_section(self):
        """Create animation demonstration section"""
        frame = tk.LabelFrame(
            self.root, 
            text="Animation Effects", 
            font=("Arial", 14, "bold"), 
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        frame.pack(pady=10, padx=20, fill="x")
        
        # Animation buttons
        btn_config = WidgetConfig(
            width=140, height=45,
            font_size=10
        )
        
        # Pulse animation
        pulse_style = ButtonStyle(
            normal_color="#9b59b6",
            hover_color="#8e44ad",
            pressed_color="#7d3c98"
        )
        
        self.pulse_btn = AnimatedButton(
            text="Pulse Effect",
            config=btn_config,
            style=pulse_style
        )
        
        pulse_widget = self.pulse_btn.render(frame, "tkinter")
        pulse_widget.pack(side="left", padx=5, pady=10)
        
        self.pulse_btn.on_click(
            lambda: self.trigger_pulse_animation()
        )
        
        # Flash animation
        flash_style = ButtonStyle(
            normal_color="#1abc9c",
            hover_color="#16a085",
            pressed_color="#138d75"
        )
        
        self.flash_btn = AnimatedButton(
            text="Flash Effect",
            config=btn_config,
            style=flash_style
        )
        
        flash_widget = self.flash_btn.render(frame, "tkinter")
        flash_widget.pack(side="left", padx=5, pady=10)
        
        self.flash_btn.on_click(
            lambda: self.trigger_flash_animation()
        )
        
        # Bounce animation
        bounce_style = ButtonStyle(
            normal_color="#e67e22",
            hover_color="#d35400",
            pressed_color="#a04000"
        )
        
        self.bounce_btn = AnimatedButton(
            text="Bounce Effect",
            config=btn_config,
            style=bounce_style
        )
        
        bounce_widget = self.bounce_btn.render(frame, "tkinter")
        bounce_widget.pack(side="left", padx=5, pady=10)
        
        self.bounce_btn.on_click(
            lambda: self.trigger_bounce_animation()
        )
        
        # Color transition
        transition_style = ButtonStyle(
            normal_color="#34495e",
            hover_color="#2c3e50",
            pressed_color="#1b2631"
        )
        
        self.transition_btn = AnimatedButton(
            text="Color Transition",
            config=btn_config,
            style=transition_style
        )
        
        transition_widget = self.transition_btn.render(frame, "tkinter")
        transition_widget.pack(side="left", padx=5, pady=10)
        
        self.transition_btn.on_click(
            lambda: self.trigger_color_transition()
        )
        
        # Control buttons
        control_frame = tk.Frame(frame, bg="#f0f0f0")
        control_frame.pack(side="right", padx=10)
        
        stop_btn = tk.Button(
            control_frame,
            text="Stop All",
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10),
            command=self.stop_all_animations
        )
        stop_btn.pack(side="top", pady=2)
        
        reset_btn = tk.Button(
            control_frame,
            text="Reset",
            bg="#7f8c8d",
            fg="white",
            font=("Arial", 10),
            command=self.reset_all_buttons
        )
        reset_btn.pack(side="top", pady=2)
    
    def create_log_section(self):
        """Create event log section"""
        frame = tk.LabelFrame(
            self.root, 
            text="Event Log", 
            font=("Arial", 14, "bold"), 
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Text area with scrollbar
        text_frame = tk.Frame(frame)
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(
            text_frame,
            height=10,
            bg="white",
            fg="#2c3e50",
            font=("Consolas", 10),
            wrap="word",
            state="disabled"
        )
        
        scrollbar = tk.Scrollbar(text_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Control buttons
        btn_frame = tk.Frame(frame, bg="#f0f0f0")
        btn_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        clear_btn = tk.Button(
            btn_frame,
            text="Clear Log",
            command=self.clear_log,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10)
        )
        clear_btn.pack(side="left")
        
        demo_btn = tk.Button(
            btn_frame,
            text="Demo All Effects",
            command=self.demo_all_effects,
            bg="#3498db",
            fg="white",
            font=("Arial", 10)
        )
        demo_btn.pack(side="right")
    
    def log_message(self, message: str):
        """Add message to log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def clear_log(self):
        """Clear all log messages"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.log_message("Log cleared 🧹")
    
    def trigger_pulse_animation(self):
        """Trigger pulse animation on primary button"""
        self.primary_btn.pulse_animation(duration=1.0, scale_factor=1.2)
        self.log_message("Pulse animation triggered on Primary Button ✨")
    
    def trigger_flash_animation(self):
        """Trigger flash animation on success button"""
        self.success_btn.flash_animation(flash_color="#ffffff", duration=0.4)
        self.log_message("Flash animation triggered on Success Button ⚡")
    
    def trigger_bounce_animation(self):
        """Trigger bounce animation on warning button"""
        self.warning_btn.bounce_animation(duration=0.8)
        self.log_message("Bounce animation triggered on Warning Button 🏀")
    
    def trigger_color_transition(self):
        """Trigger color transition on danger button"""
        # Animate to a different color and back
        original = self.danger_btn.style.normal_color
        self.danger_btn.set_colors(normal="#8e44ad")
        
        # Schedule return to original color
        self.root.after(1000, lambda: self.danger_btn.set_colors(normal=original))
        self.log_message("Color transition triggered on Danger Button 🎨")
    
    def stop_all_animations(self):
        """Stop all running animations"""
        buttons = [
            self.primary_btn, self.success_btn, 
            self.warning_btn, self.danger_btn,
            self.pulse_btn, self.flash_btn,
            self.bounce_btn, self.transition_btn
        ]
        
        for btn in buttons:
            btn.stop_all_animations()
        
        self.log_message("All animations stopped ⏹️")
    
    def reset_all_buttons(self):
        """Reset all buttons to their default state"""
        self.stop_all_animations()
        
        # Reset colors
        self.danger_btn.set_colors(normal="#e74c3c")
        
        self.log_message("All buttons reset to default state 🔄")
    
    def demo_all_effects(self):
        """Demonstrate all animation effects in sequence"""
        self.log_message("🎪 Starting demo of all effects...")
        
        # Schedule animations with delays
        self.root.after(500, lambda: self.trigger_pulse_animation())
        self.root.after(2000, lambda: self.trigger_flash_animation())
        self.root.after(3500, lambda: self.trigger_bounce_animation())
        self.root.after(5000, lambda: self.trigger_color_transition())
        self.root.after(7000, lambda: self.log_message("Demo complete! 🎉"))
    
    def run(self):
        """Start the application"""
        self.log_message("🚀 AnimatedWidgetsPack Demo started")
        self.log_message("Click buttons to see animations in action!")
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = AnimatedWidgetsDemo()
        app.run()
    except KeyboardInterrupt:
        print("Demo stopped by user")
    except Exception as e:
        print(f"Error running demo: {e}")

if __name__ == "__main__":
    main()