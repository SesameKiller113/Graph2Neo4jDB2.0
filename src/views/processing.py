import sys
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QProgressBar, QLabel, QPushButton
)
from util.graphImport import startImport


class FileProcessingThread(QThread):
    progress_signal = pyqtSignal(int, int)  # Signal to update progress (current_index, total_files)

    def __init__(self, DataFolder, node_name):
        super().__init__()
        self.DataFolder = DataFolder
        self.node_name = node_name

    def run(self):
        """Run the file processing in a separate thread."""
        startImport(self.DataFolder, self.node_name, self.progress_signal.emit)


class FileProcessing(QMainWindow):
    def __init__(self, DataFolder, node_name):
        super().__init__()
        self.node_manage_page = None
        self.setWindowTitle("File Processing Progress")
        self.setGeometry(300, 300, 400, 200)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # Label
        self.label = QLabel("Processing files...")
        self.label.setStyleSheet("font-size: 30px; color: orange")
        self.layout.addWidget(self.label)

        # Percentage label
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.percentage_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 20px;
                border: 1px solid #bbb;
                border-radius: 5px;
                background: #eee;
            }
            QProgressBar::chunk {
                background-color: #0a6df0;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.progress_bar)

        # Finished button
        self.finished_button = QPushButton("Finished")
        self.finished_button.clicked.connect(self.backToNodeManage)

        # Start the file processing thread
        self.thread = FileProcessingThread(DataFolder, node_name)
        self.thread.progress_signal.connect(self.progress_callback)
        self.thread.finished.connect(self.onProcessingFinished)
        self.thread.start()

    def progress_callback(self, current_index, total_files):
        """Update the progress bar and percentage label."""
        percentage = int((current_index / total_files) * 100)
        self.progress_bar.setValue(percentage)
        self.percentage_label.setText(f"{percentage}%")

    def onProcessingFinished(self):
        """Handle the event when processing is finished."""
        self.label.setText("All files processed!")
        self.layout.addWidget(self.finished_button)

    def backToNodeManage(self):
        from views.nodeManage import NodeManage
        self.node_manage_page = NodeManage()
        self.node_manage_page.show()
        self.close()
