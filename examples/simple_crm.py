# examples/simple_crm.py
"""
Exemple d'application CRM simple utilisant AnimatedWidgetsPack
Démontre l'utilisation pratique des widgets dans une vraie application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime
from typing import Dict, List, Optional

from animated_widgets_pack.TextInput import TextInputStyle, TextInputType, AnimatedTextInput
from animated_widgets_pack.CheckBox import AnimatedCheckbox, CheckboxStyle
from animated_widgets_pack.Switch import AnimatedSwitch, SwitchAppearance
from animated_widgets_pack.core import WidgetConfig
from animated_widgets_pack.buttons import AnimatedButton, ButtonStyle

class Customer:
    """Modèle de données client"""
    
    def __init__(self, name: str, email: str, phone: str, company: str = "", active: bool = True):
        self.id = f"C{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.name = name
        self.email = email
        self.phone = phone
        self.company = company
        self.active = active
        self.created_date = datetime.datetime.now()
        self.last_contact = None
        self.notes = ""
        self.tags = []
    
    def to_dict(self) -> Dict:
        """Convertir en dictionnaire pour sérialisation"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'active': self.active,
            'created_date': self.created_date.isoformat(),
            'last_contact': self.last_contact.isoformat() if self.last_contact else None,
            'notes': self.notes,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Customer':
        """Créer depuis un dictionnaire"""
        customer = cls(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            company=data.get('company', ''),
            active=data.get('active', True)
        )
        customer.id = data['id']
        customer.created_date = datetime.datetime.fromisoformat(data['created_date'])
        if data.get('last_contact'):
            customer.last_contact = datetime.datetime.fromisoformat(data['last_contact'])
        customer.notes = data.get('notes', '')
        customer.tags = data.get('tags', [])
        return customer

class CustomerDatabase:
    """Base de données simple pour les clients"""
    
    def __init__(self, filename: str = "customers.json"):
        self.filename = filename
        self.customers: List[Customer] = []
        self.load_data()
    
    def load_data(self):
        """Charger les données depuis le fichier"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.customers = [Customer.from_dict(customer_data) for customer_data in data]
        except FileNotFoundError:
            self.customers = []
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            self.customers = []
    
    def save_data(self):
        """Sauvegarder les données dans le fichier"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                data = [customer.to_dict() for customer in self.customers]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def add_customer(self, customer: Customer):
        """Ajouter un nouveau client"""
        self.customers.append(customer)
        self.save_data()
    
    def update_customer(self, customer_id: str, customer: Customer):
        """Mettre à jour un client existant"""
        for i, c in enumerate(self.customers):
            if c.id == customer_id:
                customer.id = customer_id  # Conserver l'ID original
                self.customers[i] = customer
                self.save_data()
                return True
        return False
    
    def delete_customer(self, customer_id: str):
        """Supprimer un client"""
        self.customers = [c for c in self.customers if c.id != customer_id]
        self.save_data()
    
    def search_customers(self, query: str) -> List[Customer]:
        """Rechercher des clients"""
        if not query:
            return self.customers
        
        query = query.lower()
        results = []
        
        for customer in self.customers:
            if (query in customer.name.lower() or 
                query in customer.email.lower() or 
                query in customer.company.lower() or
                query in customer.phone):
                results.append(customer)
        
        return results

