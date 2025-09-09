"""
Ici, nous avons un regroupement de tout ce qui a trait a l'entête du tableau
"""


class textes:
    """
    Les différents textes d'entête
    """
    modalite = "Modalités(Xi)"
    effectif = "effectifs(Ni)"
    ecc = "ECC"
    ecd = "ECD"
    frequence = "Fréquences(Fi)"
    fcc = "FCC"
    fcd = "FCD"
    modalite_x_effectif = "(Xi * Ni)"
    centre = "Centre(Ci)"
    amplitude = "Amplitude(Ai)"
    densite = "Densite(Di)"


liste_entete = (textes.modalite,
                textes.effectif,
                textes.modalite_x_effectif,
                textes.ecc,
                textes.ecd,
                textes.frequence,
                textes.fcc,
                textes.fcd,
                textes.centre,
                textes.amplitude,
                textes.densite,
                )

entete_et_index = {texte: indice for indice, texte in enumerate(liste_entete)}
