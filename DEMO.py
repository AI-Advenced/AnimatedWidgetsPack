#!/usr/bin/env python3
"""
DEMO.py - Quick demonstration of AnimatedWidgetsPack

Run this script to see the library in action!
"""

import sys
import os

# Add current directory to path for demo
sys.path.insert(0, '.')

def run_simple_demo():
    """Run a simple console demo"""
    print("🎨 AnimatedWidgetsPack Demo")
    print("=" * 50)
    
    try:
        # Import the library
        from animated_widgets_pack import (
            AnimatedButton, WidgetConfig, ButtonStyle, 
            ColorUtils, AnimationManager, EasingType
        )
        
        print("✅ Library imported successfully")
        
        # Create a button configuration
        config = WidgetConfig(
            width=200, 
            height=60,
            border_radius=12,
            animation_duration=0.3
        )
        
        # Create a button style
        style = ButtonStyle(
            normal_color="#3498db",
            hover_color="#2980b9",
            pressed_color="#21618c",
            text="Demo Button 🚀",
            hover_lift=5.0,
            click_scale=0.9
        )
        
        # Create animated button
        button = AnimatedButton("Amazing Button!", config, style)
        print(f"✅ Button created: '{button.style.text}'")
        print(f"   State: {button.get_state()}")
        print(f"   Colors: {style.normal_color} → {style.hover_color} → {style.pressed_color}")
        
        # Test color utilities
        original_color = ColorUtils.parse_color("#3498db")
        lighter_color = ColorUtils.lighten_color(original_color, 0.3)
        darker_color = ColorUtils.darken_color(original_color, 0.3)
        
        print(f"✅ Color manipulation:")
        print(f"   Original: {original_color.to_hex()}")
        print(f"   Lighter:  {lighter_color.to_hex()}")
        print(f"   Darker:   {darker_color.to_hex()}")
        
        # Test state management
        button.set_state("hover")
        print(f"✅ State changed to: {button.get_state()}")
        
        button.disable()
        print(f"✅ Button disabled: {button.get_state()}")
        
        button.enable()
        print(f"✅ Button enabled: {button.get_state()}")
        
        # Test callbacks
        click_count = {"value": 0}
        
        def on_click():
            click_count["value"] += 1
            print(f"   🖱️  Button clicked {click_count['value']} time(s)!")
        
        button.on_click(on_click)
        
        # Simulate some clicks
        button.trigger_callback('click')
        button.trigger_callback('click')
        button.trigger_callback('click')
        
        print("✅ Event system working")
        
        # Test animation manager
        manager = button._animation_manager
        print(f"✅ Animation manager active: {manager.get_active_count()} animations")
        
        print("\n🎉 All systems working perfectly!")
        print("\n💡 To see the visual demo, run:")
        print("   python examples/simple_example.py")
        print("   python examples/demo_tkinter.py")
        
        print("\n📦 Package ready for installation:")
        print("   pip install -e .")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the AnimatedWidgetsPack directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def run_gui_demo():
    """Run GUI demo if tkinter is available"""
    try:
        import tkinter as tk
        from animated_widgets_pack import AnimatedButton, WidgetConfig, ButtonStyle
        
        print("\n🖼️  Starting GUI demo...")
        
        # Create window
        root = tk.Tk()
        root.title("AnimatedWidgetsPack - Quick Demo")
        root.geometry("300x150")
        root.configure(bg="#ecf0f1")
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        pos_x = (root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        
        # Add title
        title = tk.Label(
            root, 
            text="AnimatedWidgetsPack", 
            font=("Arial", 14, "bold"),
            bg="#ecf0f1", 
            fg="#2c3e50"
        )
        title.pack(pady=20)
        
        # Create animated button
        config = WidgetConfig(width=180, height=45, border_radius=8)
        style = ButtonStyle(
            normal_color="#e74c3c",
            hover_color="#c0392b",
            pressed_color="#a93226"
        )
        
        button = AnimatedButton("Try Me! ✨", config, style)
        widget = button.render(root, "tkinter")
        widget.pack(pady=10)
        
        # Add click handler
        click_count = {"value": 0}
        
        def handle_click():
            click_count["value"] += 1
            if click_count["value"] % 3 == 0:
                button.pulse_animation(duration=0.6, scale_factor=1.2)
            button.set_text(f"Clicked {click_count['value']} times! 🎯")
        
        button.on_click(handle_click)
        
        # Instructions
        instructions = tk.Label(
            root,
            text="Hover and click to see smooth animations!",
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        instructions.pack(pady=5)
        
        print("✨ GUI demo running - close window to continue")
        root.mainloop()
        
    except ImportError:
        print("❌ Tkinter not available - skipping GUI demo")
    except Exception as e:
        print(f"❌ GUI demo error: {e}")

if __name__ == "__main__":
    print("🚀 Starting AnimatedWidgetsPack demonstration...\n")
    
    # Run console demo
    run_simple_demo()
    
    # Ask user if they want GUI demo
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        run_gui_demo()
    else:
        print("\n📱 Add --gui flag to see visual demo:")
        print("   python DEMO.py --gui")
    
    print("\n🎨 Demo complete! Thanks for trying AnimatedWidgetsPack!")