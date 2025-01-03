import sys
from PyQt6.QtWidgets import QApplication

from views.nodeManage import NodeManage


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = NodeManage()
    main_window.show()
    sys.exit(app.exec())