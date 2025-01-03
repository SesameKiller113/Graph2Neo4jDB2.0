from PyQt6.QtCore import Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QLabel, QFrame, QApplication, QScrollArea, QHBoxLayout, QPushButton, QMessageBox
)
from views.columnMapping import ColumnMapping


class ColumnDefine(QWidget):
    def __init__(self, DataFolder, node_name):
        super().__init__()
        self.setWindowTitle("Column Define View")
        self.setGeometry(200, 100, 1400, 900)

        # Main layout for the window
        main_layout = QHBoxLayout(self)

        # Left panel for draggable texts
        self.left_panel = QScrollArea()
        self.left_panel.setWidgetResizable(True)
        left_content = QWidget()
        self.left_panel.setWidget(left_content)

        self.left_layout = QGridLayout(left_content)
        main_layout.addWidget(self.left_panel, 1)

        # Add draggable labels
        self.column_labels = {}
        columns = DataFolder.get_all_col_names()
        self.add_draggable_labels(columns)

        # Right panel for DropBox
        self.box_panel = QScrollArea()
        self.box_panel.setWidgetResizable(True)
        box_content = QWidget()
        self.box_panel.setWidget(box_content)

        self.box_layout = QGridLayout(box_content)
        main_layout.addWidget(self.box_panel, 3)

        # Add a single DropBox
        self.box = DropBox()
        self.box_layout.addWidget(self.box, 0, 0)
        self.box.dropped.connect(self.update_box_contents)

        # Add "Next Step" button
        self.next_step_button = QPushButton("Next Step")
        self.next_step_button.setFixedHeight(50)
        self.next_step_button.setFixedWidth(120)
        self.next_step_button.setStyleSheet("background-color: #0a6df0; color: white;")
        self.next_step_button.clicked.connect(self.next_step)
        main_layout.addWidget(self.next_step_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Set main layout
        self.setLayout(main_layout)

        # Prepare for the next window
        self.node_name = node_name
        self.columnMapping = None
        self.selected_columns = []  # Single list to track all selected columns
        self.DataFolder = DataFolder

    def add_draggable_labels(self, columns):
        """Add draggable labels for each column name"""
        for index, column in enumerate(columns):
            label = DraggableLabel(column, index, self)
            self.column_labels[index] = label
            row, col = divmod(index, 2)  # Arrange in two columns
            self.left_layout.addWidget(label, row, col)

    def restore_label(self, label):
        """Restore label to its original position if not dropped in any box"""
        if label.index in self.column_labels:
            label.setParent(self.left_panel.widget())
            label.show()
            row, col = divmod(label.index, 2)
            self.left_layout.addWidget(label, row, col)

            # Remove label's text from `selected_columns`
            if label.text() in self.selected_columns:
                self.selected_columns.remove(label.text())
                print(f"Removed {label.text()} from selected columns")

    def update_box_contents(self, column_name, label):
        """Update box contents when a label is dropped into the box"""
        # Add the column name to the selected columns if not already present
        if column_name not in self.selected_columns:
            self.selected_columns.append(column_name)

        # Place the label visually in the DropBox
        label.setParent(self.box)
        label.show()
        row, col = divmod(len(self.selected_columns) - 1, 4)
        self.box.layout.addWidget(label, row, col)

        print(f"Selected columns: {self.selected_columns}")

    def next_step(self):
        """Handle transition to the next step"""
        if not self.selected_columns:
            QMessageBox.critical(self, "Error", "You need to select at least one column before proceeding!")
            return

        # Placeholder for the next step
        print("Transitioning to the next step...")
        print(f"Selected columns: {self.selected_columns}")

        # Show the columnMapping page and close the columnDefine page
        self.columnMapping = ColumnMapping(self.DataFolder, self.selected_columns, self.node_name)
        self.columnMapping.show()
        self.close()


class DraggableLabel(QLabel):
    def __init__(self, text, index, parent):
        super().__init__(text)
        self.index = index
        self.parent = parent
        self.setFixedSize(200, 50)  # Larger size for better visibility
        self.setStyleSheet(
            "background-color: #2196F3; color: white; font-size: 16px; padding: 10px; border-radius: 8px;"
        )
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mouseMoveEvent(self, event):
        """Handle dragging of the label"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.text())
            drag.setMimeData(mime_data)

            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())

            result = drag.exec(Qt.DropAction.MoveAction)
            if result != Qt.DropAction.MoveAction:
                self.parent.restore_label(self)


class DropBox(QFrame):
    dropped = pyqtSignal(str, DraggableLabel)

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.Box)
        self.setAcceptDrops(True)
        self.setStyleSheet(
            "background-color: #f0f0f0; border: 2px dashed #aaa; border-radius: 8px;"
        )

        # Layout for labels
        self.layout = QGridLayout()
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event):
        """Allow drag operation if text data is available"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event and add label to box"""
        text = event.mimeData().text()
        source_label = event.source()
        event.acceptProposedAction()
        self.dropped.emit(text, source_label)

