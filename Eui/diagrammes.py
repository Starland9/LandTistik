from PyQt6.QtWidgets import QMainWindow, QTableWidget

from Cui import diagrammes
from Models import Tableau_statistique as ts
from Models.Entete import textes as col
import matplotlib.pyplot as plt


class Diagrammes(QMainWindow, diagrammes.Ui_MainWindow):
    def __init__(self, tableau: QTableWidget):
        """
        On va travailler sur les digrammes ici

        :param tableau:
        """
        super(Diagrammes, self).__init__()
        self.setupUi(self)

        self.tableau = tableau
        plt.grid()

    def bande(self):
        """
        Creation et affichage du diagramme à bande

        :return:
        """
        x = ts.obtenir_tableau_grace_au_nom(self.tableau, col.modalite)
        y = ts.obtenir_tableau_grace_au_nom(self.tableau, col.effectif)
        plt.xlabel(col.modalite)
        plt.ylabel(col.effectif)
        plt.title("Diagramme à bande des effectifs en fonction des modalités")
        plt.bar(x, y)

        plt.show()
