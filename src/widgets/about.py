import src.ui.about as about
from PyQt6.QtWidgets import QMainWindow, QDialog


class About(QDialog, about.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btnOk.clicked.connect(self.close)
