"""Le but ici est de créer une bibliothèque qui va se charger de nous donner toutes les fonctions et méthodes qui vont
nous servir à gérer notre tableau statistique.

"""
import numpy as np
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


from models.Entete import entete_et_index, liste_entete, textes
from models.Entre_sorti import erreur


_ALIASES_ENTETES = {
    textes.modalite: {"Modaltés (Xi)", "Modalités (Xi)"},
}


def nettoyer_tableau(tableau: QTableWidget):
    """
    Fonction permettant de nettoyer le tableau

    :param tableau:
    :return:
    """
    for i in range(tableau.rowCount() - 1):
        tableau.removeRow(0)
    for i in range(tableau.columnCount() - 1):
        tableau.removeColumn(tableau.columnCount() - 1)


def remplir_le_tableau_au_debut(tableau: QTableWidget):
    """
    Fonction juste pour remplir le tableau au debut
    :param tableau: le tableau a etudier

    :return:
    """
    tableau.setRowCount(10)
    tableau.insertColumn(1)
    for row in range(tableau.rowCount() - 1):
        for col in range(tableau.columnCount()):
            tableau.setItem(row, col, QTableWidgetItem(
                f"{(55 + row) * col + row}" + (f" mod" if col == 0 else "0")))


def initialiser_entete_par_defaut(tableau: QTableWidget):
    """Assure que la première colonne est celle des modalités."""
    if tableau.columnCount() == 0:
        tableau.insertColumn(0)
    tableau.setHorizontalHeaderItem(0, QTableWidgetItem(textes.modalite))


def obtenir_indice_colonne(tableau: QTableWidget, nom_colonne: str | None = None, indice: int | None = None):
    """Retourne l'indice réel d'une colonne dans le tableau."""
    if indice is not None:
        return indice if 0 <= indice < tableau.columnCount() else None

    if nom_colonne is None:
        return None

    cibles = {nom_colonne, *_ALIASES_ENTETES.get(nom_colonne, set())}
    for col in range(tableau.columnCount()):
        header_item = tableau.horizontalHeaderItem(col)
        if header_item and header_item.text() in cibles:
            return col
    return None


def colonne_existe(tableau: QTableWidget, nom_colonne: str) -> bool:
    """Indique si une colonne donnée existe réellement dans le tableau."""
    return obtenir_indice_colonne(tableau, nom_colonne=nom_colonne) is not None


def obtenir_tableau_grace_au_nom(tableau_des_donnes: QTableWidget, nom_colonne=None, indice=None):
    """
    Fonction permettant d'obtenir un tableau de données à partir d'un nom de colonne

    :param indice: indice à donner si on veut cibler la colone grace a son indice
    :param tableau_des_donnes:
    :param nom_colonne: nom à donner pour obtenir la colonne
    :return:
    """

    col = obtenir_indice_colonne(
        tableau_des_donnes, nom_colonne=nom_colonne, indice=indice)
    if col is None:
        return False

    try:
        col_modalite = obtenir_indice_colonne(
            tableau_des_donnes, nom_colonne=textes.modalite)
        tableau = [
            tableau_des_donnes.item(row, col).text() if not TypeModalite().obtenir_type_mod(
                tableau_des_donnes) == TypeModalite().numeric and col == 0 else
            float(tableau_des_donnes.item(row, col).text())
            for row in range(tableau_des_donnes.rowCount() - 1)]
        if col_modalite is not None and col != 0 and not TypeModalite().obtenir_type_mod(
                tableau_des_donnes) == TypeModalite().numeric:
            tableau = [
                tableau_des_donnes.item(row, col).text() if col == col_modalite else
                float(tableau_des_donnes.item(row, col).text())
                for row in range(tableau_des_donnes.rowCount() - 1)
            ]
        return np.array(tableau)
    except AttributeError as e:
        # Ici peut-être on ne trouve pas la bonne colonne ou la ligne a un type 'none'. Il faut donc ouvrir une
        #  boite de dialogue pour dire qu'il y a l'un de ces PB !!!
        erreur(e)
        return False


