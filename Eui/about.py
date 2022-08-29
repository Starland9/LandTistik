
        
import about
from PyQt6.QtWidgets import QMainWindow

class About(QMainWindow, about.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        
