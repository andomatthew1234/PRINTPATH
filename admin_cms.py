import tkinter as tk
from tkinter import messagebox
import json
import os

DATA_FILE = 'data.json'

class PrintPathCMS:
    def __init__(self, root):
        self.root = root
        self.root.title("PrintPath CMS")
        self.root.geometry("600x450")
        
        self.data = []
        self.load_data()

        # UI Layout
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Listbox for items
        self.listbox = tk.Listbox(left_frame, width=30)
        self.listbox.pack(fill=tk.Y, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="New", command=self.clear_form).pack(side=tk.LEFT, expand=True)
        tk.Button(btn_frame, text="Delete", command=self.delete_item).pack(side=tk.RIGHT, expand=True)

        # Form Fields
        self.fields = {}
        labels = ['id', 'name', 'price', 'description', 'image', 'stripe_link']
        for i, label in enumerate(labels):
            tk.Label(right_frame, text=label.capitalize()).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = tk.Entry(right_frame, width=40)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=2)
            self.fields[label] = entry

        tk.Button(right_frame, text="Save Item to JSON", command=self.save_item, bg="#00AE42", fg="white").grid(row=len(labels), column=0, columnspan=2, pady=15, sticky=tk.EW)
        
        self.refresh_list()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = []

    def save_to_file(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for item in self.data:
            self.listbox.insert(tk.END, item['name'])

    def on_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            item = self.data[index]
            self.clear_form()
            for key in self.fields:
                self.fields[key].insert(0, str(item.get(key, '')))

    def clear_form(self):
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.listbox.selection_clear(0, tk.END)

    def save_item(self):
        new_item = {}
        for key, entry in self.fields.items():
            val = entry.get()
            if key == 'price':
                try: val = float(val)
                except ValueError: val = 0.0
            new_item[key] = val

        if not new_item['id'] or not new_item['name']:
            messagebox.showwarning("Error", "ID and Name are required.")
            return

        # Check if updating or adding new
        selection = self.listbox.curselection()
        if selection:
            self.data[selection[0]] = new_item
        else:
            # Check for duplicate ID
            if any(i['id'] == new_item['id'] for i in self.data):
                messagebox.showwarning("Error", "Item with this ID already exists.")
                return
            self.data.append(new_item)

        self.save_to_file()
        self.refresh_list()
        self.clear_form()
        messagebox.showinfo("Success", "Saved successfully to data.json")

    def delete_item(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            del self.data[index]
            self.save_to_file()
            self.refresh_list()
            self.clear_form()

if __name__ == "__main__":
    root = tk.Tk()
    app = PrintPathCMS(root)
    root.mainloop()