class CustomerFormDialog:
    """Dialog pour ajouter/modifier un client"""
    
    def __init__(self, parent, customer: Optional[Customer] = None):
        self.parent = parent
        self.customer = customer
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau Client" if not customer else "Modifier Client")
        self.dialog.geometry("500x600")
        self.dialog.configure(bg="#f8f9fa")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
        
        self.create_form()
        
        # If editing, populate fields
        if customer:
            self.populate_fields()
    
    def create_form(self):
        """Créer le formulaire"""
        # Configuration commune
        config = WidgetConfig(
            width=300,
            height=35,
            font_family="Arial",
            animation_duration=0.25
        )
        
        # Title
        title_label = tk.Label(
            self.dialog,
            text="Informations Client",
            font=("Arial", 16, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        title_label.pack(pady=(20, 30))
        
        # Form fields
        fields_frame = tk.Frame(self.dialog, bg="#f8f9fa")
        fields_frame.pack(padx=40, pady=10, fill="both", expand=True)
        
        # Name field
        self.name_input = AnimatedTextInput(
            placeholder="Nom complet du client",
            config=config,
            style=TextInputStyle(
                label_text="Nom *",
                helper_text="Nom et prénom du client"
            )
        )
        self.name_input.set_required().set_min_length(2)
        self.name_input.render(fields_frame, "tkinter").pack(pady=(0, 15), fill="x")
        
        # Email field
        self.email_input = AnimatedTextInput(
            placeholder="email@exemple.com",
            input_type=TextInputType.EMAIL,
            config=config,
            style=TextInputStyle(
                label_text="Email *",
                helper_text="Adresse email valide"
            )
        )
        self.email_input.set_required()
        self.email_input.render(fields_frame, "tkinter").pack(pady=(0, 15), fill="x")
        
        # Phone field
        self.phone_input = AnimatedTextInput(
            placeholder="+33 1 23 45 67 89",
            input_type=TextInputType.PHONE,
            config=config,
            style=TextInputStyle(
                label_text="Téléphone *",
                helper_text="Numéro de téléphone avec indicatif"
            )
        )
        self.phone_input.set_required()
        self.phone_input.render(fields_frame, "tkinter").pack(pady=(0, 15), fill="x")
        
        # Company field
        self.company_input = AnimatedTextInput(
            placeholder="Nom de l'entreprise",
            config=config,
            style=TextInputStyle(
                label_text="Entreprise",
                helper_text="Entreprise du client (optionnel)"
            )
        )
        self.company_input.render(fields_frame, "tkinter").pack(pady=(0, 15), fill="x")
        
        # Active status
        status_frame = tk.Frame(fields_frame, bg="#f8f9fa")
        status_frame.pack(pady=(10, 20), fill="x")
        
        status_label = tk.Label(
            status_frame,
            text="Statut du client:",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            fg="#34495e"
        )
        status_label.pack(anchor="w")
        
        self.active_checkbox = AnimatedCheckbox(
            label="Client actif",
            checked=True,
            style=CheckboxStyle()
        )
        self.active_checkbox.render(status_frame, "tkinter").pack(anchor="w", pady=(5, 0))
        
        # Notes field
        notes_label = tk.Label(
            fields_frame,
            text="Notes:",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            fg="#34495e"
        )
        notes_label.pack(anchor="w", pady=(10, 5))
        
        self.notes_text = tk.Text(
            fields_frame,
            height=4,
            bg="white",
            relief="solid",
            bd=1,
            font=("Arial", 10),
            wrap="word"
        )
        self.notes_text.pack(fill="x", pady=(0, 20))
        
        # Buttons
        buttons_frame = tk.Frame(self.dialog, bg="#f8f9fa")
        buttons_frame.pack(side="bottom", fill="x", padx=40, pady=20)
        
        # Cancel button
        cancel_btn = AnimatedButton(
            "Annuler",
            config=WidgetConfig(width=120, height=35),
            style=ButtonStyle(
                normal_color="#6c757d",
                hover_color="#5a6268",
                pressed_color="#495057"
            )
        )
        cancel_btn.on_click(self.cancel)
        cancel_btn.render(buttons_frame, "tkinter").pack(side="right", padx=(10, 0))
        
        # Save button
        save_text = "Modifier" if self.customer else "Ajouter"
        self.save_btn = AnimatedButton(
            save_text,
            config=WidgetConfig(width=120, height=35),
            style=ButtonStyle(
                normal_color="#28a745",
                hover_color="#218838",
                pressed_color="#1e7e34"
            )
        )
        self.save_btn.on_click(self.save)
        self.save_btn.render(buttons_frame, "tkinter").pack(side="right")
        
        # Validation feedback
        self.setup_validation()
    
    def setup_validation(self):
        """Configuration de la validation en temps réel"""
        def validate_form():
            is_valid = (self.name_input.is_valid() and 
                       self.email_input.is_valid() and 
                       self.phone_input.is_valid())
            
            # Update save button state
            if is_valid:
                self.save_btn.set_colors(normal="#28a745")
            else:
                self.save_btn.set_colors(normal="#dc3545")
        
        # Bind validation to input changes
        self.name_input.on_value_changed(lambda o, n: validate_form())
        self.email_input.on_value_changed(lambda o, n: validate_form())
        self.phone_input.on_value_changed(lambda o, n: validate_form())
    
    def populate_fields(self):
        """Remplir les champs avec les données du client"""
        if not self.customer:
            return
        
        self.name_input.set_value(self.customer.name)
        self.email_input.set_value(self.customer.email)
        self.phone_input.set_value(self.customer.phone)
        self.company_input.set_value(self.customer.company)
        self.active_checkbox.set_checked(self.customer.active, animate=False)
        self.notes_text.insert("1.0", self.customer.notes)
    
    def save(self):
        """Sauvegarder le client"""
        # Validate all fields
        if not (self.name_input.is_valid() and 
                self.email_input.is_valid() and 
                self.phone_input.is_valid()):
            
            # Show validation errors with animations
            if not self.name_input.is_valid():
                self.name_input.shake_animation() if hasattr(self.name_input, 'shake_animation') else None
            if not self.email_input.is_valid():
                self.email_input.shake_animation() if hasattr(self.email_input, 'shake_animation') else None
            if not self.phone_input.is_valid():
                self.phone_input.shake_animation() if hasattr(self.phone_input, 'shake_animation') else None
            
            messagebox.showerror("Erreur", "Veuillez corriger les erreurs dans le formulaire")
            return
        
        # Create or update customer
        if self.customer:
            # Update existing
            self.customer.name = self.name_input.get_value()
            self.customer.email = self.email_input.get_value()
            self.customer.phone = self.phone_input.get_value()
            self.customer.company = self.company_input.get_value()
            self.customer.active = self.active_checkbox.is_checked()
            self.customer.notes = self.notes_text.get("1.0", "end-1c")
            self.result = self.customer
        else:
            # Create new
            self.result = Customer(
                name=self.name_input.get_value(),
                email=self.email_input.get_value(),
                phone=self.phone_input.get_value(),
                company=self.company_input.get_value(),
                active=self.active_checkbox.is_checked()
            )
            self.result.notes = self.notes_text.get("1.0", "end-1c")
        
        # Success animation
        self.save_btn.flash_animation("#28a745")
        
        # Close dialog after animation
        self.dialog.after(300, self.close)
    
    def cancel(self):
        """Annuler et fermer"""
        self.result = None
        self.close()
    
    def close(self):
        """Fermer le dialog"""
        self.dialog.destroy()

class SimpleCRMApp:
    """Application CRM principale"""
    
    def __init__(self):
        self.db = CustomerDatabase()
        self.selected_customer = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Simple CRM - AnimatedWidgetsPack Demo")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f8f9fa")
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_ui()
        
        # Load initial data
        self.refresh_customer_list()
    
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
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_title = tk.Label(
            header_frame,
            text="📋 Simple CRM",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        header_title.pack(side="left", padx=20, pady=20)
        
        # Stats
        stats_frame = tk.Frame(header_frame, bg="#2c3e50")
        stats_frame.pack(side="right", padx=20, pady=20)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        self.stats_label.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel - Customer list
        left_panel = tk.Frame(main_frame, bg="#ffffff", relief="solid", bd=1)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Search section
        search_frame = tk.Frame(left_panel, bg="#ffffff")
        search_frame.pack(fill="x", padx=15, pady=15)
        
        search_label = tk.Label(
            search_frame,
            text="🔍 Rechercher des clients",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        search_label.pack(anchor="w", pady=(0, 10))
        
        self.search_input = AnimatedTextInput(
            placeholder="Nom, email, entreprise...",
            config=WidgetConfig(width=300, height=35),
            style=TextInputStyle()
        )
        self.search_input.on_value_changed(self.on_search)
        self.search_input.render(search_frame, "tkinter").pack(fill="x")
        
        # Customer list
        list_frame = tk.Frame(left_panel, bg="#ffffff")
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        list_label = tk.Label(
            list_frame,
            text="👥 Liste des clients",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        list_label.pack(anchor="w", pady=(0, 10))
        
        # Treeview for customer list
        columns = ('Name', 'Email', 'Company', 'Status')
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.customer_tree.heading('Name', text='Nom')
        self.customer_tree.heading('Email', text='Email')
        self.customer_tree.heading('Company', text='Entreprise')
        self.customer_tree.heading('Status', text='Statut')
        
        # Define column widths
        self.customer_tree.column('Name', width=150)
        self.customer_tree.column('Email', width=200)
        self.customer_tree.column('Company', width=150)
        self.customer_tree.column('Status', width=80)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.customer_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        
        # Right panel - Actions and details
        right_panel = tk.Frame(main_frame, bg="#ffffff", relief="solid", bd=1, width=300)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Actions section
        actions_frame = tk.Frame(right_panel, bg="#ffffff")
        actions_frame.pack(fill="x", padx=15, pady=15)
        
        actions_label = tk.Label(
            actions_frame,
            text="⚡ Actions",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        actions_label.pack(anchor="w", pady=(0, 15))
        
        # Action buttons
        btn_config = WidgetConfig(width=250, height=40)
        
        self.add_btn = AnimatedButton(
            "➕ Nouveau Client",
            config=btn_config,
            style=ButtonStyle(
                normal_color="#28a745",
                hover_color="#218838",
                pressed_color="#1e7e34"
            )
        )
        self.add_btn.on_click(self.add_customer)
        self.add_btn.render(actions_frame, "tkinter").pack(pady=(0, 10), fill="x")
        
        self.edit_btn = AnimatedButton(
            "✏️ Modifier",
            config=btn_config,
            style=ButtonStyle(
                normal_color="#007bff",
                hover_color="#0056b3",
                pressed_color="#004085"
            )
        )
        self.edit_btn.on_click(self.edit_customer)
        self.edit_btn.render(actions_frame, "tkinter").pack(pady=(0, 10), fill="x")
        
        self.delete_btn = AnimatedButton(
            "🗑️ Supprimer",
            config=btn_config,
            style=ButtonStyle(
                normal_color="#dc3545",
                hover_color="#c82333",
                pressed_color="#bd2130"
            )
        )
        self.delete_btn.on_click(self.delete_customer)
        self.delete_btn.render(actions_frame, "tkinter").pack(pady=(0, 10), fill="x")
        
        self.contact_btn = AnimatedButton(
            "📞 Marquer Contact",
            config=btn_config,
            style=ButtonStyle(
                normal_color="#17a2b8",
                hover_color="#138496",
                pressed_color="#0f6674"  
            )
        )
        self.contact_btn.on_click(self.mark_contact)
        self.contact_btn.render(actions_frame, "tkinter").pack(fill="x")
        
        # Initially disable edit/delete buttons
        self.update_action_buttons(False)
        
        # Customer details section
        details_frame = tk.Frame(right_panel, bg="#ffffff")
        details_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        details_label = tk.Label(
            details_frame,
            text="📄 Détails du client",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        )
        details_label.pack(anchor="w", pady=(0, 15))
        
        self.details_text = tk.Text(
            details_frame,
            bg="#f8f9fa",
            relief="solid",
            bd=1,
            font=("Arial", 10),
            wrap="word",
            state="disabled"
        )
        self.details_text.pack(fill="both", expand=True)
        
        # Update stats
        self.update_stats()
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        total = len(self.db.customers)
        active = len([c for c in self.db.customers if c.active])
        inactive = total - active
        
        self.stats_label.configure(
            text=f"Total: {total} | Actifs: {active} | Inactifs: {inactive}"
        )
    
    def refresh_customer_list(self, customers=None):
        """Actualiser la liste des clients"""
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Use provided customers or all customers
        if customers is None:
            customers = self.db.customers
        
        # Populate treeview
        for customer in customers:
            status = "✅ Actif" if customer.active else "❌ Inactif"
            self.customer_tree.insert('', 'end', values=(
                customer.name,
                customer.email,
                customer.company or "N/A",
                status
            ), tags=(customer.id,))
        
        # Update stats
        self.update_stats()
    
    def on_search(self, old_value, new_value):
        """Gérer la recherche"""
        if not new_value.strip():
            self.refresh_customer_list()
        else:
            results = self.db.search_customers(new_value)
            self.refresh_customer_list(results)
    
    def on_customer_select(self, event):
        """Gérer la sélection d'un client"""
        selection = self.customer_tree.selection()
        if not selection:
            self.selected_customer = None
            self.update_action_buttons(False)
            self.show_customer_details(None)
            return
        
        # Get selected customer
        item = selection[0]
        customer_id = self.customer_tree.item(item, 'tags')[0]
        self.selected_customer = next((c for c in self.db.customers if c.id == customer_id), None)
        
        self.update_action_buttons(True)
        self.show_customer_details(self.selected_customer)
    
    def update_action_buttons(self, enabled: bool):
        """Activer/désactiver les boutons d'action"""
        state = "normal" if enabled else "disabled"
        
        # Note: This is a simplified approach
        # In a full implementation, you'd modify the button's internal state
        if enabled:
            self.edit_btn.enable()
            self.delete_btn.enable()
            self.contact_btn.enable()
        else:
            self.edit_btn.disable()
            self.delete_btn.disable()
            self.contact_btn.disable()
    
    def show_customer_details(self, customer: Optional[Customer]):
        """Afficher les détails du client"""
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        
        if customer:
            created = customer.created_date.strftime("%d/%m/%Y %H:%M")
            last_contact = customer.last_contact.strftime("%d/%m/%Y %H:%M") if customer.last_contact else "Jamais"
            
            details = f"""ID: {customer.id}
            
📛 Nom: {customer.name}
📧 Email: {customer.email}
📞 Téléphone: {customer.phone}
🏢 Entreprise: {customer.company or 'N/A'}
✅ Statut: {'Actif' if customer.active else 'Inactif'}

📅 Créé le: {created}
📞 Dernier contact: {last_contact}

📝 Notes:
{customer.notes or 'Aucune note'}"""
            
            self.details_text.insert("1.0", details)
        else:
            self.details_text.insert("1.0", "Sélectionnez un client pour voir ses détails")
        
        self.details_text.configure(state="disabled")
    
    def add_customer(self):
        """Ajouter un nouveau client"""
        dialog = CustomerFormDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.db.add_customer(dialog.result)
            self.refresh_customer_list()
            
            # Success feedback
            self.add_btn.flash_animation("#28a745")
            messagebox.showinfo("Succès", f"Client '{dialog.result.name}' ajouté avec succès!")
    
    def edit_customer(self):
        """Modifier le client sélectionné"""
        if not self.selected_customer:
            return
        
        dialog = CustomerFormDialog(self.root, self.selected_customer)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.db.update_customer(self.selected_customer.id, dialog.result)
            self.selected_customer = dialog.result
            self.refresh_customer_list()
            self.show_customer_details(self.selected_customer)
            
            # Success feedback
            self.edit_btn.flash_animation("#007bff")
            messagebox.showinfo("Succès", f"Client '{dialog.result.name}' modifié avec succès!")
    
    def delete_customer(self):
        """Supprimer le client sélectionné"""
        if not self.selected_customer:
            return
        
        # Confirmation
        result = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le client '{self.selected_customer.name}' ?\n\nCette action est irréversible."
        )
        
        if result:
            self.db.delete_customer(self.selected_customer.id)
            self.selected_customer = None
            self.refresh_customer_list()
            self.update_action_buttons(False)
            self.show_customer_details(None)
            
            # Success feedback
            self.delete_btn.flash_animation("#dc3545")
            messagebox.showinfo("Succès", "Client supprimé avec succès!")
    
    def mark_contact(self):
        """Marquer un contact avec le client"""
        if not self.selected_customer:
            return
        
        self.selected_customer.last_contact = datetime.datetime.now()
        self.db.update_customer(self.selected_customer.id, self.selected_customer)
        self.show_customer_details(self.selected_customer)
        
        # Success feedback
        self.contact_btn.flash_animation("#17a2b8")
        messagebox.showinfo("Contact", f"Contact marqué pour '{self.selected_customer.name}'")
    
    def run(self):
        """Lancer l'application"""
        try:
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Show welcome message
            messagebox.showinfo(
                "Bienvenue", 
                "Bienvenue dans Simple CRM!\n\n"
                "Cette application démontre l'utilisation d'AnimatedWidgetsPack "
                "dans une vraie application de gestion de clients.\n\n"
                "Fonctionnalités:\n"
                "• Ajouter/modifier/supprimer des clients\n"
                "• Recherche en temps réel\n"
                "• Validation des formulaires\n"
                "• Animations fluides\n"
                "• Sauvegarde automatique"
            )
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
    
    def on_closing(self):
        """Gérer la fermeture de l'application"""
        try:
            # Save any pending changes
            self.db.save_data()
            
            # Show goodbye message
            messagebox.showinfo("Au revoir", "Données sauvegardées. À bientôt!")
            
            # Close application
            self.root.destroy()
            
        except Exception as e:
            print(f"Erreur lors de la fermeture: {e}")
            self.root.destroy()

def main():
    """Point d'entrée principal"""
    try:
        app = SimpleCRMApp()
        app.run()
    except Exception as e:
        print(f"Erreur fatale: {e}")
        messagebox.showerror("Erreur Fatale", f"Impossible de démarrer l'application: {e}")

if __name__ == "__main__":
    main()