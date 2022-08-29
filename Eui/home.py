"""
Dans ce module, nous allons travailler sur les fonctions de la premiere interface, nous les implémenterons peu à peu.
"""

from Cui import home
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from Models.Tableau_statistique import *
from Models.Entete import textes as noms_colones
from Models.Entre_sorti import *
from Eui import diagrammes


class Home(QMainWindow, home.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.window_diagrammes = None
        self.setupUi(self)
        # Fichier sur lequel on travaille actuellement
        self.fichier_courant = None

        # remplir_le_tableau_au_debut(self.tab)

        #     On dépose le gestionnaire des actions ici
        self.gestion_des_actions()

    def gestion_des_actions(self):
        """
        Fonction qui va se charger de toutes les actions que nous ferons sur l'interface

        """
        #         ajout d'une nouvelle ligne
        self.btn_add.clicked.connect(self.ajout_ligne)
        #     Completion du tableau
        self.btn_complete_tab.clicked.connect(self.completer_le_tableau)
        self.btnDiagrammes.clicked.connect(self.voir_diagrammes)

        #     Insertion des nouvelles colones
        self.actionEffectifs.triggered.connect(self.insertion_effectifs)
        self.actionF_quences.triggered.connect(self.insertion_frequences)
        self.actionCentre.triggered.connect(self.insertion_centre)
        self.actionAmplitude.triggered.connect(self.insertion_amplitude)
        self.actionDensit.triggered.connect(self.insertion_densite)

        #     Actions du menu Fichier
        self.actionNouveau.triggered.connect(self.nouveau_fichier)
        self.action_Ouvrir.triggered.connect(self.ouvrir_fichier)
        self.action_Enregistrer.triggered.connect(self.enregistrer_fichier)
        self.actionEnregistrer_sous.triggered.connect(self.enregistrer_fichier_sous)

    def ajout_ligne(self):
        """
        Fonction d'ajout d'une nouvelle ligne

        :return:
        """
        self.tab.insertRow(self.tab.rowCount() - 1)

    def completer_le_tableau(self):
        """
        Completion apres verification du tableau

        :return:
        """

        # On controle d'abord le tableau
        control = ControlTableau().tableau_valide(self.tab)
        if not control is True:
            QMessageBox.information(self, "Verifier le tableau", control)
            return False

        #         Ensuite, on donne les totaux
        completer_colones(self.tab)
        donner_les_totaux(self.tab)
        return True

    # Actions du menu Fichier
    def ouvrir_fichier(self):
        """
        Ouvrir le fichier sur le disque
        """
        # if self.completer_le_tableau():
        self.fichier_courant = ouvrir_un_fichier(self, self.tab)

    def enregistrer_fichier(self):
        """
        Enregistrer le fichier sur le disque sans ouvrir la boite de dialogue
        """
        if self.completer_le_tableau():
            if not self.fichier_courant:
                self.fichier_courant = enregistrer_fichier_sous(self, self.tab)
            else:
                enregistrer_fichier(self.fichier_courant, self.tab)

    def enregistrer_fichier_sous(self):
        """
        Enregistrer le fichier sur le disque avec ouverture de la boite de dialogue
        """
        if self.completer_le_tableau():
            self.fichier_courant = enregistrer_fichier_sous(self, self.tab)
            return True

    # Actions du menu d'insertion
    def insertion_effectifs(self):
        """
        Insertion de la colone des effectifs

        :return:
        """
        self.actionEffectifs.setEnabled(False)
        inserer_colone(self.tab, noms_colones.effectif)
        inserer_colone(self.tab, noms_colones.modalite_x_effectif)
        inserer_colone(self.tab, noms_colones.ecc)
        inserer_colone(self.tab, noms_colones.ecd)

    def insertion_frequences(self):
        """
        insertion des colones des fréquences

        :return:
        """
        self.actionF_quences.setEnabled(False)
        inserer_colone(self.tab, noms_colones.frequence)
        inserer_colone(self.tab, noms_colones.fcc)
        inserer_colone(self.tab, noms_colones.fcd)

    def insertion_amplitude(self):
        """
        insertion des colones des amplitudes

        :return:
        """
        self.actionAmplitude.setEnabled(False)
        inserer_colone(self.tab, noms_colones.amplitude)

    def insertion_densite(self):
        """
        insertion des colones des densités

        :return:
        """
        self.actionDensit.setEnabled(False)
        inserer_colone(self.tab, noms_colones.densite)

    def insertion_centre(self):
        """
        insertion des colones des centres

        :return:
        """
        self.actionCentre.setEnabled(False)
        inserer_colone(self.tab, noms_colones.centre)

    def nouveau_fichier(self):
        """
        On crée un nouveau fichier

        :return:
        """
        if self.fichier_courant:
            self.enregistrer_fichier()
            nettoyer_tableau(self.tab)
        else:
            if self.enregistrer_fichier_sous():
                nettoyer_tableau(self.tab)

    def voir_diagrammes(self):
        """
        On consulte juste les diagrammes

        :return:
        """
        self.window_diagrammes = diagrammes.Diagrammes(self.tab)
        self.window_diagrammes.bande()
        self.window_diagrammes.show()

