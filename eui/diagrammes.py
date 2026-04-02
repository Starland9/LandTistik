"""
Module de visualisation des diagrammes statistiques.
Le visualiseur travaille sur une copie des données afin d'éviter tout couplage
instable avec le QTableWidget principal pendant le rendu.
"""

from models.Statistiques import frequences, frequences_cumulees_croissantes
from models.Entete import textes as col
from models import Tableau_statistique as ts
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import QTimer
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from dataclasses import dataclass
import matplotlib

matplotlib.use("QtAgg")


_TYPES = {
    "bandes": "Diagramme en bandes (effectifs)",
    "camembert": "Diagramme camembert (effectifs)",
    "ogive": "Ogive (fréquences cumulées croissantes)",
    "courbe": "Polygone des fréquences",
    "nuage": "Nuage de points",
    "boite": "Boîte à moustaches",
}


@dataclass(slots=True)
class DonneesDiagramme:
    modalites: np.ndarray
    effectifs: np.ndarray
    is_numeric: bool


def preparer_donnees(tableau) -> DonneesDiagramme:
    """Extrait et valide les données nécessaires au rendu des diagrammes."""
    modalites = ts.obtenir_tableau_grace_au_nom(tableau, col.modalite)
    effectifs = ts.obtenir_tableau_grace_au_nom(tableau, col.effectif)

    if modalites is False or effectifs is False:
        raise ValueError(
            "Données insuffisantes dans le tableau. Ajoutez d'abord la colonne des effectifs."
        )

    modalites = np.asarray(modalites)
    effectifs = np.asarray(effectifs, dtype=float)

    if modalites.ndim != 1 or effectifs.ndim != 1:
        raise ValueError(
            "Les données du diagramme doivent être unidimensionnelles.")
    if modalites.size == 0 or effectifs.size == 0:
        raise ValueError("Le tableau ne contient aucune donnée à tracer.")
    if modalites.size != effectifs.size:
        raise ValueError(
            "Les modalités et les effectifs n'ont pas la même taille.")
    if not np.all(np.isfinite(effectifs)):
        raise ValueError("Les effectifs contiennent des valeurs invalides.")
    if np.any(effectifs < 0):
        raise ValueError("Les effectifs doivent être positifs ou nuls.")
    if np.sum(effectifs) <= 0:
        raise ValueError(
            "La somme des effectifs doit être strictement positive.")

    is_numeric = ts.TypeModalite().obtenir_type_mod(
        tableau) == ts.TypeModalite.numeric
    if is_numeric:
        try:
            modalites = modalites.astype(float)
        except ValueError as exc:
            raise ValueError(
                "Les modalités numériques sont invalides.") from exc

    return DonneesDiagramme(
        modalites=modalites.copy(),
        effectifs=effectifs.copy(),
        is_numeric=is_numeric,
    )


class _MplCanvas(FigureCanvas):
    """Canvas matplotlib embarqué dans la fenêtre Qt."""

    def __init__(self, parent=None):
        figure = Figure(figsize=(8, 5))
        self.axes = figure.add_subplot(111)
        super().__init__(figure)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)


