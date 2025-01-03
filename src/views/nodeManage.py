import json
import os
import sys
import streamlit as st
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
    QWidget, QApplication, QLabel, QVBoxLayout, QGridLayout, QCheckBox, QPushButton, QHBoxLayout, QMessageBox,
    QLineEdit, QScrollArea
)
from py2neo import Graph

from util.nodesFetch import nodesInNeo4j, nodeInfoFetch
from views.selectNodeFolder import SelectNodeFolder


class NodeManage(QWidget):
    def __init__(self):
        super().__init__()
        self.terminate_button = None
        self.add_page = None
        self.start_button = None
        self.input_box = None
        self.checkboxes = None
        self.proceed_button = None
        self.layout = None
        self.variable_layout = None
        self.selected_nodes = []  # To track selected nodes
        self.node_info = {}  # Store info for selected nodes
        self.selected_variables = []  # Variables selected by the user
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Node Manage")
        self.setGeometry(200, 100, 1400, 900)

        # Scrollable Area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        container_widget = QWidget()
        self.layout = QVBoxLayout(container_widget)

        scroll_area.setWidget(container_widget)

        # Fetch and display all nodes
        nodes = nodesInNeo4j()
        self.addNodes_labels(nodes)

        # Set main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def addNodes_labels(self, nodes):
        grid_layout = QGridLayout()
        for index, node in enumerate(nodes):
            checkbox = QCheckBox(node)
            checkbox.setStyleSheet("""
                font-size: 18px;
                padding: 10px;
                background-color: pink;
                color: white;
                border: 2px solid #ccc;
                border-radius: 15px;
                """)
            checkbox.setFixedSize(200, 60)
            checkbox.stateChanged.connect(lambda state, n=node: self.toggle_node_selection(state, n))
            row, col = divmod(index, 4)
            grid_layout.addWidget(checkbox, row, col)

        self.layout.addLayout(grid_layout)

        # Add a button to proceed
        self.proceed_button = QPushButton("Proceed")
        self.proceed_button.setStyleSheet("""
                font-size: 18px;
                padding: 10px;
                background-color: pink;
                color: white;
                border: 2px solid #ccc;
                border-radius: 15px;    
            """)
        self.proceed_button.clicked.connect(self.proceed_to_relationship)
        self.layout.addWidget(self.proceed_button)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()

        # Add start to add node button
        self.start_button = QPushButton("Start to add a new node")
        self.start_button.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background-color: green;
            color: white;
            border: 2px solid #ccc;
            border-radius: 25px;
        """)
        self.start_button.setFixedSize(260, 60)
        self.start_button.clicked.connect(self.start_to_add_node)
        button_layout.addWidget(self.start_button)

        # Add app terminate button
        self.terminate_button = QPushButton("Terminate The APP")
        self.terminate_button.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background-color: orange;
            color: white;
            border: 2px solid #ccc;
            border-radius: 25px;
        """)
        self.terminate_button.setFixedSize(200, 60)
        self.terminate_button.clicked.connect(self.terminate_app)
        button_layout.addWidget(self.terminate_button)

        # Add the horizontal layout to the main layout
        self.layout.addLayout(button_layout)

    def toggle_node_selection(self, state, node):
        """Track selected nodes"""
        if state == 2:  # Checked
            if len(self.selected_nodes) < 2:
                self.selected_nodes.append(node)
            else:
                QMessageBox.warning(self, "Limit Reached", "You can only select two nodes!")
        elif state == 0:  # Unchecked
            if node in self.selected_nodes:
                self.selected_nodes.remove(node)

    def proceed_to_relationship(self):
        """Fetch node info and proceed to relationship creation"""
        if len(self.selected_nodes) != 2:
            QMessageBox.warning(self, "Invalid Selection", "Please select exactly two nodes!")
            return

        # Fetch node info for both selected nodes
        self.node_info = {node: set(nodeInfoFetch(node)) for node in self.selected_nodes}

        # Get the intersection of the two node infos
        common_variables = self.node_info[self.selected_nodes[0]].intersection(self.node_info[self.selected_nodes[1]])

        if not common_variables:
            QMessageBox.warning(self, "No Common Variables", "No common variables found between the selected nodes!")
            return

        # Display variable selection UI
        self.display_variable_selection(common_variables)

    def display_variable_selection(self, common_variables):
        """Display variable selection UI for creating relationships"""

        # Clear the orign layout
        self.clear_layout(self.layout)

        self.variable_layout = QVBoxLayout()

        # Add the return button
        back_button = QPushButton("Back")
        back_button.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background-color: lightblue;
            color: black;
            border: 2px solid #ccc;
            border-radius: 15px;
        """)
        back_button.clicked.connect(self.back_to_node_selection)
        self.layout.addWidget(back_button)

        label = QLabel(f"Select variables to link {self.selected_nodes[0]} and {self.selected_nodes[1]}:")
        label.setStyleSheet("""
            font-size: 35px;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.variable_layout.addWidget(label)

        # Display checkboxes for each common variable
        self.checkboxes = {}
        for variable in common_variables:
            variable_layout = QHBoxLayout()

            # Label for variable
            variable_label = QLabel(variable)
            variable_label.setStyleSheet("font-size: 25px;")
            variable_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

            # Checkbox for variable
            checkbox = QCheckBox()

            # Add label and checkbox to layout
            variable_layout.addWidget(variable_label)
            variable_layout.addWidget(checkbox)
            variable_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.variable_layout.addLayout(variable_layout)
            self.checkboxes[variable] = checkbox

        # Add a button to create the relationship
        create_button = QPushButton("Create Relationship")
        create_button.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background-color: pink;
            color: white;
            border: 2px solid #ccc;
            border-radius: 15px;    
        """)
        create_button.clicked.connect(self.create_relationship)
        self.variable_layout.addWidget(create_button)

        # Add relationship input box
        relation_layout = QHBoxLayout()
        relation_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        relation_label = QLabel("Please enter your relation here:")
        relation_label.setStyleSheet("""
            font-size: 18px;
        """)

        relation_layout.addWidget(relation_label)

        self.input_box = QLineEdit()
        self.input_box.setStyleSheet("""
            font-size: 16px;
            padding: 5px;
        """)
        relation_layout.addWidget(self.input_box)

        # Ensure proper alignment
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(relation_layout)

        self.layout.addLayout(self.variable_layout)

    def create_relationship(self):
        """Create a relationship based on selected variables"""
        # Get selected variables
        self.selected_variables = [var for var, checkbox in self.checkboxes.items() if checkbox.isChecked()]

        if not self.selected_variables:
            QMessageBox.warning(self, "No Variables Selected", "Please select at least one variable!")
            return
        # Get the input relationship name
        relationship = self.input_box.text()

        # Call a function to create the relationship in Neo4j
        self.create_relationship_in_neo4j(self.selected_nodes[0], self.selected_nodes[1], self.selected_variables, relationship)

    def create_relationship_in_neo4j(self, node1, node2, selected_variables, relationship):
        """Function to create a relationship in Neo4j"""
        g = Graph(st.secrets["NEO4J_URI"], auth=(st.secrets["NEO4J_USERNAME"], st.secrets["NEO4J_PASSWORD"]))

        conditions = " AND ".join([f"a.{var} = b.{var}" for var in selected_variables])
        query = f"""
        MATCH (a:{node1}), (b:{node2})
        WHERE {conditions}
        CREATE (a)-[:{relationship}]->(b)
        """
        try:
            g.run(query)
            QMessageBox.information(self, "Success", "Relationship created successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create relationship: {str(e)}")

    def clear_layout(self, layout):
        """Clear all widgets and sub-layouts from the given layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def back_to_node_selection(self):
        """Return to the node choice page"""
        self.clear_layout(self.layout)

        # Reset selected nodes
        self.selected_nodes = []

        # Reload the initial nodes selection UI
        nodes = nodesInNeo4j()  # Fetch nodes again if needed
        self.addNodes_labels(nodes)

        # Set layout to the original one
        self.layout.setAlignment(Qt.AlignmentFlag(0))

    def start_to_add_node(self):
        self.add_page = SelectNodeFolder()
        self.add_page.show()
        self.close()

    def terminate_app(self):
        self.close()
