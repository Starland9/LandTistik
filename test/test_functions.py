"""
Tests unitaires pour LandTistik.
Couvre les calculs statistiques, la gestion du tableau et les I/O.
"""

import sys
import os
import unittest
import numpy as np

# Ajouter la racine du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Statistiques as stat


class TestEffectifsCumules(unittest.TestCase):
    """Tests des effectifs et fréquences cumulés."""

    def setUp(self):
        self.effectifs = np.array([10.0, 5.0, 15.0, 25.0, 3.0])
        self.modalites = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    def test_ecc(self):
        ecc = stat.effectifs_cumules_croissants(self.effectifs)
        np.testing.assert_array_equal(ecc, [10, 15, 30, 55, 58])

    def test_ecd(self):
        ecd = stat.effectifs_cumules_decroissants(self.effectifs)
        # Le dernier ECD doit valoir Ni (dernier effectif)
        self.assertEqual(ecd[-1], self.effectifs[-1])
        # Le premier ECD doit valoir N
        self.assertEqual(ecd[0], np.sum(self.effectifs))

    def test_frequences_somme_1(self):
        fi = stat.frequences(self.effectifs)
        self.assertAlmostEqual(float(np.sum(fi)), 1.0, places=10)

    def test_fcc_max_1(self):
        fcc = stat.frequences_cumulees_croissantes(self.effectifs)
        self.assertAlmostEqual(float(fcc[-1]), 1.0, places=10)

    def test_fcd_premier_1(self):
        fcd = stat.frequences_cumulees_decroissantes(self.effectifs)
        self.assertAlmostEqual(float(fcd[0]), 1.0, places=10)


class TestParametresPosition(unittest.TestCase):
    """Tests des paramètres de position."""

    def setUp(self):
        # Distribution simple : valeurs 1, 2, 3, 4, 5 avec effectifs égaux
        self.modalites = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.effectifs = np.array([2.0, 2.0, 2.0, 2.0, 2.0])

    def test_moyenne_arithmetique(self):
        moyenne = stat.moyenne_arithmetique(self.modalites, self.effectifs)
        self.assertAlmostEqual(moyenne, 3.0)

    def test_mediane(self):
        mediane = stat.mediane(self.modalites, self.effectifs)
        self.assertAlmostEqual(mediane, 3.0)

    def test_mode(self):
        # Avec effectifs égaux, le mode est la première valeur
        effectifs_inegaux = np.array([1.0, 1.0, 5.0, 1.0, 1.0])
        mode = stat.mode(self.modalites, effectifs_inegaux)
        self.assertEqual(mode, 3.0)

    def test_quartile_q1(self):
        q1 = stat.quartile(self.modalites, self.effectifs, 0.25)
        self.assertGreater(q1, 0)
        self.assertLess(q1, 3.0)

    def test_quartile_q3(self):
        q3 = stat.quartile(self.modalites, self.effectifs, 0.75)
        self.assertGreater(q3, 3.0)

    def test_iqr_positif(self):
        iqr = stat.ecart_interquartile(self.modalites, self.effectifs)
        self.assertGreater(iqr, 0)


class TestParametresDispersion(unittest.TestCase):
    """Tests des paramètres de dispersion."""

    def setUp(self):
        self.modalites = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.effectifs = np.array([2.0, 2.0, 2.0, 2.0, 2.0])

    def test_variance_positive(self):
        v = stat.variance(self.modalites, self.effectifs)
        self.assertGreater(v, 0)

    def test_ecart_type_egal_racine_variance(self):
        v = stat.variance(self.modalites, self.effectifs)
        s = stat.ecart_type(self.modalites, self.effectifs)
        self.assertAlmostEqual(s, np.sqrt(v))

    def test_etendue(self):
        e = stat.etendue(self.modalites)
        self.assertEqual(e, 4.0)

    def test_coefficient_variation_positif(self):
        cv = stat.coefficient_variation(self.modalites, self.effectifs)
        self.assertGreater(cv, 0)


