# 🎓 EduAccess : Détection Précoce des Difficultés d'Apprentissage

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20v0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit%20v1.32+-FF4B4B.svg)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org)
[![Pytest Tests](https://img.shields.io/badge/Tests-13%20Passed-brightgreen.svg)](https://docs.pytest.org)
[![License](https://img.shields.io/badge/License-Academic%20EMSI-lightgrey.svg)]()

> **Module :** Développement et déploiement d’applications intelligentes  
> **Établissement :** École Marocaine des Sciences de l'Ingénieur (EMSI)  
> **Enseignante :** Pr. Soukaina Gouraguine  
> **Projet :** PROJET 1 — EduAccess  

---

## 📌 1. Contexte & Objectifs du Projet

Le projet **EduAccess** consiste à concevoir, développer et déployer une **application intelligente d'aide à la décision** capable d'exploiter les traces d'apprentissage numériques issues de l'**Open University Learning Analytics Dataset (OULAD)** afin de repérer au plus tôt (dès les 30 à 60 premiers jours) les étudiants présentant des signes de difficultés académiques ou de risque d'abandon.

### ⚖️ Principe d'Aide à la Décision & Bienveillance
> L'application constitue un **outil d'aide à l'analyse et à l'accompagnement pédagogique**, et **en aucun cas un système de décision ou d'exclusion automatique**. Les alertes levées par l'intelligence artificielle permettent de proposer des mesures proactives (tutorat individualisé, aménagement de calendrier, remédiation méthodologique) avant qu'il ne soit trop tard.

---

## 🏗️ 2. Architecture Globale du Projet

```
c:\Users\dell\Desktop\projet/
├── open+university+learning+analytics+dataset/ # Données brutes OULAD (7 fichiers CSV)
│   ├── studentInfo.csv
│   ├── studentRegistration.csv
│   ├── studentAssessment.csv
│   ├── assessments.csv
│   ├── studentVle.csv (453 Mo, 10.6M lignes)
│   ├── vle.csv
│   └── courses.csv
├── data/                                 # Données traitées et métadonnées
│   ├── processed_students.csv            # Dataset unifié (32 593 lignes, 26 colonnes)
│   └── feature_metadata.json             # Schémas et distributions
├── models/                               # Modèles sérialisés et métriques
│   ├── best_model.joblib                 # Modèle optimal retenu (HistGradientBoosting)
│   ├── model_gradient_boosting.joblib
│   ├── model_random_forest.joblib
│   ├── model_logistic_regression.joblib
│   └── metrics.json                      # Scores comparatifs et feature importance
├── src/                                  # Code source modulaire Python
│   ├── __init__.py
│   ├── config.py                         # Chemins, colonnes et constantes
│   ├── data_loader.py                    # ETL par chunks et consolidation
│   ├── feature_engineering.py            # Encodage, standardisation & recommandations
│   ├── train.py                          # Entraînement multi-modèles & validation croisée
│   └── evaluate.py                       # Évaluation, ROC et seuils de décision
├── api/                                  # API REST FastAPI
│   ├── __init__.py
│   ├── schemas.py                        # Modèles Pydantic v2
│   └── main.py                           # Endpoints (/health, /predict, /predict_batch, /docs)
├── app/                                  # Frontend Web Streamlit
│   └── streamlit_app.py                  # Dashboard interactif à 5 vues
├── tp/                                   # Matériel pédagogique de TP
│   ├── TP_EduAccess_Enonce.md            # Énoncé détaillé du TP
│   ├── TP_EduAccess_Enonce.ipynb         # Notebook Jupyter de l'énoncé
│   ├── TP_EduAccess_Correction.md        # Corrigé complet et explications
│   ├── TP_EduAccess_Correction.ipynb     # Notebook Jupyter du corrigé
│   └── generate_notebooks.py             # Script de génération des notebooks
├── docs/                                 # Documentation & Présentation
│   ├── SUPPORT_PEDAGOGIQUE.md            # Support de cours complet
│   ├── presentation.html                 # Diaporama interactif pour la soutenance
│   └── ARCHITECTURE.md                   # Description architecturale détaillée
├── tests/                                # Suite de tests automatisés (Pytest)
│   ├── __init__.py
│   ├── test_data.py                      # Tests d'intégrité des données
│   ├── test_models.py                    # Tests d'inférence et probabilités
│   └── test_api.py                       # Tests des endpoints FastAPI
├── Dockerfile                            # Image conteneurisée de l'application
├── docker-compose.yml                    # Orchestration API + Streamlit
├── requirements.txt                      # Dépendances Python du projet
├── run_project.py                        # Interface CLI universelle
└── README.md                             # Documentation principale
```

---

## 🚀 3. Installation et Démarrage Rapide

### 3.1. Prérequis
- Python 3.10, 3.11 ou 3.13 installé.
- Git (optionnel).

### 3.2. Installation des Dépendances
Dans un terminal PowerShell ou Bash à la racine du projet :
```bash
pip install -r requirements.txt
```

### 3.3. Utilisation du Script CLI Universel (`run_project.py`)

| Commande | Action Réalisée |
| :--- | :--- |
| `python run_project.py prepare` | Exécute l'ETL par chunks et génère `data/processed_students.csv` |
| `python run_project.py train` | Entraîne et compare les 3 modèles ML (CV 5-folds) |
| `python run_project.py test` | Lance la suite de 13 tests automatisés avec Pytest |
| `python run_project.py api` | Démarre le serveur FastAPI sur `http://127.0.0.1:8000` |
| `python run_project.py app` | Lance l'application Streamlit sur `http://localhost:8501` |
| `python run_project.py full` | Enchaîne ETL $\rightarrow$ Entraînement $\rightarrow$ Tests Pytest |

---

## 🤖 4. Modèles de Machine Learning & Performances

Trois familles de modèles ont été comparées sous validation croisée stratifiée à 5 plis :

| Modèle | Accuracy | Précision (Risque) | Rappel (Risque) | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Régression Logistique** | 92.77% | 95.64% | 90.44% | 92.97% | 0.9735 |
| **Random Forest** | 92.39% | 95.88% | 89.37% | 92.51% | 0.9787 |
| 🏆 **HistGradientBoosting** | **93.04%** | **95.88%** | **90.70%** | **93.22%** | **0.9812** |

### 🔍 Facteurs Déterminants Détectés (Permutation Importance)
1. **Notes aux évaluations précoces (`early_avg_score`)** : Premier signal de compréhension.
2. **Engagement VLE dans les 30 premiers jours (`early_30_clicks`)** : Indicateur direct d'assiduité.
3. **Nombre d'évaluations échouées (`failed_assessments_count`)** : Note < 40/100 alertant un décrochage.
4. **Retard de soumission (`late_submissions_count`)** : Symptôme de difficulté d'organisation temporelle.
5. **Charge d'étude (`studied_credits`)** : Risque accru au-delà de 120 crédits simultanés.

---

## 📡 5. Documentation de l'API REST FastAPI

L'API est documentée interactivement via **Swagger UI** :
- **URL locale :** `http://127.0.0.1:8000/docs`
- **Documentation ReDoc :** `http://127.0.0.1:8000/redoc`

### Endpoints Clés :
- `GET /health` : Vérification du statut du service et chargement du modèle.
- `GET /metrics` : Métriques comparatives complètes et matrices de confusion.
- `GET /sample_profiles` : Exemples prêts à l'emploi (profils à faible, moyen et fort risque).
- `POST /predict` : Prédiction temps réel pour un profil étudiant avec probabilité, jauge et plan d'accompagnement.
- `POST /predict_batch` : Diagnostic d'une liste d'étudiants en un seul appel.
- `POST /predict_csv` : Import d'un fichier CSV de cohorte avec enrichissement des colonnes de risque.

#### Exemple d'appel avec cURL :
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "code_module": "BBB",
       "gender": "F",
       "region": "London Region",
       "highest_education": "HE Qualification",
       "imd_band": "60-70%",
       "age_band": "0-35",
       "disability": "N",
       "num_of_prev_attempts": 0,
       "studied_credits": 60,
       "date_registration": -30.0,
       "pre_course_clicks": 60.0,
       "early_30_clicks": 350.0,
       "total_clicks": 1200.0,
       "active_days": 35.0,
       "early_assessments_count": 2.0,
       "early_avg_score": 75.0,
       "early_late_submissions": 0.0,
       "total_assessments_submitted": 4.0,
       "overall_avg_score": 78.0,
       "min_score": 70.0,
       "late_submissions_count": 0.0,
       "failed_assessments_count": 0.0
     }'
```

---

## 🖥️ 6. Interface Utilisateur Streamlit

Lancez l'interface avec :
```bash
streamlit run app/streamlit_app.py
```
Accédez au tableau de bord sur `http://localhost:8501`. L'application offre 4 vues d'analyse :
1. **Vue d'ensemble et Analyse OULAD** : Indicateurs clés, graphiques Plotly de distribution de la réussite et d'engagement VLE.
2. **Modèles et Performances** : Tableaux comparatifs, matrices de confusion et courbes d'importance des variables.
3. **Simulateur de Risque Précoce** : Formulaire interactif en 3 volets avec jauge Plotly, diagnostic et recommandations pédagogiques ciblées.
4. **Analyse par Cohorte** : Exploration des étudiants OULAD avec filtres et import de fichier CSV externe.

---

## 🧪 7. Tests Automatisés (Pytest)

La suite de tests vérifie l'intégralité du cycle de vie de l'application :
```bash
pytest -v
```
**Résultat obtenu :**
```text
tests/test_api.py::test_api_root PASSED [ 7%]
tests/test_api.py::test_api_health PASSED [ 15%]
tests/test_api.py::test_api_metrics PASSED [ 23%]
tests/test_api.py::test_api_sample_profiles PASSED [ 30%]
tests/test_api.py::test_api_predict_single_profile PASSED [ 38%]
tests/test_api.py::test_api_predict_batch PASSED [ 46%]
tests/test_data.py::test_processed_dataset_exists_and_loads PASSED [ 53%]
tests/test_data.py::test_required_features_present PASSED [ 61%]
tests/test_data.py::test_target_values_and_no_nulls_in_critical_features PASSED [ 69%]
tests/test_models.py::test_model_artifact_exists PASSED [ 76%]
tests/test_models.py::test_model_prediction_shape_and_probability_bounds PASSED [ 84%]
tests/test_models.py::test_risk_level_categories PASSED [ 92%]
tests/test_models.py::test_recommendation_generation PASSED [100%]
============================= 13 passed in 4.38s ==============================
```

---

## 🐳 8. Déploiement Conteneurisé avec Docker

Le projet inclut un `Dockerfile` optimisé et un fichier `docker-compose.yml` orchestrant l'API et Streamlit :
```bash
# Construction et lancement des services
docker-compose up --build
```
- API REST : accessible sur `http://localhost:8000` (docs sur `http://localhost:8000/docs`)
- Frontend Streamlit : accessible sur `http://localhost:8501`

---

## 📋 9. Livrables du Cahier des Charges

| N° | Livrable Attendu | Emplacement dans le Projet | Description |
| :---: | :--- | :--- | :--- |
| **1** | **Support pédagogique** | [`docs/SUPPORT_PEDAGOGIQUE.md`](file:///c:/Users/dell/Desktop/projet/docs/SUPPORT_PEDAGOGIQUE.md) & [`docs/presentation.html`](file:///c:/Users/dell/Desktop/projet/docs/presentation.html) | Cours exhaustif + diaporama interactif de 12 slides pour soutenance orale. |
| **2** | **Code source** | [`src/`](file:///c:/Users/dell/Desktop/projet/src), [`api/`](file:///c:/Users/dell/Desktop/projet/api), [`app/`](file:///c:/Users/dell/Desktop/projet/app) | Code Python complet, modulaire, testé et documenté. |
| **3** | **TP guidé** | [`tp/TP_EduAccess_Enonce.md`](file:///c:/Users/dell/Desktop/projet/tp/TP_EduAccess_Enonce.md) & [`tp/TP_EduAccess_Enonce.ipynb`](file:///c:/Users/dell/Desktop/projet/tp/TP_EduAccess_Enonce.ipynb) | Énoncé détaillé avec objectifs, prérequis et manipulations. |
| **4** | **Correction du TP** | [`tp/TP_EduAccess_Correction.md`](file:///c:/Users/dell/Desktop/projet/tp/TP_EduAccess_Correction.md) & [`tp/TP_EduAccess_Correction.ipynb`](file:///c:/Users/dell/Desktop/projet/tp/TP_EduAccess_Correction.ipynb) | Solution exécutable pas-à-pas avec interprétation des résultats. |
