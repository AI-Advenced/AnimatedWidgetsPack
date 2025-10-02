"""
Module textinput - Animated text input with validation and effects
"""

import re
import time
import threading
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional, List, Union
from enum import Enum
from .core import AnimatedWidget, WidgetConfig
from .animations import AnimationManager, AnimationConfig, EasingType
from .utils import ColorUtils, Color, Rectangle, Point

class TextInputType(Enum):
    """Text input types with different validation"""
    TEXT = "text"
    PASSWORD = "password"
    EMAIL = "email"
    NUMBER = "number"
    PHONE = "phone"
    URL = "url"
    SEARCH = "search"

class ValidationResult:
    """Result of input validation"""
    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message
        self.timestamp = time.time()

@dataclass
class TextInputStyle:
    """Text input specific styling"""
    normal_border_color: str = "#bdc3c7"
    focus_border_color: str = "#3498db"
    error_border_color: str = "#e74c3c"
    success_border_color: str = "#27ae60"
    disabled_border_color: str = "#ecf0f1"
    
    normal_background: str = "#ffffff"
    focus_background: str = "#ffffff"
    disabled_background: str = "#f8f9fa"
    
    text_color: str = "#2c3e50"
    placeholder_color: str = "#95a5a6"
    error_text_color: str = "#e74c3c"
    success_text_color: str = "#27ae60"
    
    border_width: int = 2
    border_radius: int = 8
    padding: tuple = (10, 15)
    
    # Animation properties
    focus_scale: float = 1.02
    focus_glow: bool = True
    focus_glow_color: str = "#3498db"
    focus_glow_size: int = 3
    
    # Label properties
    label_text: str = ""
    label_color: str = "#34495e"
    label_font_size: int = 12
    floating_label: bool = True
    
    # Helper text
    helper_text: str = ""
    helper_color: str = "#7f8c8d"
    show_character_count: bool = False
    
    # Icons
    prefix_icon: Optional[str] = None
    suffix_icon: Optional[str] = None
    show_password_toggle: bool = True  # For password inputs

class TextInputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return ValidationResult(True, "Email valide")
        return ValidationResult(False, "Format d'email invalide")
    
    @staticmethod
    def validate_phone(phone: str) -> ValidationResult:
        """Validate phone number"""
        # Remove all non-digit characters
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Check various phone formats
        patterns = [
            r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$',  # US format
            r'^\+?33[1-9]\d{8}$',  # French format
            r'^\+?[1-9]\d{1,14}$'  # International format
        ]
        
        for pattern in patterns:
            if re.match(pattern, clean_phone):
                return ValidationResult(True, "Numéro de téléphone valide")
        
        return ValidationResult(False, "Format de téléphone invalide")
    
    @staticmethod
    def validate_url(url: str) -> ValidationResult:
        """Validate URL format"""
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        if re.match(pattern, url):
            return ValidationResult(True, "URL valide")
        return ValidationResult(False, "Format d'URL invalide")
    
    @staticmethod
    def validate_number(value: str, min_val: float = None, max_val: float = None) -> ValidationResult:
        """Validate numeric input"""
        try:
            num = float(value)
            
            if min_val is not None and num < min_val:
                return ValidationResult(False, f"La valeur doit être supérieure à {min_val}")
            
            if max_val is not None and num > max_val:
                return ValidationResult(False, f"La valeur doit être inférieure à {max_val}")
            
            return ValidationResult(True, "Nombre valide")
        except ValueError:
            return ValidationResult(False, "Veuillez entrer un nombre valide")
    
    @staticmethod
    def validate_required(value: str) -> ValidationResult:
        """Validate required field"""
        if value.strip():
            return ValidationResult(True, "Champ requis rempli")
        return ValidationResult(False, "Ce champ est requis")
    
    @staticmethod
    def validate_min_length(value: str, min_length: int) -> ValidationResult:
        """Validate minimum length"""
        if len(value) >= min_length:
            return ValidationResult(True, f"Longueur minimale respectée ({min_length})")
        return ValidationResult(False, f"Minimum {min_length} caractères requis")
    
    @staticmethod
    def validate_max_length(value: str, max_length: int) -> ValidationResult:
        """Validate maximum length"""
        if len(value) <= max_length:
            return ValidationResult(True, f"Longueur maximale respectée ({max_length})")
        return ValidationResult(False, f"Maximum {max_length} caractères autorisés")
    
    @staticmethod
    def validate_pattern(value: str, pattern: str, message: str = "Format invalide") -> ValidationResult:
        """Validate against custom pattern"""
        if re.match(pattern, value):
            return ValidationResult(True, "Format valide")
        return ValidationResult(False, message)

