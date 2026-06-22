import json
import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Configurations & Styling
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("green")  # Built-in green theme matches #00AE42 styling nicely

DATA_FILE = 'data.json'
PRINTS_FILE = 'prints.json'


class PrintPathCMS:

    def __init__(self, root):
        self.root = root
        self.root.title("PrintPath Core Admin Engine")
        self.root.geometry("850x600")

        # Load Existing Databases
        self.item_data = self.load_json(DATA_FILE)
        self.order_data = self.load_json(PRINTS_FILE)

        # Track currently selected indices for editing
        self.current_item_index = None
        self.current_order_index = None

        # Tabview Controller
        self.tabview = ctk.CTkTabview(
            self.root, segmented_button_selected_color="#00AE42"
        )
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Initializing Tab Views
        self.tab_presets = self.tabview.add("Store Inventory (Presets)")
        self.tab_orders = self.tabview.add("Order Status Tracker")

        self.setup_presets_tab()
        self.setup_orders_tab()

    def load_json(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_json(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    # ==========================================
    # TAB 1: STORE PRESETS (data.json)
    # ==========================================
    def setup_presets_tab(self):
        # Configure layout inside preset grid
        self.tab_presets.grid_columnconfigure(1, weight=1)
        self.tab_presets.grid_rowconfigure(0, weight=1)

        # Left Column Frame: Items Listbox
        left_panel = ctk.CTkFrame(self.tab_presets, width=250)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            left_panel, text="Catalog Items", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Standard Tkinter Listbox wrapped inside a frame (needed for listing)
        self.item_listbox = tk.Listbox(
            left_panel,
            bg="#2A2A2A",
            fg="white",
            selectbackground="#00AE42",
            border=0,
            highlightthickness=0,
        )
        self.item_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.item_listbox.bind('<<ListboxSelect>>', self.on_item_select)

        # Modify actions buttons
        btn_panel = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_panel.pack(fill="x", pady=10, padx=10)
        ctk.CTkButton(
            btn_panel, text="New", width=80, command=self.clear_item_form
        ).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(
            btn_panel,
            text="Delete",
            width=80,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.delete_item,
        ).pack(side="right", expand=True, padx=2)

        # Right Column Frame: Inputs Form
        right_panel = ctk.CTkScrollableFrame(self.tab_presets)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.item_fields = {}
        labels = ['id', 'name', 'price', 'description', 'image', 'stripe_link']

        for i, label in enumerate(labels):
            ctk.CTkLabel(
                right_panel,
                text=f"{label.capitalize().replace('_', ' ')}:",
                font=ctk.CTkFont(size=13),
            ).grid(row=i * 2, column=0, sticky="w", padx=15, pady=(5, 0))
            entry = ctk.CTkEntry(right_panel, placeholder_text=f"Enter {label}")
            entry.grid(row=(i * 2) + 1, column=0, sticky="ew", padx=15, pady=(0, 10))
            self.item_fields[label] = entry

        right_panel.grid_columnconfigure(0, weight=1)

        # Main Dynamic Save Button
        ctk.CTkButton(
            right_panel,
            text="Save Product Entry",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#00AE42",
            hover_color="#008F36",
            command=self.save_item,
        ).grid(row=len(labels) * 2, column=0, pady=20, padx=15, sticky="ew")

        self.refresh_item_list()

    def refresh_item_list(self):
        self.item_listbox.delete(0, tk.END)
        for item in self.item_data:
            self.item_listbox.insert(tk.END, item['name'])

    def on_item_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_item_index = selection[0]
            item = self.item_data[self.current_item_index]
            
            # Clear text fields without stripping the listbox selection state
            for entry in self.item_fields.values():
                entry.delete(0, tk.END)
                
            for key in self.item_fields:
                self.item_fields[key].insert(0, str(item.get(key, '')))

    def clear_item_form(self):
        for entry in self.item_fields.values():
            entry.delete(0, tk.END)
        self.item_listbox.selection_clear(0, tk.END)
        self.current_item_index = None

    def save_item(self):
        new_item = {}
        for key, entry in self.item_fields.items():
            val = entry.get()
            if key == 'price':
                try:
                    val = float(val)
                except ValueError:
                    val = 0.0
            new_item[key] = val

        if not new_item['id'] or not new_item['name']:
            messagebox.showwarning("Error Parsing Data", "ID and Name fields are necessary.")
            return

        if self.current_item_index is not None:
            self.item_data[self.current_item_index] = new_item
        else:
            if any(i['id'] == new_item['id'] for i in self.item_data):
                messagebox.showwarning("Database Conflict", "Product variant ID already exists.")
                return
            self.item_data.append(new_item)

        self.save_json(DATA_FILE, self.item_data)
        self.refresh_item_list()
        self.clear_item_form()
        messagebox.showinfo("Success", "Catalog Entry updated successfully!")

    def delete_item(self):
        if self.current_item_index is not None:
            del self.item_data[self.current_item_index]
            self.save_json(DATA_FILE, self.item_data)
            self.refresh_item_list()
            self.clear_item_form()

    # ==========================================
    # TAB 2: ORDER PROCESSING SYSTEM (prints.json)
    # ==========================================
    def setup_orders_tab(self):
        self.tab_orders.grid_columnconfigure(1, weight=1)
        self.tab_orders.grid_rowconfigure(0, weight=1)

        # Left Column Panel: Orders List
        left_panel = ctk.CTkFrame(self.tab_orders, width=250)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            left_panel, text="Active Orders Tracker", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        self.order_listbox = tk.Listbox(
            left_panel,
            bg="#2A2A2A",
            fg="white",
            selectbackground="#00AE42",
            border=0,
            highlightthickness=0,
        )
        self.order_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.order_listbox.bind('<<ListboxSelect>>', self.on_order_select)

        btn_panel = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_panel.pack(fill="x", pady=10, padx=10)
        ctk.CTkButton(
            btn_panel, text="New Order", width=80, command=self.clear_order_form
        ).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(
            btn_panel,
            text="Delete",
            width=80,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.delete_order,
        ).pack(side="right", expand=True, padx=2)

        # Right Column Panel: Dynamic Order Forms
        right_panel = ctk.CTkFrame(self.tab_orders)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid_columnconfigure(0, weight=1)

        self.order_fields = {}

        # Fields Config
        ctk.CTkLabel(right_panel, text="Unique System Tracking ID (e.g., PP-1004):").grid(
            row=0, column=0, sticky="w", padx=20, pady=(10, 0)
        )
        self.order_fields['order_id'] = ctk.CTkEntry(
            right_panel, placeholder_text="PP-XXXX"
        )
        self.order_fields['order_id'].grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(right_panel, text="Student Name:").grid(
            row=2, column=0, sticky="w", padx=20, pady=(5, 0)
        )
        self.order_fields['name'] = ctk.CTkEntry(
            right_panel, placeholder_text="Enter customer name"
        )
        self.order_fields['name'].grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(right_panel, text="Print Item / Model Name:").grid(
            row=4, column=0, sticky="w", padx=20, pady=(5, 0)
        )
        self.order_fields['item_name'] = ctk.CTkEntry(
            right_panel, placeholder_text="E.g., Custom Drone Gear or Green Goblin Bust"
        )
        self.order_fields['item_name'].grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(right_panel, text="Production Pipeline Status:").grid(
            row=6, column=0, sticky="w", padx=20, pady=(5, 0)
        )
        status_options = ['PENDING', 'QUEUE', 'PRINTING', 'WAITING', 'DELIVERED']
        self.status_dropdown = ctk.CTkOptionMenu(
            right_panel, values=status_options, button_color="#00AE42", dropdown_hover_color="#008F36"
        )
        self.status_dropdown.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.status_dropdown.set('PENDING')

        # Action Execution Button
        ctk.CTkButton(
            right_panel,
            text="Sync Order & Status",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#00AE42",
            hover_color="#008F36",
            command=self.save_order,
        ).grid(row=8, column=0, pady=30, padx=20, sticky="ew")

        self.refresh_order_list()

    def refresh_order_list(self):
        self.order_listbox.delete(0, tk.END)
        for order in self.order_data:
            self.order_listbox.insert(
                tk.END, f"{order['order_id']} - {order['name']}"
            )

    def on_order_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_order_index = selection[0]
            order = self.order_data[self.current_order_index]
            
            # Clear text fields without stripping selection state
            for entry in self.order_fields.values():
                entry.delete(0, tk.END)
                
            self.order_fields['order_id'].insert(0, order.get('order_id', ''))
            self.order_fields['name'].insert(0, order.get('name', ''))
            self.order_fields['item_name'].insert(0, order.get('item_name', ''))
            self.status_dropdown.set(order.get('status', 'PENDING'))

    def clear_order_form(self):
        for entry in self.order_fields.values():
            entry.delete(0, tk.END)
        self.status_dropdown.set('PENDING')
        self.order_listbox.selection_clear(0, tk.END)
        self.current_order_index = None

    def save_order(self):
        new_order = {
            'order_id': self.order_fields['order_id'].get().upper().strip(),
            'name': self.order_fields['name'].get().strip(),
            'item_name': self.order_fields['item_name'].get().strip(),
            'status': self.status_dropdown.get(),
        }

        if not new_order['order_id'] or not new_order['name']:
            messagebox.showwarning("Validation Required", "Tracking ID and Student Name are mandated fields.")
            return

        if self.current_order_index is not None:
            self.order_data[self.current_order_index] = new_order
        else:
            if any(o['order_id'] == new_order['order_id'] for o in self.order_data):
                messagebox.showwarning("Registry Conflict", "This unique Order ID has already been assigned.")
                return
            self.order_data.append(new_order)

        self.save_json(PRINTS_FILE, self.order_data)
        self.refresh_order_list()
        self.clear_order_form()
        messagebox.showinfo("Success", "Order workflow pipeline updated!")

    def delete_order(self):
        if self.current_order_index is not None:
            del self.order_data[self.current_order_index]
            self.save_json(PRINTS_FILE, self.order_data)
            self.refresh_order_list()
            self.clear_order_form()


if __name__ == "__main__":
    root = ctk.CTk()
    app = PrintPathCMS(root)
    root.mainloop()