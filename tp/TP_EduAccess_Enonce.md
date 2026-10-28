# Travaux Pratiques Guidés : Détection Précoce des Difficultés d'Apprentissage (EduAccess)

**Établissement :** École Marocaine des Sciences de l'Ingénieur (EMSI)  
**Module :** Développement et déploiement d’applications intelligentes  
**Enseignante :** Pr. Soukaina Gouraguine  
**Projet :** PROJET 1 — EduAccess  
**Fichiers associés :** `tp/TP_EduAccess_Enonce.ipynb`, `tp/TP_EduAccess_Correction.ipynb`

---

## 1. Objectifs Pédagogiques du TP

À l'issue de ce TP, les étudiants seront capables de :
1. **Manipuler et croiser des données éducatives massives** issues de l'Open University Learning Analytics Dataset (OULAD).
2. **Identifier et neutraliser les risques de fuite d'information (*Data Leakage*)** dans un contexte d'alerte précoce.
3. **Construire un pipeline de Feature Engineering** extrayant des signaux faibles d'engagement (interactions VLE, dynamiques d'évaluation).
4. **Entraîner, optimiser et comparer plusieurs modèles de Machine Learning supervisés** (Régression Logistique, Random Forest, Gradient Boosting).
5. **Évaluer de manière critique les modèles** à l'aide de métriques adaptées (F1-score, Recall, ROC-AUC, Matrice de confusion).
6. **Exposer le modèle retenu sous forme d'API REST (FastAPI)** et concevoir une **interface interactive d'aide à la décision (Streamlit)**.

---

## 2. Prérequis & Environnement de Travail

- **Langage :** Python 3.10 ou supérieur.
- **Bibliothèques requises :** `pandas`, `numpy`, `scikit-learn`, `fastapi`, `uvicorn`, `streamlit`, `plotly`, `pytest`, `joblib`.
- **Données :** Dossier `open+university+learning+analytics+dataset/` contenant les 7 fichiers CSV (`studentInfo.csv`, `studentRegistration.csv`, `studentAssessment.csv`, `assessments.csv`, `studentVle.csv`, etc.).

---

## 3. Déroulement du TP (5 Étapes Pas-à-Pas)

### Étape 1 : Ingestion, Exploration et Nettoyage des Données
#### Contexte & Manipulation :
Le jeu de données OULAD contient plusieurs millions de lignes d'interactions numériques et utilise des chaînes `'?'` pour représenter certaines valeurs manquantes.

#### Questions de manipulation :
1. Charger les fichiers `studentInfo.csv`, `studentRegistration.csv` et `assessments.csv` en remplaçant automatiquement les `'?'` par des valeurs `NaN`.
2. Analyser la distribution de la colonne cible `final_result`. Quelles sont les 4 modalités présentes ?
3. Créer la variable cible binaire `is_at_risk` :
   - `is_at_risk = 1` si `final_result` vaut `'Fail'` ou `'Withdrawn'`.
   - `is_at_risk = 0` si `final_result` vaut `'Pass'` ou `'Distinction'`.
4. **Question critique :** Pourquoi est-il strictement interdit d'utiliser la colonne `date_unregistration` pour prédire le risque d'échec ? Expliquer le concept de *Data Leakage*.

---

### Étape 2 : Feature Engineering Précoce & Agrégation VLE
#### Contexte & Manipulation :
Le fichier `studentVle.csv` pèse plus de 450 Mo et contient plus de 10 millions de lignes. Le charger d'un bloc en mémoire peut saturer la RAM.

#### Questions de manipulation :
1. Écrire une fonction utilisant `chunksize=1_000_000` pour lire `studentVle.csv` par morceaux et calculer par étudiant et par module :
   - `pre_course_clicks` : somme des clics lorsque `date < 0`.
   - `early_30_clicks` : somme des clics lorsque `date <= 30`.
   - `total_clicks` : somme totale des clics.
   - `active_days` : nombre de jours distincts d'interaction.
2. Croiser les évaluations (`studentAssessment.csv` et `assessments.csv`) pour calculer :
   - Le nombre de devoirs rendus tôt (`date <= 60`).
   - La note moyenne aux premiers devoirs (`early_avg_score`).
   - Le nombre de devoirs rendus en retard (`date_submitted > date`).
3. Fusionner toutes les tables pour obtenir un DataFrame unique consolidé de 32 593 lignes.

---

### Étape 3 : Entraînement et Comparaison de Modèles de Classification
#### Contexte & Manipulation :
Vous devez comparer au moins deux modèles de classification (ex: Régression Logistique, Random Forest, HistGradientBoosting).

#### Questions de manipulation :
1. Séparer les données en jeu d'entraînement (80%) et jeu de test (20%) de façon stratifiée (`random_state=42`).
2. Mettre en place un `ColumnTransformer` scikit-learn :
   - Normalisation standard (`StandardScaler`) pour les variables numériques.
   - Encodage One-Hot (`OneHotEncoder(handle_unknown='ignore')`) pour les variables catégorielles.
3. Entraîner et comparer au moins trois modèles :
   - Modèle 1 : Régression Logistique (`LogisticRegression(max_iter=1000)`).
   - Modèle 2 : Forêt Aléatoire (`RandomForestClassifier(n_estimators=100, max_depth=12)`).
   - Modèle 3 : Gradient Boosting (`HistGradientBoostingClassifier(max_iter=150)`).
4. Évaluer chaque modèle en validation croisée stratifiée 5-folds (`StratifiedKFold`).

---

### Étape 4 : Évaluation Approfondie et Interprétabilité
#### Questions de manipulation :
1. Calculer pour chaque modèle sur le jeu de test :
   - L'Accuracy, la Précision (sur la classe à risque), le Rappel, le F1-score et le score ROC-AUC.
2. Afficher la matrice de confusion du meilleur modèle. Expliquer ce que représentent concrètement les Faux Négatifs dans ce projet éducatif.
3. Calculer la `permutation_importance` pour identifier les 5 variables ayant le plus fort pouvoir prédictif.
4. Sauvegarder le modèle optimal dans un fichier `models/best_model.joblib`.

---

### Étape 5 : Déploiement : API FastAPI & Interface Streamlit
#### Questions de manipulation :
1. Créer une API REST avec FastAPI (`api/main.py`) exposant :
   - `GET /health` : vérification de l'état du modèle.
   - `POST /predict` : inférence unitaire prenant en entrée un profil étudiant (format JSON validé par Pydantic) et renvoyant la probabilité de risque, le statut et des recommandations.
2. Développer une application Streamlit (`app/streamlit_app.py`) intégrant :
   - Un tableau de bord d'analyse exploratoire avec graphiques interactifs (Plotly).
   - Un formulaire d'évaluation individuelle en direct avec jauge de risque.
   - Un panneau de recommandations pédagogiques ciblées (tutorat, soutien méthodologique, alerte bienveillante).

---

## 4. Résultats Attendus

À la fin du TP, vous devez obtenir :
1. Un pipeline propre et reproductible sans fuite d'information.
2. Un F1-Score supérieur à **90%** et une aire sous la courbe ROC supérieure à **0.95**.
3. Une API fonctionnelle documentée sur `http://127.0.0.1:8000/docs`.
4. Une interface utilisateur Streamlit intuitive et ergonomique.
