
import sys
import qdarktheme
from PyQt6.QtWidgets import QApplication

from widgets import home

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    window = home.Home()
    window.show()
    sys.exit(app.exec())
