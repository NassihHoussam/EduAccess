# Architecture Technique du Projet EduAccess

## 1. Vue d'Ensemble du Système

Le projet **EduAccess** est conçu selon une architecture modulaire en couches, garantissant une séparation nette des responsabilités, la reproductibilité des expérimentations de Machine Learning, et la facilité de maintenance et de déploiement.

```mermaid
flowchart TD
    subgraph DataLayer["1. Couche Données (OULAD)"]
        D1[studentInfo.csv]
        D2[studentRegistration.csv]
        D3[studentAssessment.csv]
        D4[assessments.csv]
        D5[studentVle.csv - 10.6M lignes]
    end

    subgraph ProcessingLayer["2. Pipeline ETL & Feature Engineering"]
        P1[Chunked Aggregator VLE]
        P2[Assessment Feature Extractor]
        P3[Unified Dataset Builder]
        P4[ColumnTransformer: StandardScaler + OneHot]
    end

    subgraph MLLayer["3. Machine Learning & Model Registry"]
        M1[Logistic Regression]
        M2[Random Forest]
        M3[HistGradientBoosting]
        M4[Evaluation & Permutation Importance]
        M5[(best_model.joblib & metrics.json)]
    end

    subgraph ServiceLayer["4. Couche Service & Inférence (FastAPI)"]
        A1[GET /health & /metrics]
        A2[POST /predict]
        A3[POST /predict_batch & /predict_csv]
        A4[Swagger UI /docs]
    end

    subgraph UILayer["5. Interface Utilisateur (Streamlit)"]
        U1[Dashboard EDA & KPIs]
        U2[Comparateur de Modèles]
        U3[Simulateur Interactif de Risque]
        U4[Module d'Accompagnement Pédagogique]
        U5[Analyse de Cohorte CSV]
    end

    DataLayer --> ProcessingLayer
    ProcessingLayer --> MLLayer
    MLLayer --> ServiceLayer
    ServiceLayer -.-> UILayer
    MLLayer --> UILayer
```

---

## 2. Description des Couches

### 2.1. Couche Données (ETL & Aggregation)
- **Source** : Dataset OULAD (Open University Learning Analytics Dataset).
- **Problématique volume** : `studentVle.csv` contient plus de 10,6 millions d'interactions individuelles (453 Mo).
- **Solution technique** : Traitement par morceaux (*chunking* avec taille de lot de 1 000 000 lignes) avec `pandas`, extrayant spécifiquement les clics pré-cours (`date < 0`), les clics précoces (`date <= 30`), et les jours de connexion distincts.
- **Résultat** : Génération d'un fichier intermédiaire consolidé `data/processed_students.csv` (32 593 lignes, 26 colonnes), réduisant le temps de chargement de 15 secondes à 0.1 seconde.

### 2.2. Couche Feature Engineering
- **Catégorielles** : `code_module`, `gender`, `region`, `highest_education`, `imd_band`, `age_band`, `disability`. Encodées via `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`.
- **Numériques** : 15 indicateurs d'engagement et de réussite (clics VLE, notes d'évaluations, retards de soumission, charge de crédits, date d'inscription). Normalisées via `StandardScaler()`.
- **Prévention du Data Leakage** : Exclusion stricte de `date_unregistration` (qui constitue l'effet de l'abandon plutôt qu'une cause prédictive).

### 2.3. Couche Modélisation & Évaluation
Trois familles d'algorithmes ont été comparées sous validation croisée stratifiée 5-folds :
1. **Régression Logistique** : Modèle linéaire de référence (baseline rapide et interprétable).
2. **Random Forest** : Modèle ensembliste par bagging non linéaire.
3. **HistGradientBoosting** : Modèle ensembliste par boosting d'arbres, état de l'art sur données tabulaires.

```mermaid
graph LR
    TrainSet[Train Set: 80% - 26 074 profils] --> CV[5-Fold Stratified CV]
    CV --> LR[Logistic Regression: F1=92.77%]
    CV --> RF[Random Forest: F1=92.51%]
    CV --> GB[HistGradientBoosting: F1=93.22%]
    GB --> Best[Modèle Retenu: Gradient Boosting]
    Best --> Export[models/best_model.joblib]
```

### 2.4. Couche Exposition API (FastAPI)
- **Protocole** : REST HTTP avec validation Pydantic v2.
- **Documentation interactive** : Swagger UI sur `/docs` et Redoc sur `/redoc`.
- **Gestion du cycle de vie** : Chargement singleton du modèle via le gestionnaire de contexte `lifespan`.
- **Fonctionnalités clés** :
  - Inférence unitaire en temps réel (`POST /predict`).
  - Inférence en lot pour plusieurs étudiants (`POST /predict_batch`).
  - Scoring de cohortes entières par import de fichier (`POST /predict_csv`).
  - Monitoring des performances et de l'état du système (`GET /health`, `GET /metrics`).

### 2.5. Couche Interface Utilisateur (Streamlit)
- Tableau de bord réactif en Python pur.
- Composants graphiques interactifs propulsés par **Plotly**.
- Simulateur de détection précoce intégrant une jauge de risque dynamique et un moteur de règles générant des **recommandations d'accompagnement pédagogique individualisées**.

---

## 3. Matrice de Traçabilité des Données

| Entité | Table Source OULAD | Variable Générée | Rôle Pédagogique |
| :--- | :--- | :--- | :--- |
| **Profil Personnel** | `studentInfo.csv` | `age_band`, `highest_education`, `disability` | Identifier les profils nécessitant des aménagements spécifiques. |
| **Inscription** | `studentRegistration.csv` | `date_registration` | Détecter les inscriptions tardives à risque de décrochage. |
| **Engagement Numérique** | `studentVle.csv` | `pre_course_clicks`, `early_30_clicks` | Signal faible d'isolement ou de désengagement précoce. |
| **Régularité Éducative** | `studentAssessment.csv` | `early_avg_score`, `early_late_submissions` | Détection des blocages méthodologiques et lacunes initiales. |
| **Cible d'Alerte** | `studentInfo.csv` | `is_at_risk` (1 = Fail/Withdrawn, 0 = Pass/Distinction) | Déclenchement de l'intervention tutorale bienveillante. |
