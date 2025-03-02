import sys
import tomli
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QGridLayout, QMessageBox, QCheckBox
)
from py2neo import Graph

from views.nodeManage import NodeManage


class GraphInitialization(QWidget):
    def __init__(self, config_path="./.streamlit/secrets.toml"):
        super().__init__()
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.graph = None
        self.nodeManage_window = None

        # Initialize UI components
        self._init_ui()
        self._populate_fields()

    def _load_config(self) -> dict:
        """Load configuration from TOML file"""
        if not self.config_path.exists():
            return {"uri": "", "username": "", "password": ""}

        try:
            with open(self.config_path, "rb") as f:
                data = tomli.load(f)
            return {
                "uri": data.get("NEO4J_URI", ""),
                "username": data.get("NEO4J_USERNAME", ""),
                "password": data.get("NEO4J_PASSWORD", "")
            }
        except Exception as e:
            QMessageBox.critical(self, "Config Error",
                                f"Failed to load config file: {str(e)}")
            return {"uri": "", "username": "", "password": ""}

    def _init_ui(self):
        """Initialize UI components and layout"""
        self.setWindowTitle("Neo4j Database Configuration")
        self.setFixedSize(400, 250)

        # Input fields
        self.uri_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Buttons
        self.test_btn = QPushButton("Test Connection")
        self.save_btn = QPushButton("Save Configuration")
        self.test_btn.clicked.connect(lambda: self._test_connection(isManual=True))
        self.save_btn.clicked.connect(self._save_config)

        # Layout management
        layout = QVBoxLayout()
        grid = QGridLayout()

        # Add components to grid
        grid.addWidget(QLabel("URI:"), 0, 0)
        grid.addWidget(self.uri_input, 0, 1)
        grid.addWidget(QLabel("Username:"), 1, 0)
        grid.addWidget(self.user_input, 1, 1)
        grid.addWidget(QLabel("Password:"), 2, 0)
        grid.addWidget(self.pwd_input, 2, 1)

        # Assemble full layout
        layout.addLayout(grid)
        layout.addWidget(self.test_btn)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def _populate_fields(self):
        """Populate input fields with existing configuration"""
        self.uri_input.setText(self.config["uri"])
        self.user_input.setText(self.config["username"])
        self.pwd_input.setText(self.config["password"])

    def _test_connection(self, isManual=True):
        """Test database connection with current parameters"""
        uri = self.uri_input.text()
        user = self.user_input.text()
        pwd = self.pwd_input.text()

        try:
            self.graph = Graph(uri, auth=(user, pwd))
            self.graph.run("RETURN 1")  # Simple validation query
            if isManual:
                QMessageBox.information(self, "Success", "Database connection established!")
            return True
        except Exception as e:
            if isManual:
                QMessageBox.critical(self, "Connection Failed", f"Error: {str(e)}")
            return False

    def _save_config(self):
        """Save current configuration to TOML file"""
        new_config = {
            "NEO4J_URI": self.uri_input.text(),
            "NEO4J_USERNAME": self.user_input.text(),
            "NEO4J_PASSWORD": self.pwd_input.text()
        }

        try:
            if self._test_connection(False):
                with open(self.config_path, "w") as f:
                    # Manual TOML content creation
                    content = "\n".join(
                        [f'{key} = "{value}"' for key, value in new_config.items()]
                    )
                    f.write(content)
                QMessageBox.information(self, "Success", "Configuration saved successfully!")
                self.nodeManage_window = NodeManage()
                self.close()
                self.nodeManage_window.show()
            else:
                QMessageBox.critical(self, "Graph Connection Failed", "You must validate the database connection first!")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration: {str(e)}")

