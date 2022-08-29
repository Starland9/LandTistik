"""
Salut landry, j'ai beaucoup changé ma façon de coder et je deviens de plus en plus mature pour le maintien de mes
codes.
Tout d'abord, nous sommes le 2 aout 2022 et je recommence les codes de lantistik afin de le rendre vraiment plus
maintenable sur le long terme. Je sais mais bon...

"""

import sys
import qdarktheme
from PyQt6.QtWidgets import QApplication

from Eui import home

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    window = home.Home()
    window.showMaximized()
    sys.exit(app.exec())
