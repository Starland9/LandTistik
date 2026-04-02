"""
Module de visualisation des diagrammes statistiques.
Prend en charge : bandes (barres), camembert, ogive, polygone des fréquences, nuage de points.
"""

from models.Entete import textes as col
from models import Tableau_statistique as ts
from cui import diagrammes as cui_diag
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QComboBox, QLabel, QSizePolicy
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use("QtAgg")


_TYPES = {
    "bandes": "Diagramme en bandes (effectifs)",
    "camembert": "Diagramme camembert (fréquences)",
    "ogive": "Ogive (fréquences cumulées croissantes)",
    "courbe": "Polygone des fréquences",
    "nuage": "Nuage de points",
    "boite": "Boîte à moustaches",
}


class _MplCanvas(FigureCanvas):
    """Widget matplotlib intégré dans PyQt6."""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 5), tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)


class Diagrammes(QMainWindow, cui_diag.Ui_MainWindow):
    def __init__(self, tableau: QTableWidget):
        """
        Fenêtre de visualisation des diagrammes.

        :param tableau: tableau statistique principal
        """
        super().__init__()
        self.setupUi(self)
        self.tableau = tableau
        self.setWindowTitle("LandTistik — Visualiseur de diagrammes")

        # Canvas matplotlib embarqué
        self.canvas = _MplCanvas(self)

        # Barre de sélection du type de diagramme
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.addWidget(QLabel("Type de diagramme :"))
        self.combo_type = QComboBox()
        for key, label in _TYPES.items():
            self.combo_type.addItem(label, key)
        toolbar_layout.addWidget(self.combo_type)
        btn_afficher = QPushButton("Afficher")
        btn_afficher.clicked.connect(self._afficher_depuis_combo)
        toolbar_layout.addWidget(btn_afficher)
        btn_exporter = QPushButton("Exporter image…")
        btn_exporter.clicked.connect(self._exporter_image)
        toolbar_layout.addWidget(btn_exporter)
        toolbar_layout.addStretch()

        # Assemblage dans le layout de la fenêtre
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.addWidget(toolbar_widget)
        vbox.addWidget(self.canvas)
        self.setCentralWidget(container)
        self.resize(900, 600)

    # ─── API publique ─────────────────────────────────────────────────────────

    def afficher(self, type_diagramme: str = "bandes"):
        """Affiche le diagramme demandé."""
        idx = self.combo_type.findData(type_diagramme)
        if idx >= 0:
            self.combo_type.setCurrentIndex(idx)
        self._tracer(type_diagramme)

    # ─── Tracé ────────────────────────────────────────────────────────────────

    def _afficher_depuis_combo(self):
        key = self.combo_type.currentData()
        self._tracer(key)

    def _tracer(self, type_diagramme: str):
        self.canvas.axes.clear()
        try:
            x_raw = ts.obtenir_tableau_grace_au_nom(self.tableau, col.modalite)
            y_raw = ts.obtenir_tableau_grace_au_nom(self.tableau, col.effectif)

            if x_raw is False or y_raw is False:
                self._erreur_tracé("Données insuffisantes dans le tableau.")
                return

            is_numeric = ts.TypeModalite().obtenir_type_mod(
                self.tableau) == ts.TypeModalite.numeric

            if type_diagramme == "bandes":
                self._bandes(x_raw, y_raw, is_numeric)
            elif type_diagramme == "camembert":
                self._camembert(x_raw, y_raw)
            elif type_diagramme == "ogive":
                self._ogive(x_raw, y_raw, is_numeric)
            elif type_diagramme == "courbe":
                self._courbe_frequences(x_raw, y_raw, is_numeric)
            elif type_diagramme == "nuage":
                self._nuage_points(x_raw, y_raw, is_numeric)
            elif type_diagramme == "boite":
                self._boite_moustaches(x_raw, y_raw, is_numeric)
            else:
                self._bandes(x_raw, y_raw, is_numeric)

        except Exception as e:
            self._erreur_tracé(str(e))

        try:
            self.canvas.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:
            self._erreur_tracé(str(e))

    def _bandes(self, x, y, is_numeric: bool):
        """Diagramme en barres des effectifs."""
        ax = self.canvas.axes
        x_labels = [str(v) for v in x]
        bars = ax.bar(range(len(y)), y, color="#1e71a3",
                      edgecolor="white", alpha=0.85)
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=30, ha="right")
        ax.set_xlabel(col.modalite)
        ax.set_ylabel(col.effectif)
        ax.set_title("Diagramme en bandes des effectifs")
        ax.grid(axis="y", alpha=0.4)
        for bar, val in zip(bars, y):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(int(val)), ha="center", va="bottom", fontsize=9)

    def _camembert(self, x, y):
        """Diagramme camembert des fréquences."""
        ax = self.canvas.axes
        labels = [str(v) for v in x]
        wedges, texts, autotexts = ax.pie(
            y, labels=labels, autopct="%1.1f%%",
            startangle=90, pctdistance=0.8,
            wedgeprops=dict(edgecolor="white")
        )
        ax.set_title("Diagramme camembert des effectifs")
        ax.axis("equal")

    def _ogive(self, x, y, is_numeric: bool):
        """Ogive des fréquences cumulées croissantes."""
        ax = self.canvas.axes
        from models.Statistiques import frequences_cumulees_croissantes
        fcc = frequences_cumulees_croissantes(y.astype(float))
        if is_numeric:
            x_vals = x.astype(float)
            ax.step(x_vals, fcc, where="post", color="#e07b39", linewidth=2)
            ax.plot(x_vals, fcc, "o", color="#e07b39", markersize=5)
        else:
            x_pos = np.arange(len(fcc))
            ax.step(x_pos, fcc, where="post", color="#e07b39", linewidth=2)
            ax.plot(x_pos, fcc, "o", color="#e07b39", markersize=5)
            ax.set_xticks(x_pos)
            ax.set_xticklabels([str(v) for v in x], rotation=30, ha="right")
        ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="100%")
        ax.set_xlabel(col.modalite)
        ax.set_ylabel("FCC")
        ax.set_title("Ogive des fréquences cumulées croissantes")
        ax.grid(alpha=0.3)
        ax.legend()

    def _courbe_frequences(self, x, y, is_numeric: bool):
        """Polygone des fréquences."""
        ax = self.canvas.axes
        from models.Statistiques import frequences
        fi = frequences(y.astype(float))
        if is_numeric:
            x_vals = x.astype(float)
            ax.plot(x_vals, fi, marker="o", color="#4caf50",
                    linewidth=2, markersize=6)
            ax.fill_between(x_vals, fi, alpha=0.2, color="#4caf50")
        else:
            x_pos = np.arange(len(fi))
            ax.plot(x_pos, fi, marker="o", color="#4caf50",
                    linewidth=2, markersize=6)
            ax.fill_between(x_pos, fi, alpha=0.2, color="#4caf50")
            ax.set_xticks(x_pos)
            ax.set_xticklabels([str(v) for v in x], rotation=30, ha="right")
        ax.set_xlabel(col.modalite)
        ax.set_ylabel("Fréquences (Fi)")
        ax.set_title("Polygone des fréquences")
        ax.grid(alpha=0.3)

    def _nuage_points(self, x, y, is_numeric: bool):
        """Nuage de points (scatter plot)."""
        ax = self.canvas.axes
        if is_numeric:
            x_vals = x.astype(float)
            ax.scatter(x_vals, y.astype(float), color="#9c27b0",
                       alpha=0.8, edgecolors="white", s=60)
            ax.set_xlabel(col.modalite)
        else:
            x_pos = np.arange(len(y))
            ax.scatter(x_pos, y.astype(float), color="#9c27b0",
                       alpha=0.8, edgecolors="white", s=60)
            ax.set_xticks(x_pos)
            ax.set_xticklabels([str(v) for v in x], rotation=30, ha="right")
            ax.set_xlabel(col.modalite)
        ax.set_ylabel(col.effectif)
        ax.set_title("Nuage de points")
        ax.grid(alpha=0.3)

    def _boite_moustaches(self, x, y, is_numeric: bool):
        """Boîte à moustaches (box plot)."""
        ax = self.canvas.axes
        if not is_numeric:
            self._erreur_tracé(
                "La boîte à moustaches nécessite des modalités numériques.")
            return
        expanded = np.repeat(x.astype(float), y.astype(int))
        bp = ax.boxplot(expanded, vert=True, patch_artist=True,
                        boxprops=dict(facecolor="#1e71a3", alpha=0.7),
                        medianprops=dict(color="orange", linewidth=2))
        ax.set_ylabel(col.modalite)
        ax.set_title("Boîte à moustaches")
        ax.grid(axis="y", alpha=0.3)

    def _erreur_tracé(self, msg: str):
        ax = self.canvas.axes
        ax.text(0.5, 0.5, f"Erreur : {msg}", transform=ax.transAxes,
                ha="center", va="center", color="red", fontsize=12)

    # ─── Export image ─────────────────────────────────────────────────────────

    def _exporter_image(self):
        """Exporte le graphique courant en image PNG/PDF."""
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporter le graphique",
            filter="PNG (*.png);;PDF (*.pdf);;SVG (*.svg)"
        )
        if filename:
            self.canvas.fig.savefig(filename, dpi=150, bbox_inches="tight")
