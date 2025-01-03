import os
import json
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QCheckBox
)
from views.processing import FileProcessing


from PyQt6.QtWidgets import QScrollArea


class ColumnMapping(QWidget):
    def __init__(self, DataFolder, csv_columns, node_name):
        super().__init__()
        self.csv_columns = csv_columns
        self.node_name = node_name
        self.new_variable_names = {}
        self.property_key_checkboxes = {}
        self.column_mappings = []
        self.node_name = node_name
        self.DataFolder = DataFolder

        self.setWindowTitle("Column Mapping")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(400, 200, 1200, 800)

        # Create a scroll area for the main content
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Create a main widget to hold the content inside the scroll area
        scroll_widget = QWidget()
        self.main_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)

        # Set spacing for the layout
        self.main_layout.setSpacing(20)

        # Display the Node Name as a title
        node_name_label = QLabel("Node Name: " + self.node_name)
        node_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        node_name_label.setStyleSheet("font-size: 35px; font-weight: bold; margin-bottom: 20px;")
        self.main_layout.addWidget(node_name_label)

        # Display the columns for mapping
        self.display_column_mapping()

        # Add "Submit" button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedHeight(50)
        self.submit_button.setStyleSheet("background-color: #0a6df0; color: white;")
        self.submit_button.clicked.connect(self.submit_mapping)
        self.main_layout.addWidget(self.submit_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Add the scroll area to the main window layout
        window_layout = QVBoxLayout(self)
        window_layout.addWidget(scroll_area)
        self.setLayout(window_layout)

        # Prepare for the next page
        self.processing_page = None

    def display_column_mapping(self):
        """Display input fields for column mapping."""
        for original_name in self.csv_columns:
            # Horizontal layout for each column
            h_layout = QHBoxLayout()
            h_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            # Original Column Name Label
            original_name_label = QLabel(original_name + ":")
            original_name_label.setStyleSheet("font-size: 16px; font-weight: bold;")

            # Input Field for renaming
            new_name_input = QLineEdit()
            new_name_input.setPlaceholderText("Enter new variable name")
            new_name_input.setMinimumHeight(30)
            new_name_input.setFixedWidth(300)

            # Checkbox to mark as Property Key
            property_key_checkbox = QCheckBox("Property Key")
            property_key_checkbox.setFixedHeight(30)

            # Add widgets to the horizontal layout
            h_layout.addWidget(original_name_label)
            h_layout.addWidget(new_name_input)
            h_layout.addWidget(property_key_checkbox)
            h_layout.addStretch()

            # Add the horizontal layout to the main layout
            self.main_layout.addLayout(h_layout)

            # Store input fields and checkboxes
            self.new_variable_names[original_name] = new_name_input
            self.property_key_checkboxes[original_name] = property_key_checkbox

    def collect_mapping(self):
        """Collect the column mapping data from user inputs."""
        mapping = {
            "Node Name": self.node_name,
            "Property Key": []  # Default to an empty list
        }
        for original_name, new_name_input in self.new_variable_names.items():
            new_variable_name = new_name_input.text().strip()
            if self.property_key_checkboxes[original_name].isChecked():
                mapping["Property Key"].append(original_name)

            # Add original and new names to the mapping
            mapping[original_name] = new_variable_name if new_variable_name else original_name
        print(mapping)
        return mapping

    def submit_mapping(self):
        """Handle the submission of column mapping."""
        self.column_mappings = self.collect_mapping()

        # Store node configuration to cache
        cache_folder = os.path.abspath("../cache")
        node_folder = os.path.join(cache_folder, self.node_name)
        file_path = os.path.join(node_folder, f"{self.node_name}Config.json")
        os.makedirs(node_folder, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.column_mappings, f, ensure_ascii=False, indent=4)
        self.processing_page = FileProcessing(self.DataFolder, self.node_name)
        self.processing_page.show()
        self.close()


