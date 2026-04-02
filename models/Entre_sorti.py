"""
Nous implémenterons ici les fonctions liées à la lecture et l'écriture sur le disque
"""
import csv
import datetime
import io
from json import JSONDecoder, JSONEncoder

from PyQt6.QtWidgets import QTableWidget, QFileDialog, QMessageBox

from models.Entete import textes, liste_entete
import models.Tableau_statistique as ts

global_filter = "Fichier Landtistik (*.ltk)"
csv_filter = "Fichier CSV (*.csv)"


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
        for k, v in texte_json.items():
            if not v == []:
                ts.inserer_colone(tableau, k)
            ts.remplir_colone(tableau, k, v)

        return filename

    else:
        return False


def importer_csv(self, tableau: QTableWidget):
    """
    Importe des données depuis un fichier CSV dans le tableau.
    Le CSV doit avoir au moins deux colonnes : modalités et effectifs.

    :param self:
    :param tableau: tableau cible
    :return: nom du fichier ou False
    """
    filename, _filter = QFileDialog.getOpenFileName(
        self, "Importer un fichier CSV", filter=csv_filter
    )
    if not filename:
        return False

    try:
        with open(filename, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            rows = list(reader)

        if not rows:
            QMessageBox.warning(self, "Fichier vide", "Le fichier CSV est vide.")
            return False

        # Detect delimiter (try comma if semicolon gave 1 column)
        if len(rows[0]) == 1:
            with open(filename, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=",")
                rows = list(reader)

        # Skip header row if it contains non-numeric data in 2nd column
        start_row = 0
        if rows and len(rows[0]) >= 2:
            try:
                float(rows[0][1])
            except ValueError:
                start_row = 1

        data_rows = rows[start_row:]
        if not data_rows:
            QMessageBox.warning(self, "Données invalides", "Aucune donnée trouvée dans le fichier.")
            return False

        ts.nettoyer_tableau(tableau)
        for i in range(len(data_rows)):
            tableau.insertRow(i)

        # Fill modalités and effectifs
        for row_idx, row in enumerate(data_rows):
            if len(row) >= 1:
                tableau.setItem(row_idx, 0, __import__('PyQt6').QtWidgets.QTableWidgetItem(str(row[0]).strip()))
            if len(row) >= 2:
                # Insert effectif column if needed
                if tableau.columnCount() < 2:
                    ts.inserer_colone(tableau, textes.effectif)
                tableau.setItem(row_idx, 1, __import__('PyQt6').QtWidgets.QTableWidgetItem(str(row[1]).strip()))

        return filename

    except Exception as e:
        erreur(e)
        QMessageBox.critical(self, "Erreur d'import", f"Impossible de lire le fichier CSV :\n{e}")
        return False


def exporter_csv(self, tableau: QTableWidget):
    """
    Exporte le tableau vers un fichier CSV.

    :param self:
    :param tableau: tableau à exporter
    :return: nom du fichier ou False
    """
    filename, _filter = QFileDialog.getSaveFileName(
        self, "Exporter en CSV", filter=csv_filter
    )
    if not filename:
        return False

    try:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";")

        # Header
        headers = [
            tableau.horizontalHeaderItem(col).text()
            for col in range(tableau.columnCount())
        ]
        writer.writerow(headers)

        # Data rows (exclude last total row)
        for row in range(tableau.rowCount()):
            row_data = []
            for col in range(tableau.columnCount()):
                item = tableau.item(row, col)
                row_data.append(item.text() if item else "")
            writer.writerow(row_data)

        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            f.write(output.getvalue())

        return filename

    except Exception as e:
        erreur(e)
        QMessageBox.critical(self, "Erreur d'export", f"Impossible d'exporter en CSV :\n{e}")
        return False


def erreur(motif: Exception):
    txt = f"""
    ------------------------------------------------------------------------------
    Problème survenu le {datetime.datetime.now()}
    Énoncé : {motif.__str__()}
    Trace: {motif.__traceback__.tb_frame if motif.__traceback__ else 'N/A'}
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
