from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from src.ui import home
from src.widgets import about
import pandas as pd


class Home(QMainWindow, home.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.window_about = None
        self.window_diagrams = None
        self.setupUi(self)
        self.current_file = None

        self.manage_actions()

        self.table_data_frame = pd.DataFrame.from_dict(
            {
                "Modalités": [],
                "Effectifs": [],
                "Frequence": [],
                "Centre": [],
                "Repartition": [],
                "Densité": [],
            },
        )

        self.update_table_from_dataframe()

    def manage_actions(self):
        self.actionA_prop_os.triggered.connect(self.show_about)
        self.btn_add.clicked.connect(self.add_row)

    def show_about(self):
        self.window_about = about.About()
        self.window_about.show()

    def update_table_from_dataframe(self):
        self.tab.setRowCount(len(self.table_data_frame))
        self.tab.setColumnCount(len(self.table_data_frame.columns))
        self.tab.setHorizontalHeaderLabels(self.table_data_frame.columns)
        for i in range(len(self.table_data_frame)):
            for j in range(len(self.table_data_frame.columns)):
                self.tab.setItem(
                    i, j, QTableWidgetItem(str(self.table_data_frame.iloc[i, j]))
                )

    def update_dataframe_from_table(self):
        df_map = {}
        for i in range(self.tab.rowCount()):
            for j in range(self.tab.columnCount()):
                if self.tab.item(i, j) is None:
                    continue
                df_map[self.tab.horizontalHeaderItem(j).text()] = self.tab.item(i, j).text()

        print("df : ", self.table_data_frame.describe())

    def add_row(self):
        self.tab.setRowCount(self.tab.rowCount() + 1)
        self.update_dataframe_from_table()
