# LandTistik

**LandTistik** est un logiciel de statistiques open-source conçu pour être simple, puissant et moderne. Idéal pour les étudiants en statistiques, mathématiques et sciences des données.

## Démonstration

#file:record.webm

Si l'aperçu ne s'affiche pas, ouvrez directement [record.webm](record.webm).

---

## 🚀 Fonctionnalités

### 📊 Tableau statistique complet
- Saisie des modalités (Xi) et des effectifs (Ni)
- Calcul automatique de toutes les colonnes :
  - **Xi × Ni** — produit modalité × effectif
  - **ECC / ECD** — effectifs cumulés croissants / décroissants
  - **Fi** — fréquences relatives
  - **FCC / FCD** — fréquences cumulées croissantes / décroissantes
  - **Centre (Ci)** — centre de classe (pour données continues)
  - **Amplitude (Ai)** — largeur de classe
  - **Densité (Di)** — densité de fréquence

### 📐 Paramètres statistiques
- Moyenne arithmétique et géométrique
- **Médiane, Mode**
- **Quartiles Q1, Q3** et écart interquartile
- **Variance** et **écart-type**
- Coefficient de variation
- Étendue, taux de variation

### 📈 Visualisations
- Diagramme en **bandes** (effectifs)
- **Camembert** (fréquences)
- **Ogive** (fréquences cumulées croissantes)
- **Polygone des fréquences**
- **Nuage de points**
- **Boîte à moustaches** (box plot)
- Export des graphiques en PNG, PDF, SVG

### 📁 Gestion des fichiers
- Format natif `.ltk` (JSON)
- **Import CSV** (séparateur `;` ou `,`)
- **Export CSV**
- Sauvegarde automatique avant nouveau fichier

### 🎨 Interface
- Thème **sombre** et **clair**
- Raccourcis clavier : `Ctrl+N`, `Ctrl+O`, `Ctrl+S`, `Ctrl+I` (import), `Ctrl+E` (export), `Ctrl+Entrée` (ajouter ligne), `Ctrl+T` (compléter tableau)
- Barre de statut informative
- Suppression de lignes

---

## 🔧 Installation

```bash
# Cloner le projet
git clone https://github.com/Starland9/LandTistik.git
cd LandTistik

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

### Dépendances principales
| Paquet | Rôle |
|--------|------|
| `PyQt6` | Interface graphique |
| `numpy` | Calculs numériques |
| `matplotlib` | Visualisations |
| `scipy` | Statistiques avancées |
| `pandas` | Manipulation de données |
| `pyqtdarktheme` | Thèmes sombre/clair |

---

## 🧪 Tests

```bash
# Lancer les tests unitaires
python -m pytest test/ -v
```

27 tests couvrant : ECC/ECD, fréquences, paramètres de position et de dispersion, intervalles, cas limites.

---

## 📚 Documentation

La documentation technique est disponible dans [**DOC.MD**](./DOC.MD).

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour commencer :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -m 'feat: ajouter ma fonctionnalité'`)
4. Pushez la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request
