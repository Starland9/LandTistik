"""
LandTistik — Logiciel de statistiques open-source pour étudiants.
"""

import sys
import pyqtdarktheme
from PyQt6.QtWidgets import QApplication

from eui import home

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(pyqtdarktheme.load_stylesheet("dark"))
    window = home.Home()
    window.showMaximized()
    sys.exit(app.exec())

