import sys
import os
import json
import pandas as pd
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox
)
from util.csvWalk import DataFolder
from views.columnDefine import ColumnDefine


class SelectNodeFolder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.import_btn = None
        self.browse_btn = None
        self.file_path_input = None
        self.label = None
        self.node_name_input = None
        self.node_name_label = None
        self.columnDefine = None
        self.setWindowTitle("Select Node Folder")
        self.setWindowIcon(QIcon("icon.png"))
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 650, 200)

        # Node Name Label
        self.node_name_label = QLabel("Node Name:", self)
        self.node_name_label.move(20, 20)

        # Node Name Input Field
        self.node_name_input = QLineEdit(self)
        self.node_name_input.setGeometry(120, 20, 380, 30)
        self.node_name_input.setPlaceholderText("Enter Node Name")

        # Folder Path Label
        self.label = QLabel("Folder Path:", self)
        self.label.move(20, 60)

        # Folder Path Input Field
        self.file_path_input = QLineEdit(self)
        self.file_path_input.setGeometry(120, 60, 380, 30)
        self.file_path_input.setText("../data")  # Set default work folder as

        # Browse Button
        self.browse_btn = QPushButton("Browse", self)
        self.browse_btn.setGeometry(530, 60, 65, 30)
        self.browse_btn.clicked.connect(self.select_folder)

        # "Get Start" Button
        self.import_btn = QPushButton("Get Start", self)
        self.import_btn.setGeometry(240, 120, 120, 40)
        self.import_btn.clicked.connect(self.trans_to_columnDefine_window)

    def select_folder(self):
        """Open a file dialog to select a folder"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder"
        )

        if folder_path:
            self.file_path_input.setText(folder_path)

    def trans_to_columnDefine_window(self):
        """Process the selected folder"""
        # Get Node Name and Folder Path
        node_name = self.node_name_input.text().strip()
        folder_path = self.file_path_input.text().strip()

        if not node_name:
            QMessageBox.critical(self, "Error", "Please enter a Node Name!")
            return

        if not folder_path:
            QMessageBox.critical(self, "Error", "Please select a folder!")
            return

        # Create a folder inside "cache" with the name of the node
        cache_folder = os.path.abspath("../cache")
        node_folder = os.path.join(cache_folder, node_name)

        # Check if the node folder already exists
        if os.path.exists(node_folder):
            QMessageBox.critical(self, "Error", f"A folder with the name '{node_name}' already exists!")
            return

        # Create the folder if it doesn't exist
        os.makedirs(node_folder)

        file_path = os.path.join(node_folder, "path.json")
        file_path_dict = {"folder_path": folder_path}

        # Write path.json
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(file_path_dict, f, ensure_ascii=False, indent=4)

        try:
            # Find all CSV files in the folder
            dataFolder = DataFolder(folder_path)
            csv_files = dataFolder.find_all_csv_files()

            if not csv_files:
                QMessageBox.critical(self, "Error", "No CSV files found in the selected folder!")
                return

            QMessageBox.information(self, "Success",
                                    f"Folder processed successfully! Found {len(csv_files)} CSV files.")
            print(f"Path saved to: {file_path}")
            print(f"Number of CSV files: {len(csv_files)}")

            # Show the columnDefine page and close the selectNodeFolder page
            self.columnDefine = ColumnDefine(dataFolder, node_name)
            self.columnDefine.show()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process folder: {str(e)}")

