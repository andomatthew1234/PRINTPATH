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
FILAMENT_FILE = 'data/filament.json'


class PrintPathCMS:

    def __init__(self, root):
        self.root = root
        self.root.title("PrintPath Core Admin Engine")
        self.root.geometry("900x650")

        # Ensure data directory exists for filament.json
        os.makedirs(os.path.dirname(FILAMENT_FILE), exist_ok=True)

        # Load Existing Databases
        self.item_data = self.load_json(DATA_FILE)
        self.order_data = self.load_json(PRINTS_FILE)
        self.filament_data = self.load_json(FILAMENT_FILE)

        # Track currently selected indices for editing
        self.current_item_index = None
        self.current_order_index = None
        self.current_filament_index = None

        # Tabview Controller
        self.tabview = ctk.CTkTabview(
            self.root, segmented_button_selected_color="#00AE42"
        )
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Initializing Tab Views
        self.tab_presets = self.tabview.add("Store Inventory (Presets)")
        self.tab_orders = self.tabview.add("Order Status Tracker")
        self.tab_filament = self.tabview.add("Filament Status")

        self.setup_presets_tab()
        self.setup_orders_tab()
        self.setup_filament_tab()

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
        self.tab_presets.grid_columnconfigure(1, weight=1)
        self.tab_presets.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(self.tab_presets, width=250)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            left_panel, text="Catalog Items", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        self.item_listbox = tk.Listbox(
            left_panel, bg="#2A2A2A", fg="white", selectbackground="#00AE42", border=0, highlightthickness=0
        )
        self.item_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.item_listbox.bind('<<ListboxSelect>>', self.on_item_select)

        btn_panel = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_panel.pack(fill="x", pady=10, padx=10)
        ctk.CTkButton(btn_panel, text="New", width=80, command=self.clear_item_form).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(btn_panel, text="Delete", width=80, fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_item).pack(side="right", expand=True, padx=2)

        right_panel = ctk.CTkScrollableFrame(self.tab_presets)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.item_fields = {}
        labels = ['id', 'name', 'price', 'description', 'image', 'stripe_link']

        for i, label in enumerate(labels):
            ctk.CTkLabel(right_panel, text=f"{label.capitalize().replace('_', ' ')}:", font=ctk.CTkFont(size=13)).grid(row=i * 2, column=0, sticky="w", padx=15, pady=(5, 0))
            entry = ctk.CTkEntry(right_panel, placeholder_text=f"Enter {label}")
            entry.grid(row=(i * 2) + 1, column=0, sticky="ew", padx=15, pady=(0, 10))
            self.item_fields[label] = entry

        right_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            right_panel, text="Save Product Entry", font=ctk.CTkFont(weight="bold"), fg_color="#00AE42", hover_color="#008F36", command=self.save_item
        ).grid(row=len(labels) * 2, column=0, pady=20, padx=15, sticky="ew")

        self.refresh_item_list()

    def refresh_item_list(self):
        self.item_listbox.delete(0, tk.END)
        for item in self.item_data:
            self.item_listbox.insert(tk.END, item.get('name', 'Unnamed'))

    def on_item_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_item_index = selection[0]
            item = self.item_data[self.current_item_index]
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
                try: val = float(val)
                except ValueError: val = 0.0
            new_item[key] = val

        if not new_item['id'] or not new_item['name']:
            messagebox.showwarning("Error Parsing Data", "ID and Name fields are necessary.")
            return

        if self.current_item_index is not None:
            self.item_data[self.current_item_index] = new_item
        else:
            if any(i.get('id') == new_item['id'] for i in self.item_data):
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

        left_panel = ctk.CTkFrame(self.tab_orders, width=250)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(left_panel, text="Active Orders Tracker", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        self.order_listbox = tk.Listbox(
            left_panel, bg="#2A2A2A", fg="white", selectbackground="#00AE42", border=0, highlightthickness=0
        )
        self.order_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.order_listbox.bind('<<ListboxSelect>>', self.on_order_select)

        btn_panel = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_panel.pack(fill="x", pady=10, padx=10)
        ctk.CTkButton(btn_panel, text="New Order", width=80, command=self.clear_order_form).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(btn_panel, text="Delete", width=80, fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_order).pack(side="right", expand=True, padx=2)

        right_panel = ctk.CTkFrame(self.tab_orders)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid_columnconfigure(0, weight=1)

        self.order_fields = {}

        ctk.CTkLabel(right_panel, text="Unique System Tracking ID (e.g., PP-1004):").grid(row=0, column=0, sticky="w", padx=20, pady=(10, 0))
        self.order_fields['order_id'] = ctk.CTkEntry(right_panel, placeholder_text="PP-XXXX")
        self.order_fields['order_id'].grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(right_panel, text="Student Name:").grid(row=2, column=0, sticky="w", padx=20, pady=(5, 0))
        self.order_fields['name'] = ctk.CTkEntry(right_panel, placeholder_text="Enter customer name")
        self.order_fields['name'].grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(right_panel, text="Print Item / Model Name:").grid(row=4, column=0, sticky="w", padx=20, pady=(5, 0))
        self.order_fields['item_name'] = ctk.CTkEntry(right_panel, placeholder_text="E.g., Custom Drone Gear")
        self.order_fields['item_name'].grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(right_panel, text="Production Pipeline Status:").grid(row=6, column=0, sticky="w", padx=20, pady=(5, 0))
        status_options = ['PENDING', 'QUEUE', 'PRINTING', 'WAITING', 'DELIVERED']
        self.status_dropdown = ctk.CTkOptionMenu(right_panel, values=status_options, button_color="#00AE42", dropdown_hover_color="#008F36")
        self.status_dropdown.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.status_dropdown.set('PENDING')

        ctk.CTkButton(
            right_panel, text="Sync Order & Status", font=ctk.CTkFont(weight="bold"), fg_color="#00AE42", hover_color="#008F36", command=self.save_order
        ).grid(row=8, column=0, pady=30, padx=20, sticky="ew")

        self.refresh_order_list()

    def refresh_order_list(self):
        self.order_listbox.delete(0, tk.END)
        for order in self.order_data:
            self.order_listbox.insert(tk.END, f"{order.get('order_id', 'ID')} - {order.get('name', 'Name')}")

    def on_order_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_order_index = selection[0]
            order = self.order_data[self.current_order_index]
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
            if any(o.get('order_id') == new_order['order_id'] for o in self.order_data):
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

    # ==========================================
    # TAB 3: FILAMENT STATUS (data/filament.json)
    # ==========================================
    def setup_filament_tab(self):
        self.tab_filament.grid_columnconfigure(1, weight=1)
        self.tab_filament.grid_rowconfigure(0, weight=1)

        # Left Column Panel: Filament List
        left_panel = ctk.CTkFrame(self.tab_filament, width=250)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            left_panel, text="Filament Inventory", font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        self.filament_listbox = tk.Listbox(
            left_panel,
            bg="#2A2A2A",
            fg="white",
            selectbackground="#00AE42",
            border=0,
            highlightthickness=0,
        )
        self.filament_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.filament_listbox.bind('<<ListboxSelect>>', self.on_filament_select)

        btn_panel = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_panel.pack(fill="x", pady=10, padx=10)
        ctk.CTkButton(
            btn_panel, text="New Material", width=80, command=self.clear_filament_form
        ).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(
            btn_panel,
            text="Delete",
            width=80,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=self.delete_filament,
        ).pack(side="right", expand=True, padx=2)

        # Right Column Panel: Dynamic Filament Forms
        right_panel = ctk.CTkScrollableFrame(self.tab_filament)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_panel.grid_columnconfigure(0, weight=1)

        self.filament_fields = {}

        # Fields Config
        ctk.CTkLabel(right_panel, text="System ID (e.g., pla-black):").grid(row=0, column=0, sticky="w", padx=20, pady=(10, 0))
        self.filament_fields['id'] = ctk.CTkEntry(right_panel, placeholder_text="Enter internal ID")
        self.filament_fields['id'].grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(right_panel, text="Display Name (e.g., Matte Black PLA):").grid(row=2, column=0, sticky="w", padx=20, pady=(5, 0))
        self.filament_fields['name'] = ctk.CTkEntry(right_panel, placeholder_text="Enter descriptive name")
        self.filament_fields['name'].grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(right_panel, text="Material Type:").grid(row=4, column=0, sticky="w", padx=20, pady=(5, 0))
        material_options = ['PLA', 'PLA+', 'PETG', 'ABS', 'ASA', 'TPU', 'Nylon', 'Silk PLA', 'Resin']
        self.material_dropdown = ctk.CTkOptionMenu(
            right_panel, values=material_options, button_color="#00AE42", dropdown_hover_color="#008F36"
        )
        self.material_dropdown.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.material_dropdown.set('PLA')

        # Hex Color Input with Visual Swatch Preview
        hex_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        hex_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(5, 0))
        hex_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hex_frame, text="Color Hex Code (e.g., #222222):").grid(row=0, column=0, sticky="w")
        self.filament_fields['color_hex'] = ctk.CTkEntry(hex_frame, placeholder_text="#HexCode")
        self.filament_fields['color_hex'].grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Color preview square
        self.color_preview = ctk.CTkFrame(hex_frame, width=30, height=30, border_width=2, border_color="#555")
        self.color_preview.grid(row=1, column=1, padx=(10, 0), pady=(0, 10))
        # Bind key release to update preview
        self.filament_fields['color_hex'].bind("<KeyRelease>", self.update_swatch_preview)

        ctk.CTkLabel(right_panel, text="Addon Price ($):").grid(row=8, column=0, sticky="w", padx=20, pady=(5, 0))
        self.filament_fields['addon_price'] = ctk.CTkEntry(right_panel, placeholder_text="0.00")
        self.filament_fields['addon_price'].grid(row=9, column=0, sticky="ew", padx=20, pady=(0, 10))

        # Action Execution Button
        ctk.CTkButton(
            right_panel,
            text="Save Filament Status",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#00AE42",
            hover_color="#008F36",
            command=self.save_filament,
        ).grid(row=10, column=0, pady=30, padx=20, sticky="ew")

        self.refresh_filament_list()

    def update_swatch_preview(self, event=None):
        hex_code = self.filament_fields['color_hex'].get().strip()
        if len(hex_code) == 7 and hex_code.startswith("#"):
            try:
                self.color_preview.configure(fg_color=hex_code)
            except:
                self.color_preview.configure(fg_color="transparent")
        else:
            self.color_preview.configure(fg_color="transparent")

    def refresh_filament_list(self):
        self.filament_listbox.delete(0, tk.END)
        for fil in self.filament_data:
            self.filament_listbox.insert(
                tk.END, f"{fil.get('name', 'Unknown')} ({fil.get('material', 'PLA')})"
            )

    def on_filament_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_filament_index = selection[0]
            fil = self.filament_data[self.current_filament_index]
            
            for entry in self.filament_fields.values():
                entry.delete(0, tk.END)
                
            self.filament_fields['id'].insert(0, str(fil.get('id', '')))
            self.filament_fields['name'].insert(0, str(fil.get('name', '')))
            self.filament_fields['color_hex'].insert(0, str(fil.get('color_hex', '')))
            self.filament_fields['addon_price'].insert(0, str(fil.get('addon_price', '0.00')))
            self.material_dropdown.set(fil.get('material', 'PLA'))
            
            # Update the visual swatch
            self.update_swatch_preview()

    def clear_filament_form(self):
        for entry in self.filament_fields.values():
            entry.delete(0, tk.END)
        self.material_dropdown.set('PLA')
        self.color_preview.configure(fg_color="transparent")
        self.filament_listbox.selection_clear(0, tk.END)
        self.current_filament_index = None

    def save_filament(self):
        new_filament = {
            'id': self.filament_fields['id'].get().strip(),
            'name': self.filament_fields['name'].get().strip(),
            'material': self.material_dropdown.get(),
            'color_hex': self.filament_fields['color_hex'].get().strip()
        }

        try:
            new_filament['addon_price'] = float(self.filament_fields['addon_price'].get())
        except ValueError:
            new_filament['addon_price'] = 0.00

        if not new_filament['id'] or not new_filament['name']:
            messagebox.showwarning("Validation Required", "Filament ID and Display Name are mandated fields.")
            return

        if self.current_filament_index is not None:
            self.filament_data[self.current_filament_index] = new_filament
        else:
            if any(f.get('id') == new_filament['id'] for f in self.filament_data):
                messagebox.showwarning("Registry Conflict", "This internal ID has already been assigned.")
                return
            self.filament_data.append(new_filament)

        self.save_json(FILAMENT_FILE, self.filament_data)
        self.refresh_filament_list()
        self.clear_filament_form()
        messagebox.showinfo("Success", "Filament inventory synced!")

    def delete_filament(self):
        if self.current_filament_index is not None:
            del self.filament_data[self.current_filament_index]
            self.save_json(FILAMENT_FILE, self.filament_data)
            self.refresh_filament_list()
            self.clear_filament_form()


if __name__ == "__main__":
    root = ctk.CTk()
    app = PrintPathCMS(root)
    root.mainloop()