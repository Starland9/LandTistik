# Features & Roadmap

Liste des fonctionnalités implémentées, en cours et prévues.

## ✅ Implémentées (v2.0)

### Améliorations Générales
- [x] **Refactoring du code :** Modernisation de la base de code (Python 3.12+, imports corrigés, packages __init__.py).
- [x] **Tests unitaires :** 27 tests couvrant tous les calculs statistiques.
- [x] **Gestion des dépendances :** requirements.txt propre et à jour.
- [x] **Modules organisés :** Structure claire avec `models/`, `eui/`, `cui/`.

### Interface Utilisateur (UI/UX)
- [x] **Thèmes :** Implémentation complète des thèmes clair/sombre via pyqtdarktheme.
- [x] **Raccourcis clavier :** Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+I, Ctrl+E, Ctrl+Entrée, Ctrl+T.
- [x] **Barre de statut :** Messages contextuels dans la barre de statut.
- [x] **Suppression de lignes :** Bouton dédié et raccourci clavier.
- [x] **Panneau de paramètres enrichi :** Médiane, mode, quartiles, variance, écart-type...
- [x] **Résumé statistique :** Boîte de dialogue avec tous les paramètres.

### Fonctionnalités Statistiques
- [x] **ECC/ECD :** Effectifs cumulés croissants et décroissants calculés automatiquement.
- [x] **Fréquences/FCC/FCD :** Fréquences relatives et cumulées calculées automatiquement.
- [x] **Centre de classe :** Détection et calcul automatique pour données continues.
- [x] **Amplitude :** Calcul automatique à partir des intervalles.
- [x] **Densité :** Calcul automatique (Ni/Ai).
- [x] **Nouveaux types de diagrammes :** Camembert, ogive, polygone des fréquences, nuage de points, boîte à moustaches.
- [x] **Import/Export CSV :** Import depuis CSV (`;` ou `,`), export vers CSV.
- [x] **Export de graphiques :** PNG, PDF, SVG.
- [x] **Analyses statistiques complètes :** Médiane, mode, quartiles, variance, écart-type, CV, étendue.

### Documentation
- [x] **README.md mis à jour** avec toutes les fonctionnalités et instructions.

---

## 🔄 En cours / Prévues (v3.0)

### Fonctionnalités Statistiques Avancées
- [ ] **Régression linéaire :** Droite de régression avec coefficient de corrélation.
- [ ] **Tests statistiques :** Test de Chi², test t de Student.
- [ ] **Intervalles de confiance :** Calcul automatique.
- [ ] **Histogramme normalisé :** Avec courbe de densité normale superposée.

### Interface
- [ ] **Export vers Excel (.xlsx) :** Via openpyxl.
- [ ] **Copier/Coller :** Copie de cellules depuis/vers le presse-papiers.
- [ ] **Annuler/Rétablir :** Historique des actions.
- [ ] **Zoom sur les graphiques :** Interaction avec les diagrammes.

### Documentation
- [ ] **Rédiger la documentation technique** dans `DOC.MD`.
- [ ] **Créer des guides utilisateurs** avec exemples pas à pas.
- [ ] **Tutoriels vidéo.**

