from PyQt6.QtWidgets import QMainWindow, QMessageBox
from src.ui import home
from src.widgets import about


class Home(QMainWindow, home.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.window_about = None
        self.window_diagrams = None
        self.setupUi(self)
        self.current_file = None

        self.manage_actions()

    def manage_actions(self):
        self.actionA_prop_os.triggered.connect(self.show_about)

    def show_about(self):
        self.window_about = about.About()
        self.window_about.show()