class AnimatedTextInput(AnimatedWidget):
    """
    Animated text input with validation, focus effects and smooth transitions
    Supports multiple input types, floating labels, and real-time validation
    """
    
    def __init__(self, placeholder: str = "", input_type: TextInputType = TextInputType.TEXT,
                 config: Optional[WidgetConfig] = None, style: Optional[TextInputStyle] = None):
        super().__init__(config)
        
        self.style = style or TextInputStyle()
        self.input_type = input_type
        self.placeholder = placeholder
        
        # Internal state
        self._current_value = ""
        self._is_focused = False
        self._is_password_visible = False
        self._current_border_color = ColorUtils.parse_color(self.style.normal_border_color)
        self._current_background_color = ColorUtils.parse_color(self.style.normal_background)
        self._current_scale = 1.0
        self._current_glow_opacity = 0.0
        self._label_position = 1.0  # 0.0 = top (floating), 1.0 = center
        
        # Validation
        self._validators: List[Callable[[str], ValidationResult]] = []
        self._current_validation: Optional[ValidationResult] = None
        self._validation_debounce_timer: Optional[threading.Timer] = None
        
        # Animation manager
        self._animation_manager = AnimationManager()
        
        # GUI widget references
        self._gui_widget = None
        self._gui_framework = None
        self._label_widget = None
        self._helper_widget = None
        self._error_widget = None
        
        # Configuration
        self.required = False
        self.readonly = False
        self.min_length = 0
        self.max_length = 0
        self.min_value = None
        self.max_value = None
        self.custom_pattern = None
        self.custom_pattern_message = ""
        
        # Setup default validators based on input type
        self._setup_default_validators()
    
    def _setup_default_validators(self):
        """Setup default validators based on input type"""
        if self.input_type == TextInputType.EMAIL:
            self.add_validator(TextInputValidator.validate_email)
        elif self.input_type == TextInputType.PHONE:
            self.add_validator(TextInputValidator.validate_phone)
        elif self.input_type == TextInputType.URL:
            self.add_validator(TextInputValidator.validate_url)
        elif self.input_type == TextInputType.NUMBER:
            self.add_validator(lambda v: TextInputValidator.validate_number(v, self.min_value, self.max_value))
    
    def render(self, parent_widget, framework: str = "tkinter"):
        """
        Render the text input in the specified GUI framework
        Supported frameworks: 'tkinter', 'pyqt5'
        """
        self._gui_framework = framework
        
        if framework == "tkinter":
            return self._render_tkinter(parent_widget)
        elif framework == "pyqt5":
            return self._render_pyqt5(parent_widget)
        else:
            raise ValueError(f"Framework non supporté: {framework}")
    
    def _render_tkinter(self, parent):
        """Render with Tkinter"""
        import tkinter as tk
        from tkinter import ttk
        
        # Create container frame
        container = tk.Frame(parent, bg=parent.cget('bg') if hasattr(parent, 'cget') else '#f0f0f0')
        
        # Label (if specified)
        if self.style.label_text:
            self._label_widget = tk.Label(
                container,
                text=self.style.label_text,
                font=(self.config.font_family, self.style.label_font_size),
                fg=self.style.label_color,
                bg=container.cget('bg')
            )
            if not self.style.floating_label:
                self._label_widget.pack(anchor="w", pady=(0, 5))
        
        # Input field frame for border effects
        input_frame = tk.Frame(
            container,
            bg=self.style.normal_border_color,
            relief="flat",
            bd=self.style.border_width
        )
        input_frame.pack(fill="x", pady=2)
        
        # Create the actual input widget
        if self.input_type == TextInputType.PASSWORD:
            self._gui_widget = tk.Entry(
                input_frame,
                show="*" if not self._is_password_visible else "",
                font=(self.config.font_family, self.config.font_size),
                fg=self.style.text_color,
                bg=self.style.normal_background,
                insertbackground=self.style.focus_border_color,
                relief="flat",
                bd=0
            )
        else:
            self._gui_widget = tk.Entry(
                input_frame,
                font=(self.config.font_family, self.config.font_size),
                fg=self.style.text_color,
                bg=self.style.normal_background,
                insertbackground=self.style.focus_border_color,
                relief="flat",
                bd=0
            )
        
        # Set placeholder-like behavior
        if self.placeholder:
            self._setup_placeholder_behavior()
        
        self._gui_widget.pack(fill="both", expand=True, padx=self.style.padding[1], pady=self.style.padding[0])
        
        # Bind events
        self._gui_widget.bind("<FocusIn>", self._on_focus_in)
        self._gui_widget.bind("<FocusOut>", self._on_focus_out)
        self._gui_widget.bind("<KeyRelease>", self._on_text_changed)
        self._gui_widget.bind("<Button-1>", self._on_click)
        
        # Helper text
        if self.style.helper_text:
            self._helper_widget = tk.Label(
                container,
                text=self.style.helper_text,
                font=(self.config.font_family, self.style.label_font_size - 1),
                fg=self.style.helper_color,
                bg=container.cget('bg')
            )
            self._helper_widget.pack(anchor="w", pady=(2, 0))
        
        # Error message label (initially hidden)
        self._error_widget = tk.Label(
            container,
            text="",
            font=(self.config.font_family, self.style.label_font_size - 1),
            fg=self.style.error_text_color,
            bg=container.cget('bg')
        )
        
        # Store input frame reference for border color changes
        self._input_frame = input_frame
        
        return container
    
    def _render_pyqt5(self, parent):
        """Render with PyQt5"""
        try:
            from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel
            from PyQt5.QtCore import Qt, QTimer
            from PyQt5.QtGui import QFont
        except ImportError:
            raise ImportError("PyQt5 non installé. Installez avec: pip install PyQt5")
        
        # Create container widget
        container = QWidget(parent)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Label
        if self.style.label_text:
            self._label_widget = QLabel(self.style.label_text)
            self._label_widget.setFont(QFont(self.config.font_family, self.style.label_font_size))
            if not self.style.floating_label:
                layout.addWidget(self._label_widget)
        
        # Input field
        self._gui_widget = QLineEdit()
        self._gui_widget.setPlaceholderText(self.placeholder)
        self._gui_widget.setFont(QFont(self.config.font_family, self.config.font_size))
        
        if self.input_type == TextInputType.PASSWORD:
            self._gui_widget.setEchoMode(QLineEdit.Password if not self._is_password_visible else QLineEdit.Normal)
        
        # Apply initial styling
        self._update_pyqt5_style()
        
        layout.addWidget(self._gui_widget)
        
        # Bind events
        self._gui_widget.focusInEvent = self._on_focus_in
        self._gui_widget.focusOutEvent = self._on_focus_out
        self._gui_widget.textChanged.connect(self._on_text_changed)
        
        # Helper text
        if self.style.helper_text:
            self._helper_widget = QLabel(self.style.helper_text)
            self._helper_widget.setFont(QFont(self.config.font_family, self.style.label_font_size - 1))
            layout.addWidget(self._helper_widget)
        
        # Error message label
        self._error_widget = QLabel("")
        self._error_widget.setFont(QFont(self.config.font_family, self.style.label_font_size - 1))
        self._error_widget.hide()
        layout.addWidget(self._error_widget)
        
        return container
    
    def _setup_placeholder_behavior(self):
        """Setup placeholder-like behavior for Tkinter"""
        def on_focus_in(event):
            if self._gui_widget.get() == self.placeholder:
                self._gui_widget.delete(0, "end")
                self._gui_widget.configure(fg=self.style.text_color)
        
        def on_focus_out(event):
            if not self._gui_widget.get():
                self._gui_widget.insert(0, self.placeholder)
                self._gui_widget.configure(fg=self.style.placeholder_color)
        
        # Set initial placeholder
        self._gui_widget.insert(0, self.placeholder)
        self._gui_widget.configure(fg=self.style.placeholder_color)
        
        # Override focus events
        original_focus_in = self._gui_widget.bind("<FocusIn>")
        original_focus_out = self._gui_widget.bind("<FocusOut>")
        
        self._gui_widget.bind("<FocusIn>", lambda e: [on_focus_in(e), self._on_focus_in(e)])
        self._gui_widget.bind("<FocusOut>", lambda e: [on_focus_out(e), self._on_focus_out(e)])
    
    def _update_pyqt5_style(self):
        """Update PyQt5 styling"""
        if self._gui_framework != "pyqt5" or not self._gui_widget:
            return
        
        border_color = self._current_border_color.to_hex()
        bg_color = self._current_background_color.to_hex()
        
        style = f"""
        QLineEdit {{
            border: {self.style.border_width}px solid {border_color};
            border-radius: {self.style.border_radius}px;
            padding: {self.style.padding[0]}px {self.style.padding[1]}px;
            background-color: {bg_color};
            color: {self.style.text_color};
            font-family: {self.config.font_family};
            font-size: {self.config.font_size}px;
        }}
        QLineEdit:focus {{
            border-color: {self.style.focus_border_color};
            background-color: {self.style.focus_background};
        }}
        QLineEdit:disabled {{
            border-color: {self.style.disabled_border_color};
            background-color: {self.style.disabled_background};
            color: #999999;
        }}
        """
        
        self._gui_widget.setStyleSheet(style)
    
    def _on_focus_in(self, event=None):
        """Handle focus in event"""
        if self.get_state() == "disabled":
            return
        
        self._is_focused = True
        self.set_state("focus")
        self.trigger_callback('focus_in')
        
        # Animate to focus state
        self._animate_to_focus_state()
        
        # Animate floating label if enabled
        if self.style.floating_label and self.style.label_text:
            self._animate_floating_label(True)
    
    def _on_focus_out(self, event=None):
        """Handle focus out event"""
        if self.get_state() == "disabled":
            return
        
        self._is_focused = False
        
        # Validate input
        self._validate_input()
        
        # Determine new state based on validation
        if self._current_validation and not self._current_validation.is_valid:
            self.set_state("error")
        elif self._current_validation and self._current_validation.is_valid and self.get_value():
            self.set_state("success")
        else:
            self.set_state("normal")
        
        self.trigger_callback('focus_out')
        
        # Animate to normal state
        self._animate_to_normal_state()
        
        # Animate floating label
        if self.style.floating_label and self.style.label_text:
            has_value = bool(self.get_value().strip())
            self._animate_floating_label(has_value)
    
    def _on_text_changed(self, event=None):
        """Handle text change event"""
        if self._gui_framework == "tkinter":
            new_value = self._gui_widget.get()
            if new_value == self.placeholder:
                new_value = ""
        else:  # PyQt5
            new_value = self._gui_widget.text()
        
        old_value = self._current_value
        self._current_value = new_value
        
        # Trigger value changed callback
        self.trigger_callback('value_changed', old_value, new_value)
        
        # Debounced validation
        self._schedule_validation()
        
        # Update character count if enabled
        if self.style.show_character_count:
            self._update_character_count()
    
    def _on_click(self, event=None):
        """Handle click event"""
        self.trigger_callback('click')
    
    def _animate_to_focus_state(self):
        """Animate to focus state"""
        # Border color animation
        start_color = self._current_border_color
        end_color = ColorUtils.parse_color(self.style.focus_border_color)
        self._animate_color_transition("border", start_color, end_color)
        
        # Background color animation
        start_bg = self._current_background_color
        end_bg = ColorUtils.parse_color(self.style.focus_background)
        self._animate_color_transition("background", start_bg, end_bg)
        
        # Scale animation
        if self.style.focus_scale != 1.0:
            self._animation_manager.animate(
                "scale",
                self._current_scale,
                self.style.focus_scale,
                lambda value: self._update_scale(value),
                AnimationConfig(duration=0.2, easing=EasingType.EASE_OUT_QUAD)
            )
        
        # Glow animation
        if self.style.focus_glow:
            self._animation_manager.animate(
                "glow",
                self._current_glow_opacity,
                1.0,
                lambda value: self._update_glow(value),
                AnimationConfig(duration=0.3, easing=EasingType.EASE_OUT_QUAD)
            )
    
    def _animate_to_normal_state(self):
        """Animate to normal state"""
        # Determine target colors based on validation state
        if self.get_state() == "error":
            border_color = self.style.error_border_color
            bg_color = self.style.normal_background
        elif self.get_state() == "success":
            border_color = self.style.success_border_color
            bg_color = self.style.normal_background
        else:
            border_color = self.style.normal_border_color
            bg_color = self.style.normal_background
        
        # Border color animation
        start_color = self._current_border_color
        end_color = ColorUtils.parse_color(border_color)
        self._animate_color_transition("border", start_color, end_color)
        
        # Background color animation
        start_bg = self._current_background_color
        end_bg = ColorUtils.parse_color(bg_color)
        self._animate_color_transition("background", start_bg, end_bg)
        
        # Scale animation back to normal
        self._animation_manager.animate(
            "scale",
            self._current_scale,
            1.0,
            lambda value: self._update_scale(value),
            AnimationConfig(duration=0.2, easing=EasingType.EASE_OUT_QUAD)
        )
        
        # Glow fade out
        if self.style.focus_glow:
            self._animation_manager.animate(
                "glow",
                self._current_glow_opacity,
                0.0,
                lambda value: self._update_glow(value),
                AnimationConfig(duration=0.3, easing=EasingType.EASE_OUT_QUAD)
            )
    
    def _animate_floating_label(self, to_top: bool):
        """Animate floating label position"""
        if not self.style.floating_label or not self._label_widget:
            return
        
        target_position = 0.0 if to_top else 1.0
        
        self._animation_manager.animate(
            "label_position",
            self._label_position,
            target_position,
            lambda value: self._update_label_position(value),
            AnimationConfig(duration=0.25, easing=EasingType.EASE_OUT_CUBIC)
        )
    
    def _animate_color_transition(self, property_name: str, start_color: Color, end_color: Color):
        """Animate color transition"""
        def update_color(progress: float):
            current_color = ColorUtils.interpolate_colors(start_color, end_color, progress)
            
            if property_name == "border":
                self._current_border_color = current_color
            elif property_name == "background":
                self._current_background_color = current_color
            
            self.update_appearance()
        
        self._animation_manager.animate(
            f"color_{property_name}",
            0.0,
            1.0,
            update_color,
            AnimationConfig(duration=0.25, easing=EasingType.EASE_OUT_CUBIC)
        )
    
    def _update_scale(self, scale_value: float):
        """Update input scale"""
        self._current_scale = scale_value
        # Implementation depends on GUI framework
        # For now, store value for future use
    
    def _update_glow(self, opacity: float):
        """Update glow effect"""
        self._current_glow_opacity = opacity
        # Implementation depends on GUI framework
        # Could add box-shadow effect or similar
    
    def _update_label_position(self, position: float):
        """Update floating label position"""
        self._label_position = position
        
        if self._gui_framework == "tkinter" and self._label_widget:
            # Animate label position and size
            if position < 0.5:  # Moving to top
                font_size = int(self.style.label_font_size * 0.85)
                self._label_widget.configure(font=(self.config.font_family, font_size))
            else:  # Moving to center
                self._label_widget.configure(font=(self.config.font_family, self.style.label_font_size))
    
    def update_appearance(self):
        """Update input appearance"""
        if not self._gui_widget:
            return
        
        if self._gui_framework == "tkinter":
            if hasattr(self, '_input_frame'):
                self._input_frame.configure(bg=self._current_border_color.to_hex())
            self._gui_widget.configure(bg=self._current_background_color.to_hex())
        elif self._gui_framework == "pyqt5":
            self._update_pyqt5_style()
    
    def _validate_input(self):
        """Validate current input value"""
        if not self._validators:
            return
        
        value = self.get_value()
        
        # Run all validators
        for validator in self._validators:
            try:
                result = validator(value)
                if not result.is_valid:
                    self._current_validation = result
                    self._show_error_message(result.message)
                    return
            except Exception as e:
                result = ValidationResult(False, f"Erreur de validation: {str(e)}")
                self._current_validation = result
                self._show_error_message(result.message)
                return
        
        # All validations passed
        self._current_validation = ValidationResult(True, "Validation réussie")
        self._hide_error_message()
    
    def _schedule_validation(self):
        """Schedule validation with debounce"""
        if self._validation_debounce_timer:
            self._validation_debounce_timer.cancel()
        
        self._validation_debounce_timer = threading.Timer(0.5, self._validate_input)
        self._validation_debounce_timer.start()
    
    def _show_error_message(self, message: str):
        """Show error message"""
        if self._error_widget:
            if self._gui_framework == "tkinter":
                self._error_widget.configure(text=message)
                self._error_widget.pack(anchor="w", pady=(2, 0))
            else:  # PyQt5
                self._error_widget.setText(message)
                self._error_widget.show()
    
    def _hide_error_message(self):
        """Hide error message"""
        if self._error_widget:
            if self._gui_framework == "tkinter":
                self._error_widget.pack_forget()
            else:  # PyQt5
                self._error_widget.hide()
    
    def _update_character_count(self):
        """Update character count display"""
        if not self.style.show_character_count:
            return
        
        current_length = len(self.get_value())
        max_length = self.max_length if self.max_length > 0 else "∞"
        
        count_text = f"{current_length}/{max_length}"
        
        if self._helper_widget:
            base_text = self.style.helper_text
            if base_text:
                full_text = f"{base_text} ({count_text})"
            else:
                full_text = count_text
            
            if self._gui_framework == "tkinter":
                self._helper_widget.configure(text=full_text)
            else:  # PyQt5
                self._helper_widget.setText(full_text)
    
    def add_validator(self, validator: Callable[[str], ValidationResult]):
        """Add a custom validator"""
        self._validators.append(validator)
        return self
    
    def set_required(self, required: bool = True):
        """Set field as required"""
        self.required = required
        if required:
            self.add_validator(TextInputValidator.validate_required)
        return self
    
    def set_min_length(self, min_length: int):
        """Set minimum length validation"""
        self.min_length = min_length
        self.add_validator(lambda v: TextInputValidator.validate_min_length(v, min_length))
        return self
    
    def set_max_length(self, max_length: int):
        """Set maximum length validation"""
        self.max_length = max_length
        self.add_validator(lambda v: TextInputValidator.validate_max_length(v, max_length))
        return self
    
    def set_pattern(self, pattern: str, message: str = "Format invalide"):
        """Set custom pattern validation"""
        self.custom_pattern = pattern
        self.custom_pattern_message = message
        self.add_validator(lambda v: TextInputValidator.validate_pattern(v, pattern, message))
        return self
    
    def set_number_range(self, min_val: float = None, max_val: float = None):
        """Set number range for numeric inputs"""
        if self.input_type != TextInputType.NUMBER:
            raise ValueError("La validation numérique n'est disponible que pour les champs NUMBER")
        
        self.min_value = min_val
        self.max_value = max_val
        # Re-setup validator with new range
        self._validators = [v for v in self._validators if "validate_number" not in str(v)]
        self.add_validator(lambda v: TextInputValidator.validate_number(v, min_val, max_val))
        return self
    
    def get_value(self) -> str:
        """Get current input value"""
        if self._gui_widget:
            if self._gui_framework == "tkinter":
                value = self._gui_widget.get()
                if value == self.placeholder:
                    return ""
                return value
            else:  # PyQt5
                return self._gui_widget.text()
        return self._current_value
    
    def set_value(self, value: str):
        """Set input value"""
        self._current_value = value
        if self._gui_widget:
            if self._gui_framework == "tkinter":
                self._gui_widget.delete(0, "end")
                self._gui_widget.insert(0, value)
            else:  # PyQt5
                self._gui_widget.setText(value)
        
        # Trigger validation
        self._validate_input()
    
    def clear(self):
        """Clear input value"""
        self.set_value("")
    
    def is_valid(self) -> bool:
        """Check if current input is valid"""
        self._validate_input()
        return self._current_validation is None or self._current_validation.is_valid
    
    def get_validation_message(self) -> str:
        """Get current validation message"""
        if self._current_validation:
            return self._current_validation.message
        return ""
    
    def focus(self):
        """Set focus to input"""
        if self._gui_widget:
            self._gui_widget.focus_set() if self._gui_framework == "tkinter" else self._gui_widget.setFocus()
    
    def toggle_password_visibility(self):
        """Toggle password visibility (for password inputs)"""
        if self.input_type != TextInputType.PASSWORD:
            return
        
        self._is_password_visible = not self._is_password_visible
        
        if self._gui_widget:
            if self._gui_framework == "tkinter":
                show_char = "" if self._is_password_visible else "*"
                self._gui_widget.configure(show=show_char)
            else:  # PyQt5
                from PyQt5.QtWidgets import QLineEdit
                mode = QLineEdit.Normal if self._is_password_visible else QLineEdit.Password
                self._gui_widget.setEchoMode(mode)
    
    def shake_animation(self, duration: float = 0.6):
        """Create shake animation for error feedback"""
        def shake_update(progress):
            offset = math.sin(progress * math.pi * 6) * 10 * (1 - progress)
            # Apply horizontal offset (implementation depends on framework)
            self._apply_shake_offset(offset)
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_OUT_CUBIC)
        self._animation_manager.animate("shake", 0.0, 1.0, shake_update, config)
    
    def _apply_shake_offset(self, offset: float):
        """Apply shake offset (framework-specific implementation)"""
        pass  # Implementation depends on GUI framework capabilities
    
    def pulse_animation(self, duration: float = 1.0):
        """Create pulse animation for focus feedback"""
        def pulse_update(progress):
            scale = 1.0 + 0.05 * math.sin(progress * math.pi * 2)
            self._update_scale(scale)
        
        config = AnimationConfig(
            duration=duration,
            easing=EasingType.EASE_IN_OUT_QUAD,
            repeat_count=2
        )
        self._animation_manager.animate("pulse", 0.0, 1.0, pulse_update, config)
    
    def highlight_animation(self, color: str = "#f1c40f", duration: float = 0.8):
        """Create highlight animation"""
        original_bg = self._current_background_color
        highlight_color = ColorUtils.parse_color(color)
        
        def highlight_update(progress):
            if progress <= 0.5:
                # Fade to highlight color
                current = ColorUtils.interpolate_colors(original_bg, highlight_color, progress * 2)
            else:
                # Fade back to original
                current = ColorUtils.interpolate_colors(highlight_color, original_bg, (progress - 0.5) * 2)
            
            self._current_background_color = current
            self.update_appearance()
        
        config = AnimationConfig(duration=duration, easing=EasingType.EASE_IN_OUT_QUAD)
        self._animation_manager.animate("highlight", 0.0, 1.0, highlight_update, config)
    
    def on_value_changed(self, callback: Callable):
        """Set callback for value changes"""
        self.bind_callback('value_changed', callback)
        return self
    
    def on_focus_in(self, callback: Callable):
        """Set callback for focus in"""
        self.bind_callback('focus_in', callback)
        return self
    
    def on_focus_out(self, callback: Callable):
        """Set callback for focus out"""
        self.bind_callback('focus_out', callback)
        return self
    
    def on_validation_error(self, callback: Callable):
        """Set callback for validation errors"""
        self.bind_callback('validation_error', callback)
        return self
    
    def stop_all_animations(self):
        """Stop all input animations"""
        self._animation_manager.stop_all_animations()
        super().stop_all_animations()
    
    def __del__(self):
        """Cleanup when input is destroyed"""
        if hasattr(self, '_validation_debounce_timer') and self._validation_debounce_timer:
            self._validation_debounce_timer.cancel()
        
        if hasattr(self, '_animation_manager'):
            self._animation_manager.stop_all_animations()