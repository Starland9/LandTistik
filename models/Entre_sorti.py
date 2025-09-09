"""
Nous implémenterons ici les fonctions liées à la lecture et l'écriture sur le disque
"""
import datetime
from json import JSONDecoder, JSONEncoder

from PyQt6.QtWidgets import QTableWidget, QFileDialog

from Models.Entete import textes, liste_entete
import Models.Tableau_statistique as ts

global_filter = "Fichier Landtistik (*.ltk)"


def ouvrir_un_fichier(self, tableau: QTableWidget):
    """
    Fonction permettant d'ouvrir un fichier et de charger son contenu dans un tableau.
    Les fichiers ici pour le moment sont des fichiers '.json'.

    :param self:
    :param tableau: tableau qui obtiendra les données du fichier
    """
    filename, _filter = QFileDialog.getOpenFileName(self, "Choisir le fichier à ouvrir", filter=global_filter)
    texte_json = None
    if filename:
        with open(filename, "r") as json:
            texte_json = JSONDecoder().decode(json.read().__str__())

    if texte_json:
        ts.nettoyer_tableau(tableau)
        texte_json = dict(texte_json)
        [tableau.insertRow(i) for i in range(len(texte_json[textes.modalite]))]
        # print(texte_json)
        for k, v in texte_json.items():
            if not v == []:
                ts.inserer_colone(tableau, k)
            ts.remplir_colone(tableau, k, v)

        return filename

    else:
        return False


def erreur(motif: Exception):
    txt = f"""
    ------------------------------------------------------------------------------
    Problème survenu le {datetime.datetime.now()}
    Énoncé : {motif.__str__()}
    Trace: {motif.__traceback__.tb_frame}
    ------------------------------------------------------------------------------
    """

    with open("landlog.txt", "a") as file:
        file.write(txt)


def enregistrer_fichier(nom_du_fichier: str, tableau: QTableWidget):
    """
    Fonction permettant d'enregistrer un fichier sur le disque.

    :param nom_du_fichier: nom du fichier dans lequel seront stockées les données
    :param tableau: tableau à transformer en json
    """

    data_a_enregistrer = {}
    try:
        for cle in liste_entete:
            tab = ts.obtenir_tableau_grace_au_nom(tableau, cle)
            if type(tab) == bool:
                data_a_enregistrer.__setitem__(cle, [])
            else:
                data_a_enregistrer.__setitem__(cle, tab.tolist())
    except ValueError as e:
        return erreur(e)
    data_en_json = JSONEncoder().encode(data_a_enregistrer)
    with open(nom_du_fichier, "w") as fichier_ltk:
        fichier_ltk.write(data_en_json)
    return True


def enregistrer_fichier_sous(self, tableau: QTableWidget):
    """
    Fonction qui permet de sauvegarder les données du tableau dans un fichier sur le disque tout en ouvrant la boite de
    dialogue.
    Les fichiers sont au format .ltk

    :param self:
    :param tableau:
    """
    filename, _filter = QFileDialog.getSaveFileName(self, "Enregistrer le fichier", filter=global_filter)
    if filename:
        enregistrer_fichier(filename, tableau)
        return filename
