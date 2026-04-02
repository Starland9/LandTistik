"""
Dans ce module, nous allons travailler sur les fonctions de la première interface.
"""

from cui import home
from PyQt6.QtWidgets import (
    QMainWindow, QMessageBox, QApplication, QLabel, QDialog,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QDialogButtonBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from models.Tableau_statistique import (
    ControlTableau, FusionType,
    completer_colones, donner_les_totaux, inserer_colone,
    nettoyer_tableau, obtenir_tableau_grace_au_nom, TypeModalite
)
from models.Entete import textes as noms_colones
from models.Entre_sorti import (
    ouvrir_un_fichier, enregistrer_fichier, enregistrer_fichier_sous,
    importer_csv, exporter_csv
)
from models import Statistiques as stat
import numpy as np
from eui import diagrammes


class Home(QMainWindow, home.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.window_diagrammes = None
        self.setupUi(self)
        self.fichier_courant = None
        self._theme_sombre = True

        self._configurer_interface()
        self.gestion_des_actions()
        self.statusBar().showMessage(
            "Bienvenue dans LandTistik — logiciel de statistiques pour étudiants")

    # ─── Configuration initiale de l'interface ────────────────────────────────

    def _configurer_interface(self):
        """Configure les éléments supplémentaires de l'interface."""
        # Activer les alternances de couleurs dans le tableau
        self.tab.setAlternatingRowColors(True)
        self.tab.horizontalHeader().setStretchLastSection(True)

        # Raccourcis clavier
        QShortcut(QKeySequence("Ctrl+Return"), self, self.ajout_ligne)
        QShortcut(QKeySequence("Delete"), self, self.supprimer_ligne)
        QShortcut(QKeySequence("Ctrl+T"), self, self.completer_le_tableau)

        # Enrichir le dock des paramètres avec les nouvelles statistiques
        self._etendre_panneau_parametres()

    def _etendre_panneau_parametres(self):
        """Ajoute les nouvelles étiquettes statistiques au panneau de paramètres."""
        from PyQt6.QtWidgets import QFormLayout

        extra_stats = [
            ("mediane_label", "mediane_value", "Médiane :"),
            ("mode_label", "mode_value", "Mode :"),
            ("variance_label", "variance_value", "Variance :"),
            ("ecart_type_label", "ecart_type_value", "Écart-type :"),
            ("q1_label", "q1_value", "Q1 (1er quartile) :"),
            ("q3_label", "q3_value", "Q3 (3e quartile) :"),
            ("iqr_label", "iqr_value", "Écart interquartile :"),
            ("cv_label", "cv_value", "Coeff. de variation (%) :"),
            ("etendue_label", "etendue_value", "Étendue :"),
            ("n_label", "n_value", "N (Total) :"),
        ]
        for label_name, value_name, text in extra_stats:
            lbl = QLabel(text, self.groupBox)
            val = QLabel("—", self.groupBox)
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            setattr(self, label_name, lbl)
            setattr(self, value_name, val)
            self.formLayout.addRow(lbl, val)

    # ─── Gestion des actions ──────────────────────────────────────────────────

    def gestion_des_actions(self):
        """Connecte tous les signaux de l'interface."""
        # Boutons principaux
        self.btn_add.clicked.connect(self.ajout_ligne)
        self.btn_complete_tab.clicked.connect(self.completer_le_tableau)
        self.btnDiagrammes.clicked.connect(self.voir_diagrammes)
        self.btn_calcul_params.clicked.connect(self.calculer_parametres)

        # Menu Tableau — insertions de colonnes
        self.actionEffectifs.triggered.connect(self.insertion_effectifs)
        self.actionF_quences.triggered.connect(self.insertion_frequences)
        self.actionCentre.triggered.connect(self.insertion_centre)
        self.actionAmplitude.triggered.connect(self.insertion_amplitude)
        self.actionDensit.triggered.connect(self.insertion_densite)

        # Menu Fichier
        self.actionNouveau.triggered.connect(self.nouveau_fichier)
        self.action_Ouvrir.triggered.connect(self.ouvrir_fichier)
        self.action_Enregistrer.triggered.connect(self.enregistrer_fichier)
        self.actionEnregistrer_sous.triggered.connect(
            self.enregistrer_fichier_sous)
        self.actionQuitter.triggered.connect(QApplication.quit)

        # Menu Édition
        self.action_Reinitialiser_les_donn_es.triggered.connect(
            self._reinitialiser)

        # Menu Diagrammes
        self.actionBandes.triggered.connect(
            lambda: self.voir_diagrammes("bandes"))
        self.actionCamamberg.triggered.connect(
            lambda: self.voir_diagrammes("camembert"))
        self.actionNuage_de_points.triggered.connect(
            lambda: self.voir_diagrammes("nuage"))
        self.actionTrac.triggered.connect(
            lambda: self.voir_diagrammes("ogive"))
        self.actionCourb.triggered.connect(
            lambda: self.voir_diagrammes("courbe"))

        # Menu Personnalisation — thèmes
        self.action_Clair.triggered.connect(
            lambda: self._changer_theme("light"))
        self.action_Sombre.triggered.connect(
            lambda: self._changer_theme("dark"))

        # Menu Aide
        self.actionA_prop_os.triggered.connect(self._afficher_apropos)

        # Import/Export CSV : ajouter dans le menu Fichier
        self._ajouter_actions_csv()

    def _ajouter_actions_csv(self):
        """Ajoute les actions Import/Export CSV au menu Fichier."""
        from PyQt6.QtGui import QAction
        sep = self.menu_Fichier.insertSeparator(self.actionQuitter)

        self.actionImportCSV = QAction("Importer CSV...", self)
        self.actionImportCSV.setShortcut("Ctrl+I")
        self.actionExportCSV = QAction("Exporter CSV...", self)
        self.actionExportCSV.setShortcut("Ctrl+E")

        self.menu_Fichier.insertAction(
            self.actionQuitter, self.actionImportCSV)
        self.menu_Fichier.insertAction(
            self.actionQuitter, self.actionExportCSV)

        self.actionImportCSV.triggered.connect(self._importer_csv)
        self.actionExportCSV.triggered.connect(self._exporter_csv)

        # Bouton supprimer ligne dans la barre des boutons
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtGui import QIcon
        self.btn_del = QPushButton("Supprimer la ligne", self.centralwidget)
        self.btn_del.setStyleSheet(
            "*{height:25px;width:150px;color:rgb(255,255,255);background-color:rgba(180,30,30,0.8);}"
            ":hover{background-color:rgba(220,50,50,0.9);}"
        )
        self.btn_del.clicked.connect(self.supprimer_ligne)
        self.horizontalLayout.insertWidget(1, self.btn_del)

    # ─── Actions du tableau ───────────────────────────────────────────────────

    def ajout_ligne(self):
        """Ajoute une nouvelle ligne avant la ligne TOTAL."""
        self.tab.insertRow(self.tab.rowCount() - 1)
        self.statusBar().showMessage("Ligne ajoutée")

    def supprimer_ligne(self):
        """Supprime la ligne sélectionnée (sauf la ligne TOTAL)."""
        current = self.tab.currentRow()
        if current < 0:
            QMessageBox.information(
                self, "Supprimer", "Veuillez sélectionner une ligne à supprimer.")
            return
        if current == self.tab.rowCount() - 1:
            QMessageBox.warning(self, "Supprimer",
                                "Impossible de supprimer la ligne TOTAL.")
            return
        self.tab.removeRow(current)
        self.statusBar().showMessage("Ligne supprimée")

    def completer_le_tableau(self):
        """Complète le tableau après validation."""
        control = ControlTableau().tableau_valide(self.tab)
        if control is not True:
            QMessageBox.information(self, "Vérifier le tableau", control)
            return False

        completer_colones(self.tab)
        donner_les_totaux(self.tab)
        self.statusBar().showMessage("Tableau complété avec succès")
        return True

    def _reinitialiser(self):
        """Réinitialise le tableau avec confirmation."""
        rep = QMessageBox.question(
            self, "Réinitialiser",
            "Voulez-vous vraiment effacer toutes les données ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if rep == QMessageBox.StandardButton.Yes:
            nettoyer_tableau(self.tab)
            self.fichier_courant = None
            self.setWindowTitle("LandTistik")
            self.statusBar().showMessage("Tableau réinitialisé")

    # ─── Actions du menu Fichier ──────────────────────────────────────────────

    def ouvrir_fichier(self):
        """Ouvre un fichier .ltk depuis le disque."""
        self.fichier_courant = ouvrir_un_fichier(self, self.tab)
        if self.fichier_courant:
            self.setWindowTitle(f"LandTistik — {self.fichier_courant}")
            self.statusBar().showMessage(
                f"Fichier ouvert : {self.fichier_courant}")

    def enregistrer_fichier(self):
        """Enregistre le fichier courant (ou ouvre 'Enregistrer sous' si aucun)."""
        if self.completer_le_tableau():
            if not self.fichier_courant:
                self.fichier_courant = enregistrer_fichier_sous(self, self.tab)
            else:
                enregistrer_fichier(self.fichier_courant, self.tab)
            if self.fichier_courant:
                self.setWindowTitle(f"LandTistik — {self.fichier_courant}")
                self.statusBar().showMessage(
                    f"Fichier enregistré : {self.fichier_courant}")

    def enregistrer_fichier_sous(self):
        """Enregistre dans un nouveau fichier .ltk."""
        if self.completer_le_tableau():
            self.fichier_courant = enregistrer_fichier_sous(self, self.tab)
            if self.fichier_courant:
                self.setWindowTitle(f"LandTistik — {self.fichier_courant}")
                self.statusBar().showMessage(
                    f"Fichier enregistré : {self.fichier_courant}")
            return bool(self.fichier_courant)
        return False

    def _importer_csv(self):
        """Importe des données depuis un fichier CSV."""
        result = importer_csv(self, self.tab)
        if result:
            self.statusBar().showMessage(f"CSV importé : {result}")
            QMessageBox.information(
                self, "Import réussi",
                "Les données ont été importées.\nVous pouvez maintenant compléter le tableau."
            )

    def _exporter_csv(self):
        """Exporte le tableau vers un fichier CSV."""
        result = exporter_csv(self, self.tab)
        if result:
            self.statusBar().showMessage(f"CSV exporté : {result}")
            QMessageBox.information(
                self, "Export réussi", f"Données exportées vers :\n{result}")

    def nouveau_fichier(self):
        """Crée un nouveau fichier en sauvegardant d'abord l'actuel."""
        if self.fichier_courant:
            self.enregistrer_fichier()
            nettoyer_tableau(self.tab)
        else:
            saved = self.enregistrer_fichier_sous()
            if saved or QMessageBox.question(
                self, "Nouveau fichier",
                "Continuer sans sauvegarder ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes:
                nettoyer_tableau(self.tab)
        self.fichier_courant = None
        self.setWindowTitle("LandTistik")
        self.statusBar().showMessage("Nouveau fichier créé")

    # ─── Insertions de colonnes ───────────────────────────────────────────────

    def insertion_effectifs(self):
        """Insère les colonnes d'effectifs."""
        self.actionEffectifs.setEnabled(False)
        inserer_colone(self.tab, noms_colones.effectif)
        inserer_colone(self.tab, noms_colones.modalite_x_effectif)
        inserer_colone(self.tab, noms_colones.ecc)
        inserer_colone(self.tab, noms_colones.ecd)

    def insertion_frequences(self):
        """Insère les colonnes de fréquences."""
        self.actionF_quences.setEnabled(False)
        inserer_colone(self.tab, noms_colones.frequence)
        inserer_colone(self.tab, noms_colones.fcc)
        inserer_colone(self.tab, noms_colones.fcd)

    def insertion_amplitude(self):
        """Insère la colonne des amplitudes."""
        self.actionAmplitude.setEnabled(False)
        inserer_colone(self.tab, noms_colones.amplitude)

    def insertion_densite(self):
        """Insère la colonne des densités."""
        self.actionDensit.setEnabled(False)
        inserer_colone(self.tab, noms_colones.densite)

    def insertion_centre(self):
        """Insère la colonne des centres de classes."""
        self.actionCentre.setEnabled(False)
        inserer_colone(self.tab, noms_colones.centre)

    # ─── Calcul des paramètres statistiques ──────────────────────────────────

    def calculer_parametres(self):
        """Calcule et affiche tous les paramètres statistiques."""
        if not self.completer_le_tableau():
            return

        if TypeModalite().obtenir_type_mod(self.tab) != TypeModalite.numeric:
            QMessageBox.information(
                self, "Calcul impossible",
                "Le calcul des paramètres nécessite des modalités numériques."
            )
            return

        mods = obtenir_tableau_grace_au_nom(self.tab, noms_colones.modalite)
        eff = obtenir_tableau_grace_au_nom(self.tab, noms_colones.effectif)

        if mods is False or eff is False:
            return

        mods = mods.astype(float)
        resume = stat.resume_statistique(mods, eff)

        # Mise à jour des spinbox existants
        self.moyenne_artihmetique_double_spin.setValue(
            resume["Moyenne arithmétique"])
        self.moyenneGOmTriqueDoubleSpinBox.setValue(
            resume["Moyenne géométrique"])
        self.tauxDeVariationDoubleSpinBox.setValue(
            stat.taux_de_variation(mods)
        )

        # Mise à jour des nouvelles étiquettes
        mapping = {
            "mediane_value": resume["Médiane"],
            "mode_value": resume["Mode"],
            "variance_value": resume["Variance"],
            "ecart_type_value": resume["Écart-type"],
            "q1_value": resume["Q1 (1er quartile)"],
            "q3_value": resume["Q3 (3e quartile)"],
            "iqr_value": resume["Écart interquartile"],
            "cv_value": resume["Coeff. de variation (%)"],
            "etendue_value": resume["Étendue"],
            "n_value": resume["N (Total)"],
        }
        for attr, value in mapping.items():
            if hasattr(self, attr):
                getattr(self, attr).setText(str(value))

        self.statusBar().showMessage("Paramètres calculés avec succès")
        self._afficher_resume_statistique(resume)

    def _afficher_resume_statistique(self, resume: dict):
        """Affiche une boîte de dialogue avec le résumé statistique complet."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Résumé statistique")
        dialog.resize(420, 380)
        layout = QVBoxLayout(dialog)

        table = QTableWidget(len(resume), 2, dialog)
        table.setHorizontalHeaderLabels(["Paramètre", "Valeur"])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        for row, (key, value) in enumerate(resume.items()):
            table.setItem(row, 0, QTableWidgetItem(key))
            table.setItem(row, 1, QTableWidgetItem(str(value)))

        layout.addWidget(table)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    # ─── Visualisations ───────────────────────────────────────────────────────

    def voir_diagrammes(self, type_diagramme: str = "bandes"):
        """Affiche les diagrammes dans une nouvelle fenêtre."""
        if not self.completer_le_tableau():
            return
        self.window_diagrammes = diagrammes.Diagrammes(self.tab)
        # doit précéder afficher() pour initialiser le rendu Qt
        self.window_diagrammes.show()
        self.window_diagrammes.afficher(type_diagramme)

    # ─── Thèmes ───────────────────────────────────────────────────────────────

    def _changer_theme(self, theme: str):
        """Change le thème de l'application (dark/light)."""
        try:
            import qdarktheme as pyqtdarktheme
            QApplication.instance().setStyleSheet(pyqtdarktheme.load_stylesheet(theme))
            self._theme_sombre = (theme == "dark")
            self.statusBar().showMessage(
                f"Thème {'sombre' if theme == 'dark' else 'clair'} appliqué")
        except ImportError:
            QMessageBox.warning(
                self, "Thème", "Module pyqtdarktheme non disponible.")

    # ─── Aide / À propos ──────────────────────────────────────────────────────

    def _afficher_apropos(self):
        """Affiche la boîte de dialogue À propos."""
        QMessageBox.about(
            self,
            "À propos de LandTistik",
            """<h2>LandTistik</h2>
            <p>Logiciel de statistiques open-source pour étudiants.</p>
            <p><b>Version :</b> 2.0</p>
            <p><b>Technologies :</b> Python 3, PyQt6, NumPy, Matplotlib, SciPy</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
              <li>Tableaux statistiques complets (ECC, ECD, Fréquences…)</li>
              <li>Calcul automatique : moyenne, médiane, mode, variance, quartiles…</li>
              <li>Diagrammes : bandes, camembert, ogive, polygone des fréquences</li>
              <li>Import/Export CSV</li>
              <li>Thèmes clair et sombre</li>
            </ul>
            """
        )
