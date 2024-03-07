import datetime

from PyQt6.QtWidgets import QTableWidget, QFileDialog

global_filter = "Fichier Landtistik (*.ltk)"


def open_file(self, tableau: QTableWidget):
    pass


def error(cause: Exception):
    txt = f"""
    ------------------------------------------------------------------------------
    Problème survenu le {datetime.datetime.now()}
    Énoncé : {cause.__str__()}
    Trace: {cause.__traceback__.tb_frame}
    ------------------------------------------------------------------------------
    """

    with open("landlog.txt", "a") as file:
        file.write(txt)


def save_file(nom_du_fichier: str, tableau: QTableWidget):
    pass


def save_file_as(self, tableau: QTableWidget):
    pass