class Diagrammes(QMainWindow):
    """Fenêtre autonome de rendu des diagrammes."""

    def __init__(self, donnees: DonneesDiagramme, parent=None):
        super().__init__(parent)
        self._donnees = donnees
        self._type_en_attente = "bandes"

        self.setWindowTitle("LandTistik — Visualiseur de diagrammes")
        self.resize(960, 640)

        self.canvas = _MplCanvas(self)
        self.message_label = QLabel("")
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: rgb(210, 80, 80);")

        self.combo_type = QComboBox()
        for key, label in _TYPES.items():
            self.combo_type.addItem(label, key)

        btn_afficher = QPushButton("Afficher")
        btn_afficher.clicked.connect(self._afficher_depuis_combo)

        btn_exporter = QPushButton("Exporter image...")
        btn_exporter.clicked.connect(self._exporter_image)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(QLabel("Type de diagramme :"))
        toolbar_layout.addWidget(self.combo_type)
        toolbar_layout.addWidget(btn_afficher)
        toolbar_layout.addWidget(btn_exporter)
        toolbar_layout.addStretch()

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.message_label)
        layout.addWidget(self.canvas)
        self.setCentralWidget(central_widget)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._tracer_type_en_attente)

    def afficher(self, type_diagramme: str = "bandes"):
        """Programme l'affichage du diagramme demandé."""
        index = self.combo_type.findData(type_diagramme)
        if index >= 0:
            self.combo_type.setCurrentIndex(index)
            self._type_en_attente = type_diagramme
        else:
            self._type_en_attente = "bandes"

        if self.isVisible():
            QTimer.singleShot(0, self._tracer_type_en_attente)

    def _afficher_depuis_combo(self):
        self._type_en_attente = self.combo_type.currentData() or "bandes"
        self._tracer_type_en_attente()

    def _tracer_type_en_attente(self):
        self._tracer(self._type_en_attente)

    def _tracer(self, type_diagramme: str):
        axes = self.canvas.axes
        axes.clear()
        self.message_label.clear()

        try:
            traceur = {
                "bandes": self._bandes,
                "camembert": self._camembert,
                "ogive": self._ogive,
                "courbe": self._courbe_frequences,
                "nuage": self._nuage_points,
                "boite": self._boite_moustaches,
            }.get(type_diagramme, self._bandes)

            traceur()
        except Exception as exc:
            self._afficher_erreur(str(exc))

        self.canvas.figure.tight_layout()
        self.canvas.draw_idle()

    def _bandes(self):
        axes = self.canvas.axes
        x_labels = [str(valeur) for valeur in self._donnees.modalites]
        y = self._donnees.effectifs

        bars = axes.bar(range(len(y)), y, color="#1e71a3",
                        edgecolor="white", alpha=0.9)
        axes.set_xticks(range(len(x_labels)))
        axes.set_xticklabels(x_labels, rotation=30, ha="right")
        axes.set_xlabel(col.modalite)
        axes.set_ylabel(col.effectif)
        axes.set_title("Diagramme en bandes des effectifs")
        axes.grid(axis="y", alpha=0.35)

        decalage = max(float(np.max(y)) * 0.02, 0.1)
        for bar, valeur in zip(bars, y):
            axes.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + decalage,
                f"{valeur:g}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    def _camembert(self):
        axes = self.canvas.axes
        y = self._donnees.effectifs
        axes.pie(
            y,
            labels=[str(valeur) for valeur in self._donnees.modalites],
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white"},
        )
        axes.set_title("Diagramme camembert des effectifs")
        axes.axis("equal")

    def _ogive(self):
        axes = self.canvas.axes
        fcc = frequences_cumulees_croissantes(self._donnees.effectifs)

        if self._donnees.is_numeric:
            x_values = self._donnees.modalites.astype(float)
            axes.step(x_values, fcc, where="post",
                      color="#e07b39", linewidth=2)
            axes.plot(x_values, fcc, "o", color="#e07b39", markersize=5)
        else:
            x_pos = np.arange(len(fcc))
            axes.step(x_pos, fcc, where="post", color="#e07b39", linewidth=2)
            axes.plot(x_pos, fcc, "o", color="#e07b39", markersize=5)
            axes.set_xticks(x_pos)
            axes.set_xticklabels(
                [str(valeur) for valeur in self._donnees.modalites], rotation=30, ha="right")

        axes.set_xlabel(col.modalite)
        axes.set_ylabel("FCC")
        axes.set_ylim(0, 1.05)
        axes.set_title("Ogive des fréquences cumulées croissantes")
        axes.grid(alpha=0.3)

    def _courbe_frequences(self):
        axes = self.canvas.axes
        fi = frequences(self._donnees.effectifs)

        if self._donnees.is_numeric:
            x_values = self._donnees.modalites.astype(float)
            axes.plot(x_values, fi, marker="o", color="#4caf50",
                      linewidth=2, markersize=6)
            axes.fill_between(x_values, fi, alpha=0.2, color="#4caf50")
        else:
            x_pos = np.arange(len(fi))
            axes.plot(x_pos, fi, marker="o", color="#4caf50",
                      linewidth=2, markersize=6)
            axes.fill_between(x_pos, fi, alpha=0.2, color="#4caf50")
            axes.set_xticks(x_pos)
            axes.set_xticklabels(
                [str(valeur) for valeur in self._donnees.modalites], rotation=30, ha="right")

        axes.set_xlabel(col.modalite)
        axes.set_ylabel("Fréquences (Fi)")
        axes.set_title("Polygone des fréquences")
        axes.grid(alpha=0.3)

    def _nuage_points(self):
        axes = self.canvas.axes
        y = self._donnees.effectifs.astype(float)

        if self._donnees.is_numeric:
            x_values = self._donnees.modalites.astype(float)
            axes.scatter(x_values, y, color="#9c27b0",
                         alpha=0.85, edgecolors="white", s=60)
        else:
            x_pos = np.arange(len(y))
            axes.scatter(x_pos, y, color="#9c27b0",
                         alpha=0.85, edgecolors="white", s=60)
            axes.set_xticks(x_pos)
            axes.set_xticklabels(
                [str(valeur) for valeur in self._donnees.modalites], rotation=30, ha="right")

        axes.set_xlabel(col.modalite)
        axes.set_ylabel(col.effectif)
        axes.set_title("Nuage de points")
        axes.grid(alpha=0.3)

    def _boite_moustaches(self):
        if not self._donnees.is_numeric:
            raise ValueError(
                "La boîte à moustaches nécessite des modalités numériques.")

        repetitions = np.rint(self._donnees.effectifs).astype(int)
        repetitions = np.clip(repetitions, 0, None)
        if np.sum(repetitions) == 0:
            raise ValueError(
                "Impossible de construire une boîte à moustaches avec des effectifs nuls.")

        expanded = np.repeat(
            self._donnees.modalites.astype(float), repetitions)
        axes = self.canvas.axes
        axes.boxplot(
            expanded,
            vert=True,
            patch_artist=True,
            boxprops={"facecolor": "#1e71a3", "alpha": 0.7},
            medianprops={"color": "orange", "linewidth": 2},
        )
        axes.set_ylabel(col.modalite)
        axes.set_title("Boîte à moustaches")
        axes.grid(axis="y", alpha=0.3)

    def _afficher_erreur(self, message: str):
        self.message_label.setText(message)
        self.canvas.axes.text(
            0.5,
            0.5,
            f"Erreur : {message}",
            transform=self.canvas.axes.transAxes,
            ha="center",
            va="center",
            color="red",
            fontsize=12,
        )

    def _exporter_image(self):
        """Exporte le graphique courant en image PNG/PDF/SVG."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le graphique",
            filter="PNG (*.png);;PDF (*.pdf);;SVG (*.svg)",
        )
        if filename:
            self.canvas.figure.savefig(filename, dpi=150, bbox_inches="tight")