class TestIntervalles(unittest.TestCase):
    """Tests du parsing des intervalles."""

    def test_centre_classes(self):
        mods = ["0-5", "5-10", "10-15"]
        centres = stat.centres_classes(mods)
        np.testing.assert_array_almost_equal(centres, [2.5, 7.5, 12.5])

    def test_amplitude_classes(self):
        mods = ["0-5", "5-10", "10-15"]
        amplitudes = stat.amplitudes_classes(mods)
        np.testing.assert_array_almost_equal(amplitudes, [5.0, 5.0, 5.0])

    def test_centre_classes_points(self):
        mods = ["0..2", "2..6", "6..10"]
        centres = stat.centres_classes(mods)
        np.testing.assert_array_almost_equal(centres, [1.0, 4.0, 8.0])

    def test_non_intervalle_retourne_none(self):
        mods = ["rouge", "vert", "bleu"]
        centres = stat.centres_classes(mods)
        self.assertIsNone(centres)

    def test_densite(self):
        effectifs = np.array([10.0, 20.0, 5.0])
        amplitudes = np.array([5.0, 5.0, 5.0])
        densites = stat.densites(effectifs, amplitudes)
        np.testing.assert_array_almost_equal(densites, [2.0, 4.0, 1.0])


class TestResumeStatistique(unittest.TestCase):
    """Test de la fonction de résumé global."""

    def test_resume_contient_tous_parametres(self):
        mods = np.array([1.0, 2.0, 3.0])
        effs = np.array([5.0, 10.0, 5.0])
        resume = stat.resume_statistique(mods, effs)
        expected_keys = [
            "N (Total)", "Moyenne arithmétique", "Moyenne géométrique",
            "Médiane", "Mode", "Q1 (1er quartile)", "Q3 (3e quartile)",
            "Écart interquartile", "Variance", "Écart-type",
            "Coeff. de variation (%)", "Étendue"
        ]
        for key in expected_keys:
            self.assertIn(key, resume, f"Clé manquante : {key}")

    def test_resume_total_correct(self):
        mods = np.array([1.0, 2.0, 3.0])
        effs = np.array([5.0, 10.0, 5.0])
        resume = stat.resume_statistique(mods, effs)
        self.assertEqual(resume["N (Total)"], 20)

    def test_resume_moyenne_correcte(self):
        mods = np.array([2.0, 4.0])
        effs = np.array([1.0, 1.0])
        resume = stat.resume_statistique(mods, effs)
        self.assertAlmostEqual(resume["Moyenne arithmétique"], 3.0)


class TestCasLimites(unittest.TestCase):
    """Tests des cas limites."""

    def test_effectifs_vides(self):
        mods = np.array([], dtype=float)
        effs = np.array([], dtype=float)
        self.assertEqual(stat.moyenne_arithmetique(mods, effs), 0.0)
        self.assertEqual(stat.mediane(mods, effs), 0.0)

    def test_effectifs_un_seul_element(self):
        mods = np.array([42.0])
        effs = np.array([5.0])
        self.assertEqual(stat.moyenne_arithmetique(mods, effs), 42.0)
        self.assertEqual(stat.mode(mods, effs), 42.0)

    def test_variance_distribution_constante(self):
        mods = np.array([5.0, 5.0, 5.0])
        effs = np.array([2.0, 3.0, 1.0])
        self.assertAlmostEqual(stat.variance(mods, effs), 0.0)
        self.assertAlmostEqual(stat.ecart_type(mods, effs), 0.0)

    def test_frequences_avec_zero_total(self):
        effs = np.array([0.0, 0.0, 0.0])
        fi = stat.frequences(effs)
        np.testing.assert_array_equal(fi, [0.0, 0.0, 0.0])


if __name__ == "__main__":
    unittest.main(verbosity=2)

