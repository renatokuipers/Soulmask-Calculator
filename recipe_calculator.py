import sys
import json
import os
from PySide2.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QComboBox, QPushButton, QTextEdit, QWidget, QTreeWidget, QTreeWidgetItem,
                               QMenu, QAction, QMessageBox, QFrame, QScrollArea)

def load_recipes(file_path="recipes.json"):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_recipes(recipes, file_path="recipes.json"):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(recipes, file, indent=4)

class CraftingCalculator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Soulmask Crafting Calculator")
        self.recipes = load_recipes()
        self.dark_mode = False

        self.create_menu()
        self.recipe_var = ""

        self.create_widgets()
        self.update_recipe_dropdown()

    def create_menu(self):
        self.menu = self.menuBar()
        self.view_menu = self.menu.addMenu("View")
        self.toggle_dark_mode_action = QAction("Toggle Dark Mode", self)
        self.toggle_dark_mode_action.triggered.connect(self.toggle_dark_mode)
        self.view_menu.addAction(self.toggle_dark_mode_action)

    def create_widgets(self):
        self.main_frame = QFrame()
        self.setCentralWidget(self.main_frame)
        self.main_layout = QHBoxLayout(self.main_frame)

        self.left_frame = QFrame()
        self.left_layout = QVBoxLayout(self.left_frame)
        self.main_layout.addWidget(self.left_frame)

        # Search Bar
        self.search_label = QLabel("Search:")
        self.left_layout.addWidget(self.search_label)

        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self.update_dropdown_with_search)
        self.left_layout.addWidget(self.search_entry)

        # Classification Filter
        self.class_filter_label = QLabel("Filter by Classification:")
        self.left_layout.addWidget(self.class_filter_label)

        self.class_filter_dropdown = QComboBox()
        self.class_filter_dropdown.addItems([
            'All', 'Plants', 'Minerals', 'Animals', 'Weapons', 'Armor', 'Tools', 'Containers',
            'Buildings', 'Food', 'Dishes', 'Medicines', 'Semi-finished Product', 'Other'
        ])
        self.class_filter_dropdown.currentTextChanged.connect(self.update_dropdown_with_search)
        self.left_layout.addWidget(self.class_filter_dropdown)

        # Recipe Selection
        self.recipe_label = QLabel("Select Recipe:")
        self.left_layout.addWidget(self.recipe_label)

        self.recipe_dropdown = QComboBox()
        self.recipe_dropdown.currentTextChanged.connect(self.set_recipe_var)
        self.left_layout.addWidget(self.recipe_dropdown)

        # Quantity
        self.quantity_label = QLabel("Quantity:")
        self.left_layout.addWidget(self.quantity_label)

        self.quantity_entry = QLineEdit()
        self.quantity_entry.setText("1")
        self.left_layout.addWidget(self.quantity_entry)

        # Calculate Button
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_resources)
        self.left_layout.addWidget(self.calculate_button)

        # Add Recipe Button
        self.add_recipe_button = QPushButton("Add Recipe")
        self.add_recipe_button.clicked.connect(self.open_add_recipe_window)
        self.left_layout.addWidget(self.add_recipe_button)

        # Materials Summary
        self.summary_label = QLabel("Materials Summary:")
        self.left_layout.addWidget(self.summary_label)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.left_layout.addWidget(self.summary_text)

        # Right Frame
        self.right_frame = QFrame()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.main_layout.addWidget(self.right_frame)

        # Recipe Information
        self.summary_info_label = QLabel("Recipe Information:")
        self.right_layout.addWidget(self.summary_info_label)

        self.total_resources_text = QTextEdit()
        self.total_resources_text.setReadOnly(True)
        self.right_layout.addWidget(self.total_resources_text)

        # Expand/Collapse Buttons
        self.button_frame = QHBoxLayout()
        self.expand_all_button = QPushButton("Expand All")
        self.expand_all_button.clicked.connect(self.expand_all)
        self.button_frame.addWidget(self.expand_all_button)

        self.collapse_all_button = QPushButton("Collapse All")
        self.collapse_all_button.clicked.connect(self.collapse_all)
        self.button_frame.addWidget(self.collapse_all_button)

        self.right_layout.addLayout(self.button_frame)

        # Tree View
        self.tree_frame = QScrollArea()
        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderHidden(True)
        self.tree_frame.setWidget(self.result_tree)
        self.tree_frame.setWidgetResizable(True)
        self.right_layout.addWidget(self.tree_frame)

        # Apply dark mode settings if enabled
        if self.dark_mode:
            self.set_dark_mode()

    def set_recipe_var(self, text):
        self.recipe_var = text

    def toggle_dark_mode(self):
        if self.dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()
        self.dark_mode = not self.dark_mode

    def set_dark_mode(self):
        dark_bg = "#2e2e2e"
        dark_fg = "white"

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {dark_bg}; color: {dark_fg}; }}
            QLabel {{ color: {dark_fg}; }}
            QLineEdit {{ background-color: {dark_bg}; color: {dark_fg}; }}
            QComboBox {{ background-color: {dark_bg}; color: {dark_fg}; }}
            QPushButton {{ background-color: {dark_bg}; color: {dark_fg}; }}
            QTextEdit {{ background-color: {dark_bg}; color: {dark_fg}; }}
            QTreeWidget {{ background-color: {dark_bg}; color: {dark_fg}; }}
        """)

    def set_light_mode(self):
        self.setStyleSheet("")

    def expand_all(self):
        self.result_tree.expandAll()

    def collapse_all(self):
        self.result_tree.collapseAll()

    def update_recipe_dropdown(self):
        search_text = self.search_entry.text().lower()
        class_filter = self.class_filter_dropdown.currentText()

        filtered_recipes = []
        for recipe_name, recipe_details in self.recipes.items():
            if class_filter != 'All' and recipe_details.get('Classification') != class_filter:
                continue
            if search_text in recipe_name.lower():
                filtered_recipes.append(recipe_name)

        self.recipe_dropdown.clear()
        self.recipe_dropdown.addItems(filtered_recipes)

    def update_dropdown_with_search(self):
        self.update_recipe_dropdown()

    def calculate_resources(self):
        item_name = self.recipe_var.strip()
        try:
            quantity = int(self.quantity_entry.text().strip())
        except ValueError:
            QMessageBox.critical(self, "Error", "Quantity must be an integer!")
            return

        self.result_tree.clear()
        self.total_resources_text.clear()

        if item_name in self.recipes:
            recipe = self.recipes[item_name]
            description = recipe.get('Description', 'N/A')
            crafted_in = recipe.get('Crafted in', 'Manual Crafting')

            # Show description and crafting station
            self.total_resources_text.append(f"Description: {description}\n")
            self.total_resources_text.append(f"\nCrafting Station: {crafted_in}\n")

            # Display materials required in the tree view
            total_resources = {}
            crafting_stations = {}
            visited_recipes = set()
            self.get_total_resources(item_name, quantity, total_resources, parent=None, visited_recipes=visited_recipes, crafting_stations=crafting_stations)

            # Organize summary by crafting stations
            summary = ""
            for station, materials in crafting_stations.items():
                summary += f"\nCrafting Station: {station}\n"
                for material, amount in materials.items():
                    summary += f"  {material}: {amount}\n"

            # Display materials summary in the summary frame
            self.summary_text.setText(summary)

        else:
            self.result_tree.addTopLevelItem(QTreeWidgetItem(["Recipe not found!"]))
            self.total_resources_text.append("Recipe not found!")

    def get_total_resources(self, item_name, quantity, total_resources, parent=None, visited_recipes=None, crafting_stations=None, is_required=True):
        if visited_recipes is None:
            visited_recipes = set()
        if crafting_stations is None:
            crafting_stations = {}

        if item_name not in self.recipes or item_name in visited_recipes:
            return

        visited_recipes.add(item_name)

        recipe = self.recipes[item_name]
        materials_required = recipe.get('Materials Required', {}) or {}
        extra_materials = recipe.get('Extra optional materials', {}) or {}
        crafted_in = recipe.get('Crafted in', 'Manual Crafting')

        if crafted_in not in crafting_stations:
            crafting_stations[crafted_in] = {}

        if materials_required:
            req_parent = QTreeWidgetItem(parent, ["Required Materials"])
            self.result_tree.addTopLevelItem(req_parent)
            for resource, amount in materials_required.items():
                item_id = QTreeWidgetItem(req_parent, [f"{resource} x {amount * quantity}"])
                req_parent.addChild(item_id)
                if resource in self.recipes:
                    if resource not in total_resources:
                        total_resources[resource] = 0
                    total_resources[resource] += amount * quantity
                    if resource not in crafting_stations[crafted_in]:
                        crafting_stations[crafted_in][resource] = 0
                    crafting_stations[crafted_in][resource] += amount * quantity
                    self.get_total_resources(resource, amount * quantity, total_resources, parent=item_id, visited_recipes=visited_recipes, crafting_stations=crafting_stations)
                else:
                    if resource in total_resources:
                        total_resources[resource] += amount * quantity
                    else:
                        total_resources[resource] = amount * quantity
                    if resource in crafting_stations[crafted_in]:
                        crafting_stations[crafted_in][resource] += amount * quantity
                    else:
                        crafting_stations[crafted_in][resource] = amount * quantity

        if extra_materials:
            extra_parent = QTreeWidgetItem(parent, ["Extra Optional Materials"])
            self.result_tree.addTopLevelItem(extra_parent)
            for extra, extra_amount in extra_materials.items():
                extra_id = QTreeWidgetItem(extra_parent, [f"{extra} x {extra_amount * quantity}"])
                extra_parent.addChild(extra_id)
                if extra in self.recipes:
                    if extra not in total_resources:
                        total_resources[extra] = 0
                    total_resources[extra] += extra_amount * quantity
                    if extra not in crafting_stations[crafted_in]:
                        crafting_stations[crafted_in][extra] = 0
                    crafting_stations[crafted_in][extra] += extra_amount * quantity
                    self.get_total_resources(extra, extra_amount * quantity, total_resources, parent=extra_id, visited_recipes=visited_recipes, crafting_stations=crafting_stations, is_required=False)
                else:
                    if extra in total_resources:
                        total_resources[extra] += extra_amount * quantity
                    else:
                        total_resources[extra] = extra_amount * quantity
                    if extra in crafting_stations[crafted_in]:
                        crafting_stations[crafted_in][extra] += extra_amount * quantity
                    else:
                        crafting_stations[crafted_in][extra] = extra_amount * quantity

    def open_add_recipe_window(self):
        add_recipe_window = AddRecipeWindow(self)
        add_recipe_window.show()

class AddRecipeWindow(QWidget):
    def __init__(self, calculator_app):
        super().__init__()

        self.setWindowTitle("Add Recipe")
        self.app = calculator_app

        self.resource_entries = []
        self.extra_resource_entries = []

        self.create_widgets()

    def create_widgets(self):
        self.setGeometry(100, 100, 600, 620)

        self.main_layout = QVBoxLayout(self)

        # Recipe Name
        self.recipe_name_label = QLabel("Recipe Name:")
        self.main_layout.addWidget(self.recipe_name_label)

        self.recipe_name_entry = QLineEdit()
        self.main_layout.addWidget(self.recipe_name_entry)

        # Description
        self.description_label = QLabel("Description:")
        self.main_layout.addWidget(self.description_label)

        self.description_entry = QLineEdit()
        self.main_layout.addWidget(self.description_entry)

        # Crafted in
        self.crafted_in_label = QLabel("Crafted in:")
        self.main_layout.addWidget(self.crafted_in_label)

        self.crafted_in_entry = QLineEdit()
        self.main_layout.addWidget(self.crafted_in_entry)

        # Classification
        self.classification_label = QLabel("Classification:")
        self.main_layout.addWidget(self.classification_label)

        self.classification_dropdown = QComboBox()
        self.classification_dropdown.addItems([
            'Plants', 'Minerals', 'Animals', 'Weapons', 'Armor', 'Tools', 'Containers',
            'Buildings', 'Food', 'Dishes', 'Medicines', 'Semi-finished Product', 'Other'
        ])
        self.main_layout.addWidget(self.classification_dropdown)

        # Resources
        self.resources_label = QLabel("Resources:")
        self.main_layout.addWidget(self.resources_label)

        self.resources_layout = QVBoxLayout()
        self.main_layout.addLayout(self.resources_layout)

        self.add_resource_button = QPushButton("Add Resource")
        self.add_resource_button.clicked.connect(self.add_resource_entry)
        self.main_layout.addWidget(self.add_resource_button)

        # Extra Optional Resources
        self.extra_resources_label = QLabel("Extra Optional Resources:")
        self.main_layout.addWidget(self.extra_resources_label)

        self.extra_resources_layout = QVBoxLayout()
        self.main_layout.addLayout(self.extra_resources_layout)

        self.add_extra_resource_button = QPushButton("Add Extra Optional Resource")
        self.add_extra_resource_button.clicked.connect(self.add_extra_resource_entry)
        self.main_layout.addWidget(self.add_extra_resource_button)

        # Save Button
        self.save_button = QPushButton("Save Recipe")
        self.save_button.clicked.connect(self.save_recipe)
        self.main_layout.addWidget(self.save_button)

    def add_resource_entry(self):
        resource_name_entry = QLineEdit()
        amount_entry = QLineEdit()
        resource_layout = QHBoxLayout()
        resource_layout.addWidget(resource_name_entry)
        resource_layout.addWidget(amount_entry)
        self.resources_layout.addLayout(resource_layout)
        self.resource_entries.append((resource_name_entry, amount_entry))

    def add_extra_resource_entry(self):
        extra_name_entry = QLineEdit()
        extra_amount_entry = QLineEdit()
        extra_layout = QHBoxLayout()
        extra_layout.addWidget(extra_name_entry)
        extra_layout.addWidget(extra_amount_entry)
        self.extra_resources_layout.addLayout(extra_layout)
        self.extra_resource_entries.append((extra_name_entry, extra_amount_entry))

    def save_recipe(self):
        recipe_name = self.recipe_name_entry.text().strip()
        description = self.description_entry.text().strip()
        crafted_in = self.crafted_in_entry.text().strip()
        classification = self.classification_dropdown.currentText().strip()

        if not recipe_name:
            QMessageBox.critical(self, "Error", "Recipe name cannot be empty!")
            return

        resources = {}
        for resource_name_entry, amount_entry in self.resource_entries:
            resource_name = resource_name_entry.text().strip()
            amount = amount_entry.text().strip()
            if resource_name and amount:
                try:
                    amount = int(amount)
                except ValueError:
                    QMessageBox.critical(self, "Error", "Amount must be an integer!")
                    return
                resources[resource_name] = amount

        extra_resources = {}
        for extra_name_entry, extra_amount_entry in self.extra_resource_entries:
            extra_name = extra_name_entry.text().strip()
            extra_amount = extra_amount_entry.text().strip()
            if extra_name and extra_amount:
                try:
                    extra_amount = int(extra_amount)
                except ValueError:
                    QMessageBox.critical(self, "Error", "Amount for extra optional resources must be an integer!")
                    return
                extra_resources[extra_name] = extra_amount

        if not resources and not extra_resources:
            QMessageBox.critical(self, "Error", "Resources and Extra optional materials cannot both be empty!")
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
        QMessageBox.information(self, "Success", "Recipe added successfully!")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CraftingCalculator()
    window.show()
    sys.exit(app.exec_())
