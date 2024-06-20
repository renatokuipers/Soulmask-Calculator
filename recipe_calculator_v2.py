import tkinter as tk
from tkinter import messagebox, ttk, Canvas, Scrollbar
import json
import os

def load_recipes(file_path="recipes.json"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_recipes(recipes, file_path="recipes.json"):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(recipes, file, indent=4)

class CraftingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Soulmask Crafting Calculator")

        self.recipes = load_recipes()
        self.dark_mode = False

        self.create_menu()
        self.recipe_var = tk.StringVar()
        self.create_widgets()

    def create_menu(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)

    def create_widgets(self):
        self.root.minsize(720, 640)  # Set minimum window size

        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        self.style.configure("Treeview", font=("Arial", 10), rowheight=25)
        self.style.map("Treeview", background=[('selected', 'lightblue')], foreground=[('selected', 'black')])

        self.main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.main_frame.add(self.left_frame, width=250)

        # Search Bar
        tk.Label(self.left_frame, text="Search:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.left_frame, textvariable=self.search_var, font=("Arial", 10))
        self.search_entry.grid(row=1, column=0, padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>", self.update_dropdown_with_search)

        # Classification Filter
        tk.Label(self.left_frame, text="Filter by Classification:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
        self.class_filter_var = tk.StringVar()
        self.class_filter_dropdown = ttk.Combobox(self.left_frame, textvariable=self.class_filter_var, font=("Arial", 10))
        self.class_filter_dropdown['values'] = [
            'All', 'Plants', 'Minerals', 'Animals', 'Weapons', 'Armor', 'Tools', 'Containers', 
            'Buildings', 'Food', 'Dishes', 'Medicines', 'Semi-finished Product', 'Other'
        ]
        self.class_filter_dropdown.grid(row=3, column=0, padx=10, pady=5)
        self.class_filter_dropdown.bind("<<ComboboxSelected>>", self.update_dropdown_with_search)
        self.class_filter_dropdown.set('All')

        tk.Label(self.left_frame, text="Select Recipe:", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=5)
        self.recipe_dropdown = ttk.Combobox(self.left_frame, textvariable=self.recipe_var, font=("Arial", 10))
        self.recipe_dropdown.grid(row=5, column=0, padx=10, pady=5)

        tk.Label(self.left_frame, text="Quantity:", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=5)
        self.quantity_entry = tk.Entry(self.left_frame, font=("Arial", 10))
        self.quantity_entry.insert(0, "1")  # Set default value to 1
        self.quantity_entry.grid(row=7, column=0, padx=10, pady=5)

        self.calculate_button = tk.Button(self.left_frame, text="Calculate", command=self.calculate_resources, font=("Arial", 12))
        self.calculate_button.grid(row=8, column=0, pady=10)

        self.add_recipe_button = tk.Button(self.left_frame, text="Add Recipe", command=self.open_add_recipe_window, font=("Arial", 12))
        self.add_recipe_button.grid(row=9, column=0, pady=10)

        self.right_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.main_frame.add(self.right_frame)

        self.summary_frame = tk.Frame(self.right_frame)
        self.summary_frame.pack(fill=tk.X, pady=10)

        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(fill=tk.X, pady=10)

        self.expand_all_button = tk.Button(self.button_frame, text="Expand All", command=self.expand_all, font=("Arial", 10))
        self.expand_all_button.pack(side=tk.LEFT, padx=5)

        self.collapse_all_button = tk.Button(self.button_frame, text="Collapse All", command=self.collapse_all, font=("Arial", 10))
        self.collapse_all_button.pack(side=tk.LEFT, padx=5)

        self.tree_frame = tk.Frame(self.right_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scrollbar.set)
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        self.tree_scrollbar.config(command=self.result_tree.yview)

        # self.summary_label = tk.Label(self.summary_frame, text="Summary of Total Resources Required:", font=("Arial", 12, "bold"))
        # self.summary_label.pack(side=tk.LEFT)
        
        self.summary_label = tk.Label(self.summary_frame, text="Recipe Information:", font=("Arial", 12, "bold"))
        self.summary_label.pack(side=tk.LEFT)

        self.total_resources_text = tk.Text(self.summary_frame, height=4, font=("Arial", 10), state=tk.DISABLED)
        self.total_resources_text.pack(fill=tk.X, expand=True, padx=10, pady=5)

        self.create_tooltip(self.recipe_dropdown, "Select the recipe you want to craft.")
        self.create_tooltip(self.quantity_entry, "Enter the quantity you want to craft.")

        self.update_recipe_dropdown()

        # Apply dark mode settings if enabled
        if self.dark_mode:
            self.set_dark_mode()

    def toggle_dark_mode(self):
        if self.dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()
        self.dark_mode = not self.dark_mode

    def set_dark_mode(self):
        dark_bg = "#2e2e2e"
        dark_fg = "white"
        lighter_bg = "#3e3e3e"

        self.style.configure("Treeview", background=dark_bg, foreground=dark_fg, fieldbackground=dark_bg)
        self.style.configure("Treeview.Heading", background=lighter_bg, foreground=dark_fg)
        
        self.root.configure(bg="#1e1e1e")
        self.main_frame.configure(bg="#1e1e1e")
        self.left_frame.configure(bg="#1e1e1e")
        self.right_frame.configure(bg="#1e1e1e")
        self.summary_frame.configure(bg="#1e1e1e")
        self.button_frame.configure(bg="#1e1e1e")
        self.tree_frame.configure(bg="#1e1e1e")

        self.summary_label.configure(bg="#1e1e1e", fg=dark_fg)
        self.total_resources_text.configure(bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)

        self.search_entry.configure(bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)
        self.class_filter_dropdown.configure(background=dark_bg, foreground=dark_fg)
        self.recipe_dropdown.configure(background=dark_bg, foreground=dark_fg)
        self.quantity_entry.configure(bg=dark_bg, fg=dark_fg, insertbackground=dark_fg)

        for widget in [self.calculate_button, self.add_recipe_button, self.expand_all_button, self.collapse_all_button]:
            widget.configure(bg=lighter_bg, fg=dark_fg, activebackground="#4e4e4e")

        for widget in self.left_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg="#1e1e1e", fg=dark_fg)

    def set_light_mode(self):
        light_bg = "SystemButtonFace"
        light_fg = "black"
        white_bg = "white"

        self.style.configure("Treeview", background=white_bg, foreground=light_fg, fieldbackground=white_bg)
        self.style.configure("Treeview.Heading", background=light_bg, foreground=light_fg)
        
        self.root.configure(bg=light_bg)
        self.main_frame.configure(bg=light_bg)
        self.left_frame.configure(bg=light_bg)
        self.right_frame.configure(bg=light_bg)
        self.summary_frame.configure(bg=light_bg)
        self.button_frame.configure(bg=light_bg)
        self.tree_frame.configure(bg=light_bg)

        self.summary_label.configure(bg=light_bg, fg=light_fg)
        self.total_resources_text.configure(bg=white_bg, fg=light_fg, insertbackground=light_fg)

        self.search_entry.configure(bg=white_bg, fg=light_fg, insertbackground=light_fg)
        self.class_filter_dropdown.configure(background=white_bg, foreground=light_fg)
        self.recipe_dropdown.configure(background=white_bg, foreground=light_fg)
        self.quantity_entry.configure(bg=white_bg, fg=light_fg, insertbackground=light_fg)

        for widget in [self.calculate_button, self.add_recipe_button, self.expand_all_button, self.collapse_all_button]:
            widget.configure(bg=light_bg, fg=light_fg, activebackground=light_bg)

        for widget in self.left_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=light_bg, fg=light_fg)

    def expand_all(self):
        for item in self.result_tree.get_children():
            self.result_tree.item(item, open=True)
            self._expand_all_children(item)

    def _expand_all_children(self, item):
        children = self.result_tree.get_children(item)
        for child in children:
            self.result_tree.item(child, open=True)
            self._expand_all_children(child)

    def collapse_all(self):
        for item in self.result_tree.get_children():
            self.result_tree.item(item, open=False)
            self._collapse_all_children(item)

    def _collapse_all_children(self, item):
        children = self.result_tree.get_children(item)
        for child in children:
            self.result_tree.item(child, open=False)
            self._collapse_all_children(child)

    def update_recipe_dropdown(self):
        search_text = self.search_var.get().lower()
        class_filter = self.class_filter_var.get()

        filtered_recipes = []
        for recipe_name, recipe_details in self.recipes.items():
            if class_filter != 'All' and recipe_details.get('Classification') != class_filter:
                continue
            if search_text in recipe_name.lower():
                filtered_recipes.append(recipe_name)

        self.recipe_dropdown['values'] = filtered_recipes

    def update_dropdown_with_search(self, event=None):
        self.update_recipe_dropdown()

    def create_tooltip(self, widget, text):
        tooltip = ttk.Label(self.root, text=text, background="yellow", relief="solid", borderwidth=1, wraplength=200)
        tooltip.place_forget()

        def on_enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            tooltip.place(x=x, y=y)

        def on_leave(event):
            tooltip.place_forget()

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def calculate_resources(self):
        item_name = self.recipe_var.get().strip()
        try:
            quantity = int(self.quantity_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer!")
            return

        for i in self.result_tree.get_children():
            self.result_tree.delete(i)

        self.total_resources_text.config(state=tk.NORMAL)
        self.total_resources_text.delete(1.0, tk.END)

        if item_name in self.recipes:
            recipe = self.recipes[item_name]
            description = recipe.get('Description', 'N/A')
            crafted_in = recipe.get('Crafted in', 'Manual Crafting')

            # Show description and crafting station
            self.total_resources_text.insert(tk.END, f"Description: {description}\n")
            self.total_resources_text.insert(tk.END, f"\nCrafting Station: {crafted_in}\n")
            
            # Display materials required in the tree view
            materials_required = recipe.get('Materials Required', None)
            if materials_required:
                self.get_total_resources(item_name, quantity, {}, parent='')

        else:
            self.result_tree.insert('', 'end', text='Recipe not found!')
            self.total_resources_text.insert(tk.END, "Recipe not found!")

        self.total_resources_text.config(state=tk.DISABLED)

    def get_extra_resources(self, extra_materials, parent=''):
        if extra_materials:
            extra_parent = self.result_tree.insert(parent, 'end', text="Extra Optional Materials", open=True)
            for extra, extra_amount in extra_materials.items():
                self.result_tree.insert(extra_parent, 'end', text=f"{extra} x {extra_amount}")

    def get_total_resources(self, item_name, quantity, total_resources, parent=''):
        if item_name not in self.recipes:
            return
        materials_required = self.recipes[item_name].get('Materials Required', None)
        extra_materials = self.recipes[item_name].get('Extra optional materials', None)
        
        if materials_required:
            for resource, amount in materials_required.items():
                item_id = self.result_tree.insert(parent, 'end', text=f"{resource} x {amount * quantity}", open=True)
                if resource in self.recipes:
                    self.get_total_resources(resource, amount * quantity, total_resources, parent=item_id)
                else:
                    if resource in total_resources:
                        total_resources[resource] += amount * quantity
                    else:
                        total_resources[resource] = amount * quantity
        
        if extra_materials:
            extra_parent = self.result_tree.insert(parent, 'end', text="Extra Optional Materials", open=True)
            for extra, extra_amount in extra_materials.items():
                self.result_tree.insert(extra_parent, 'end', text=f"{extra} x {extra_amount * quantity}")
                if extra in self.recipes:
                    self.get_total_resources(extra, extra_amount * quantity, total_resources, parent=extra_parent)
                else:
                    if extra in total_resources:
                        total_resources[extra] += extra_amount * quantity
                    else:
                        total_resources[extra] = extra_amount * quantity

    def open_add_recipe_window(self):
        add_recipe_window = tk.Toplevel(self.root)
        AddRecipeWindow(add_recipe_window, self)

class AddRecipeWindow:
    def __init__(self, top_level_root, calculator_app):
        self.root = top_level_root
        self.root.title("Add Recipe")
        self.app = calculator_app

        self.resource_entries = []
        self.extra_resource_entries = []

        self.create_widgets()

    def create_widgets(self):
        self.root.geometry("600x620")  # Set default window size
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        tk.Label(self.main_frame, text="Recipe Name:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        self.recipe_name_entry = tk.Entry(self.main_frame, font=("Arial", 10))
        self.recipe_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.main_frame, text="Description:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
        self.description_entry = tk.Entry(self.main_frame, font=("Arial", 10))
        self.description_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.main_frame, text="Crafted in:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
        self.crafted_in_entry = tk.Entry(self.main_frame, font=("Arial", 10))
        self.crafted_in_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.main_frame, text="Classification:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5)
        self.classification_var = tk.StringVar()
        self.classification_dropdown = ttk.Combobox(self.main_frame, textvariable=self.classification_var, font=("Arial", 10))
        self.classification_dropdown['values'] = [
            'Plants', 'Minerals', 'Animals', 'Weapons', 'Armor', 'Tools', 'Containers', 
            'Buildings', 'Food', 'Dishes', 'Medicines', 'Semi-finished Product', 'Other'
        ]
        self.classification_dropdown.grid(row=3, column=1, padx=10, pady=5)

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=4, column=0, columnspan=2, pady=10, sticky=tk.NSEW)
        self.scrollbar.grid(row=4, column=2, sticky="ns")

        self.add_resource_button = tk.Button(self.main_frame, text="Add Resource", command=self.add_resource_entry, font=("Arial", 10))
        self.add_resource_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.add_extra_resource_button = tk.Button(self.main_frame, text="Add Extra Optional Resource", command=self.add_extra_resource_entry, font=("Arial", 10))
        self.add_extra_resource_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.save_button = tk.Button(self.main_frame, text="Save Recipe", command=self.save_recipe, font=("Arial", 12))
        self.save_button.grid(row=7, column=0, columnspan=2, pady=10)

    def add_resource_entry(self):
        row = len(self.resource_entries)

        resource_name_entry = tk.Entry(self.scrollable_frame, font=("Arial", 10))
        resource_name_entry.grid(row=row, column=0, padx=10, pady=5)
        amount_entry = tk.Entry(self.scrollable_frame, font=("Arial", 10))
        amount_entry.grid(row=row, column=1, padx=10, pady=5)

        self.resource_entries.append((resource_name_entry, amount_entry))

        # Dynamically adjust the window size
        self.root.update_idletasks()
        if self.root.winfo_height() < 720:
            self.root.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")

    def add_extra_resource_entry(self):
        row = len(self.extra_resource_entries)

        extra_resource_name_entry = tk.Entry(self.scrollable_frame, font=("Arial", 10))
        extra_resource_name_entry.grid(row=row, column=0, padx=10, pady=5)
        extra_amount_entry = tk.Entry(self.scrollable_frame, font=("Arial", 10))
        extra_amount_entry.grid(row=row, column=1, padx=10, pady=5)

        self.extra_resource_entries.append((extra_resource_name_entry, extra_amount_entry))

        # Dynamically adjust the window size
        self.root.update_idletasks()
        if self.root.winfo_height() < 720:
            self.root.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")

    def save_recipe(self):
        recipe_name = self.recipe_name_entry.get().strip()
        description = self.description_entry.get().strip()
        crafted_in = self.crafted_in_entry.get().strip()
        classification = self.classification_var.get().strip()

        if not recipe_name:
            messagebox.showerror("Error", "Recipe name cannot be empty!")
            return

        resources = {}
        for resource_name_entry, amount_entry in self.resource_entries:
            resource_name = resource_name_entry.get().strip()
            amount = amount_entry.get().strip()
            if resource_name and amount:
                try:
                    amount = int(amount)
                except ValueError:
                    messagebox.showerror("Error", "Amount must be an integer!")
                    return
                resources[resource_name] = amount

        extra_resources = {}
        for extra_name_entry, extra_amount_entry in self.extra_resource_entries:
            extra_name = extra_name_entry.get().strip()
            extra_amount = extra_amount_entry.get().strip()
            if extra_name and extra_amount:
                try:
                    extra_amount = int(extra_amount)
                except ValueError:
                    messagebox.showerror("Error", "Amount for extra optional resources must be an integer!")
                    return
                extra_resources[extra_name] = extra_amount

        if not resources and not extra_resources:
            messagebox.showerror("Error", "Resources and Extra optional materials cannot both be empty!")
            return

        self.app.recipes[recipe_name] = {
            "Description": description,
            "Crafted in": crafted_in,
            "Classification": classification,
            "Materials Required": resources or None,
            "Extra optional materials": extra_resources or None
        }
        save_recipes(self.app.recipes)
        self.app.update_recipe_dropdown()
        messagebox.showinfo("Success", "Recipe added successfully!")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CraftingCalculator(root)
    root.mainloop()
