"""
simple_example.py - Basic usage example of AnimatedWidgetsPack
"""

import tkinter as tk
import sys
import os

# Add library path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from animated_widgets_pack import AnimatedButton, WidgetConfig, ButtonStyle

def create_simple_demo():
    """Create a simple demonstration window"""
    
    # Create main window
    root = tk.Tk()
    root.title("AnimatedWidgetsPack - Simple Example")
    root.geometry("400x300")
    root.configure(bg="#ecf0f1")
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    pos_x = (root.winfo_screenwidth() // 2) - (width // 2)
    pos_y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
    
    # Title
    title = tk.Label(
        root,
        text="Simple Animated Button Demo",
        font=("Arial", 16, "bold"),
        bg="#ecf0f1",
        fg="#2c3e50"
    )
    title.pack(pady=30)
    
    # Configure animated button
    config = WidgetConfig(
        width=180, 
        height=50,
        border_radius=10,
        animation_duration=0.3,
        font_size=12
    )
    
    style = ButtonStyle(
        normal_color="#3498db",
        hover_color="#2980b9", 
        pressed_color="#21618c",
        hover_lift=4.0,
        click_scale=0.9
    )
    
    # Create animated button
    button = AnimatedButton(
        text="Click Me! 🚀",
        config=config,
        style=style
    )
    
    # Render button
    button_widget = button.render(root, "tkinter")
    button_widget.pack(pady=20)
    
    # Status label
    status_label = tk.Label(
        root,
        text="Hover and click the button to see animations!",
        font=("Arial", 10),
        bg="#ecf0f1",
        fg="#7f8c8d"
    )
    status_label.pack(pady=10)
    
    # Click counter
    click_count = {"value": 0}
    
    def on_button_click():
        """Handle button click"""
        click_count["value"] += 1
        status_label.configure(
            text=f"Button clicked {click_count['value']} time(s)! ✨",
            fg="#27ae60"
        )
        
        # Trigger pulse animation on every 5th click
        if click_count["value"] % 5 == 0:
            button.pulse_animation(duration=0.8, scale_factor=1.3)
            status_label.configure(text="🎉 Bonus animation! 🎉")
    
    # Bind button click
    button.on_click(on_button_click)
    
    # Add hover callbacks for status updates
    button.bind_callback('hover_enter', 
        lambda: status_label.configure(text="Hovering... nice animation! 🎯", fg="#f39c12"))
    
    button.bind_callback('hover_leave', 
        lambda: status_label.configure(text="Hover and click the button to see animations!", fg="#7f8c8d"))
    
    # Instructions
    instructions = tk.Label(
        root,
        text="💡 Features:\n• Smooth hover animations\n• Click effects\n• Color transitions\n• Bonus pulse every 5 clicks",
        font=("Arial", 9),
        bg="#ecf0f1",
        fg="#95a5a6",
        justify="left"
    )
    instructions.pack(pady=20)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    print("🎨 Starting AnimatedWidgetsPack Simple Example...")
    print("Close the window to exit.")
    
    try:
        create_simple_demo()
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()