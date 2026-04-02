"""
Module de calculs statistiques avancés pour LandTistik.
Fournit toutes les fonctions de calcul statistique utilisées par l'application.
"""

import numpy as np
from scipy import stats as scipy_stats


def _total(effectifs: np.ndarray) -> float:
    """Retourne le total des effectifs (N)."""
    return float(np.sum(effectifs))


def modalites_x_effectifs(modalites: np.ndarray, effectifs: np.ndarray) -> np.ndarray:
    """Calcule Xi * Ni pour chaque modalité numérique."""
    return modalites * effectifs


def effectifs_cumules_croissants(effectifs: np.ndarray) -> np.ndarray:
    """Calcule les effectifs cumulés croissants (ECC)."""
    return np.cumsum(effectifs)


def effectifs_cumules_decroissants(effectifs: np.ndarray) -> np.ndarray:
    """Calcule les effectifs cumulés décroissants (ECD)."""
    ecc = effectifs_cumules_croissants(effectifs)
    n = _total(effectifs)
    return n - ecc + effectifs


def frequences(effectifs: np.ndarray) -> np.ndarray:
    """Calcule les fréquences relatives Fi = Ni / N."""
    n = _total(effectifs)
    if n == 0:
        return np.zeros_like(effectifs, dtype=float)
    return effectifs / n


def frequences_cumulees_croissantes(effectifs: np.ndarray) -> np.ndarray:
    """Calcule les fréquences cumulées croissantes (FCC)."""
    fi = frequences(effectifs)
    return np.cumsum(fi)


def frequences_cumulees_decroissantes(effectifs: np.ndarray) -> np.ndarray:
    """Calcule les fréquences cumulées décroissantes (FCD)."""
    fcc = frequences_cumulees_croissantes(effectifs)
    fi = frequences(effectifs)
    return 1 - fcc + fi


def centres_classes(modalites_str: list) -> np.ndarray | None:
    """
    Calcule le centre de chaque classe à partir de chaînes d'intervalles.
    Accepte les formats : '0-5', '0..5', '[0;5[', '0;5'
    Retourne None si les modalités ne sont pas des intervalles.
    """
    centres = []
    for m in modalites_str:
        val = _parse_intervalle(str(m))
        if val is None:
            return None
        centres.append(val)
    return np.array(centres)


def amplitudes_classes(modalites_str: list) -> np.ndarray | None:
    """
    Calcule l'amplitude de chaque classe à partir de chaînes d'intervalles.
    Retourne None si les modalités ne sont pas des intervalles.
    """
    amplitudes = []
    for m in modalites_str:
        amp = _parse_amplitude(str(m))
        if amp is None:
            return None
        amplitudes.append(amp)
    return np.array(amplitudes)


def densites(effectifs: np.ndarray, amplitudes: np.ndarray) -> np.ndarray:
    """Calcule la densité : Di = Ni / Ai."""
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.where(amplitudes != 0, effectifs / amplitudes, 0)
    return result


def _parse_intervalle(texte: str) -> float | None:
    """Parse un intervalle et retourne son centre. Retourne None si non parseable."""
    import re
    texte = texte.strip().replace('[', '').replace(']', '').replace('(', '').replace(')', '')
    # Cherche deux nombres séparés par des séparateurs courants
    patterns = [
        r'^([-\d.]+)\s*[;,\-\.]{1,2}\s*([-\d.]+)$',
        r'^([-\d.]+)\s*\.\.\s*([-\d.]+)$',
    ]
    for pattern in patterns:
        match = re.match(pattern, texte)
        if match:
            try:
                a, b = float(match.group(1)), float(match.group(2))
                return (a + b) / 2.0
            except ValueError:
                pass
    return None


def _parse_amplitude(texte: str) -> float | None:
    """Parse un intervalle et retourne son amplitude. Retourne None si non parseable."""
    import re
    texte = texte.strip().replace('[', '').replace(']', '').replace('(', '').replace(')', '')
    patterns = [
        r'^([-\d.]+)\s*[;,\-\.]{1,2}\s*([-\d.]+)$',
        r'^([-\d.]+)\s*\.\.\s*([-\d.]+)$',
    ]
    for pattern in patterns:
        match = re.match(pattern, texte)
        if match:
            try:
                a, b = float(match.group(1)), float(match.group(2))
                return abs(b - a)
            except ValueError:
                pass
    return None


# ─── Paramètres de position ───────────────────────────────────────────────────

