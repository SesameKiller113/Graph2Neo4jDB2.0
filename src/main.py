import sys
from PyQt6.QtWidgets import QApplication

from views.graphInitialization import GraphInitialization


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = GraphInitialization()
    main_window.show()
    sys.exit(app.exec())