def remplir_colone(tableau: QTableWidget, nom_colone: str, elements: list):
    """
    Remplir une colonne du tableau à partir du nom de la colonne et des elements
    :param tableau:
    :param nom_colone:
    :param elements:
    """
    colonne = obtenir_indice_colonne(tableau, nom_colonne=nom_colone)
    if colonne is None:
        return
    for ligne in range(tableau.rowCount() - 1):
        try:
            tableau.setItem(
                ligne, colonne, QTableWidgetItem(str(elements[ligne])))
        except IndexError:
            continue


def moyenne_colone(tableau: QTableWidget, nom_colone):
    """
    Fonction calcul moyenne d'une des colones du tableau

    :param tableau:
    :param nom_colone:
    :return:
    """
    colone = obtenir_tableau_grace_au_nom(tableau, nom_colone)
    return np.mean(colone)


class FusionType:
    """
    Fonction sommer plusieurs colonnes en une seule

    """
    addition = 1
    soustraction = 2
    multiplication = 3
    division = 4


def obtenir_fusion_colones(tableau: QTableWidget, liste_des_colones: tuple,
                           fusion_type: FusionType = FusionType.multiplication):
    """
    On implémente la fusion des colonnes par rapport à certains critères comme l'addition ou la multiplication

    :param tableau:
    :param liste_des_colones:
    :param fusion_type:
    :return:
    """
    big_data = [obtenir_tableau_grace_au_nom(
        tableau, colone) for colone in liste_des_colones]
    if fusion_type == FusionType.addition:
        return np.array(big_data).sum(axis=0)
    elif fusion_type == FusionType.multiplication:
        return np.array(big_data).prod(axis=0)
    else:
        return False


class ControlTableau:
    """
    On implémente une classe ici qui va se charger de controller plusieurs aspects du tableau
    controle si le tableau est bien rempli comme il faut.
    """

    class ProblemesDuTableau:
        """
        Les different problèmes qu'on peut retrouver
        """
        colonne_effectif_absente = "La colonne des effectifs est absente. Utilisez Tableau > Effectifs."
        celules_vides = "Il y a des cellules vides dans le tableau"
        texte_dans_tableau = "Il y a du texte dans certains endroits du tableau"

    @staticmethod
    def celules_remplis(tableau: QTableWidget):
        """
        On controle si toutes les cellules sont remplies

        :param tableau:
        :return:
        """
        for row in range(tableau.rowCount() - 1):
            for col in range(tableau.columnCount()):
                if col in [0, 1]:
                    try:
                        _ = tableau.item(row, col).text()
                    except AttributeError:
                        return False
                    except TypeError:
                        return False
        return True

    @staticmethod
    def texte_dans_tableau(tableau: QTableWidget):
        """
        Controle de texte dans le tableau

        :param tableau:
        :return:
        """
        for row in range(tableau.rowCount() - 1):
            for col in range(1, 2):
                try:
                    float(tableau.item(row, col).text())
                except ValueError:
                    return True
                except AttributeError:
                    return False

        return False

    def tableau_valide(self, tableau: QTableWidget):
        """
        Controle totale du tableau

        :param tableau:
        :return: Problème du tableau
        """
        if not colonne_existe(tableau, textes.effectif):
            return self.ProblemesDuTableau.colonne_effectif_absente
        if not self.celules_remplis(tableau):
            return self.ProblemesDuTableau.celules_vides
        if self.texte_dans_tableau(tableau):
            return self.ProblemesDuTableau.texte_dans_tableau

        return True


def donner_les_totaux(tableau: QTableWidget):
    """
    On donne tous les totaux de chaque colones

    :param tableau:
    :return:
    """
    ligne_du_total = tableau.rowCount() - 1
    for colone in range(1, tableau.columnCount()):
        try:
            somme_colone = obtenir_tableau_grace_au_nom(
                tableau, indice=colone).sum()
            tableau.setItem(ligne_du_total, colone,
                            QTableWidgetItem(f"{somme_colone}"))
        except AttributeError:
            pass


class TypeModalite:
    numeric = 0
    char = 1

    def obtenir_type_mod(self, tableau: QTableWidget):
        for i in range(tableau.rowCount() - 1):
            try:
                _ = float(tableau.item(i, 0).text())
            except Exception as e:
                erreur(e)
                return self.char

        return self.numeric