def moyenne_arithmetique(modalites: np.ndarray, effectifs: np.ndarray) -> float:
    """Calcule la moyenne arithmétique pondérée : x̄ = Σ(Xi*Ni) / N."""
    n = _total(effectifs)
    if n == 0:
        return 0.0
    return float(np.sum(modalites * effectifs) / n)


def moyenne_geometrique(modalites: np.ndarray, effectifs: np.ndarray) -> float:
    """Calcule la moyenne géométrique pondérée (définie uniquement pour des valeurs strictement positives)."""
    n = _total(effectifs)
    if n == 0:
        return 0.0
    if np.any(modalites <= 0):
        return 0.0
    try:
        log_sum = np.sum(effectifs * np.log(modalites))
        return float(np.exp(log_sum / n))
    except Exception:
        return 0.0


def mediane(modalites: np.ndarray, effectifs: np.ndarray) -> float:
    """Calcule la médiane à partir des données groupées."""
    expanded = np.repeat(modalites, effectifs.astype(int))
    if len(expanded) == 0:
        return 0.0
    return float(np.median(expanded))


def mode(modalites: np.ndarray, effectifs: np.ndarray) -> float:
    """Retourne la modalité la plus fréquente (mode)."""
    if len(effectifs) == 0:
        return 0.0
    idx = int(np.argmax(effectifs))
    return float(modalites[idx])


def quartile(modalites: np.ndarray, effectifs: np.ndarray, q: float) -> float:
    """Calcule un quartile (q=0.25 → Q1, q=0.5 → médiane, q=0.75 → Q3)."""
    expanded = np.repeat(modalites, effectifs.astype(int))
    if len(expanded) == 0:
        return 0.0
    return float(np.percentile(expanded, q * 100))


def ecart_interquartile(modalites: np.ndarray, effectifs: np.ndarray) -> float:
    """Calcule l'écart interquartile (Q3 - Q1)."""
    return quartile(modalites, effectifs, 0.75) - quartile(modalites, effectifs, 0.25)


# ─── Paramètres de dispersion ────────────────────────────────────────────────

def variance(modalites: np.ndarray, effectifs: np.ndarray) -> float:
    """Calcule la variance pondérée."""
    n = _total(effectifs)
    if n == 0:
        return 0.0
    mean = moyenne_arithmetique(modalites, effectifs)
    return float(np.sum(effectifs * (modalites - mean) ** 2) / n)


def ecart_type(modalites: np.ndarray, effectifs: np.ndarray) -> float:
    """Calcule l'écart-type."""
    return float(np.sqrt(variance(modalites, effectifs)))


def coefficient_variation(modalites: np.ndarray, effectifs: np.ndarray) -> float:
    """Calcule le coefficient de variation (CV = σ/x̄ × 100)."""
    mean = moyenne_arithmetique(modalites, effectifs)
    if mean == 0:
        return 0.0
    return float(ecart_type(modalites, effectifs) / abs(mean) * 100)


def etendue(modalites: np.ndarray) -> float:
    """Calcule l'étendue (max - min)."""
    if len(modalites) == 0:
        return 0.0
    return float(np.max(modalites) - np.min(modalites))


def taux_de_variation(modalites: np.ndarray) -> float:
    """Calcule le taux de variation entre le dernier et le premier élément."""
    if len(modalites) < 2 or modalites[0] == 0:
        return 0.0
    return float((modalites[-1] - modalites[0]) / modalites[0] * 100)


def resume_statistique(modalites: np.ndarray, effectifs: np.ndarray) -> dict:
    """
    Retourne un dictionnaire complet avec tous les paramètres statistiques.
    """
    return {
        "N (Total)": int(_total(effectifs)),
        "Moyenne arithmétique": round(moyenne_arithmetique(modalites, effectifs), 4),
        "Moyenne géométrique": round(moyenne_geometrique(modalites, effectifs), 4),
        "Médiane": round(mediane(modalites, effectifs), 4),
        "Mode": round(mode(modalites, effectifs), 4),
        "Q1 (1er quartile)": round(quartile(modalites, effectifs, 0.25), 4),
        "Q3 (3e quartile)": round(quartile(modalites, effectifs, 0.75), 4),
        "Écart interquartile": round(ecart_interquartile(modalites, effectifs), 4),
        "Variance": round(variance(modalites, effectifs), 4),
        "Écart-type": round(ecart_type(modalites, effectifs), 4),
        "Coeff. de variation (%)": round(coefficient_variation(modalites, effectifs), 4),
        "Étendue": round(etendue(modalites), 4),
    }
