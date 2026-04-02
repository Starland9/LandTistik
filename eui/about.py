from cui import about
from PyQt6.QtWidgets import QDialog


class About(QDialog, about.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