def completer_colones(tableau: QTableWidget):
    """
    Ici, on va dans le tableau et on regarde le type de la colonne des modalités. Ensuite on effectue ceci:
    si ce sont des chiffres, on fait mod * effectif
    si ce sont des chars, on fait mod * eff = eff

    Calcule également ECC, ECD, Fréquences, FCC, FCD, Centre, Amplitude et Densité si les colonnes existent.

    :param tableau:
    :return:
    """
    import models.Statistiques as stat

    mods_raw = obtenir_tableau_grace_au_nom(tableau, textes.modalite)
    eff = obtenir_tableau_grace_au_nom(tableau, textes.effectif)
    if eff is False or mods_raw is False:
        return

    is_numeric = TypeModalite().obtenir_type_mod(tableau) == TypeModalite.numeric

    # ─── Xi * Ni ──────────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.modalite_x_effectif):
        try:
            if is_numeric:
                mods = mods_raw.astype(float)
                remplir_colone(tableau, textes.modalite_x_effectif, list(
                    stat.modalites_x_effectifs(mods, eff)))
            else:
                remplir_colone(tableau, textes.modalite_x_effectif, list(eff))
        except Exception as e:
            erreur(e)

    # ─── ECC ──────────────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.ecc):
        try:
            remplir_colone(tableau, textes.ecc, list(
                stat.effectifs_cumules_croissants(eff)))
        except Exception as e:
            erreur(e)

    # ─── ECD ──────────────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.ecd):
        try:
            remplir_colone(tableau, textes.ecd, list(
                stat.effectifs_cumules_decroissants(eff)))
        except Exception as e:
            erreur(e)

    # ─── Fréquences ──────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.frequence):
        try:
            fi = stat.frequences(eff)
            remplir_colone(tableau, textes.frequence, [
                           round(float(v), 4) for v in fi])
        except Exception as e:
            erreur(e)

    # ─── FCC ─────────────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.fcc):
        try:
            remplir_colone(tableau, textes.fcc,
                           [round(float(v), 4) for v in stat.frequences_cumulees_croissantes(eff)])
        except Exception as e:
            erreur(e)

    # ─── FCD ─────────────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.fcd):
        try:
            remplir_colone(tableau, textes.fcd,
                           [round(float(v), 4) for v in stat.frequences_cumulees_decroissantes(eff)])
        except Exception as e:
            erreur(e)

    # ─── Centre ──────────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.centre):
        try:
            mods_list = [
                tableau.item(row, 0).text()
                for row in range(tableau.rowCount() - 1)
            ]
            centres = stat.centres_classes(mods_list)
            if centres is not None:
                remplir_colone(tableau, textes.centre, [
                               round(float(v), 4) for v in centres])
        except Exception as e:
            erreur(e)

    # ─── Amplitude ───────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.amplitude):
        try:
            mods_list = [
                tableau.item(row, 0).text()
                for row in range(tableau.rowCount() - 1)
            ]
            amplitudes = stat.amplitudes_classes(mods_list)
            if amplitudes is not None:
                remplir_colone(tableau, textes.amplitude, [
                               round(float(v), 4) for v in amplitudes])
        except Exception as e:
            erreur(e)

    # ─── Densité ─────────────────────────────────────────────────────────────
    if colonne_existe(tableau, textes.densite):
        try:
            mods_list = [
                tableau.item(row, 0).text()
                for row in range(tableau.rowCount() - 1)
            ]
            amplitudes = stat.amplitudes_classes(mods_list)
            if amplitudes is not None:
                remplir_colone(tableau, textes.densite,
                               [round(float(v), 4) for v in stat.densites(eff, amplitudes)])
        except Exception as e:
            erreur(e)


def inserer_colone(tableau: QTableWidget, nom_colone):
    """
    On donne l'entête du tableau

    :param nom_colone: nom de la colonne
    :param tableau:
    :return:
    """
    initialiser_entete_par_defaut(tableau)
    if colonne_existe(tableau, nom_colone):
        return

    indice = entete_et_index[nom_colone]
    position = sum(
        1 for entete in liste_entete[:indice] if colonne_existe(tableau, entete))
    tableau.insertColumn(position)
    tableau.setHorizontalHeaderItem(position, QTableWidgetItem(nom_colone))
