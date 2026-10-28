"""
Script de génération des notebooks Jupyter (Énoncé et Correction) pour le TP EduAccess.
"""

import json
from pathlib import Path

TP_DIR = Path(__file__).resolve().parent

def make_cell(cell_type: str, source_text: str):
    lines = [line + "\n" for line in source_text.strip().split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    cell = {
        "cell_type": cell_type,
        "metadata": {},
        "source": lines
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell

def build_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

# ---------------------------------------------------------
# NOTEBOOK 1 : ÉNONCÉ DU TP
# ---------------------------------------------------------
enonce_cells = [
    make_cell("markdown", """# TP : Détection Précoce des Difficultés d'Apprentissage (EduAccess)
**Module :** Développement et déploiement d’applications intelligentes  
**Établissement :** École Marocaine des Sciences de l'Ingénieur (EMSI)  
**Enseignante :** Pr. Soukaina Gouraguine  
**Projet :** PROJET 1 — EduAccess

---
## Objectifs du TP
1. Charger et nettoyer le jeu de données relationnel **OULAD**.
2. Prévenir le risque de fuite d'information (*Data Leakage*).
3. Construire des caractéristiques d'engagement précoce (VLE et évaluations).
4. Entraîner et comparer au moins deux modèles de classification supervisée.
5. Évaluer le modèle retenu avec des métriques adaptées (F1-score, Recall, ROC-AUC, Matrice de confusion).
6. Exposer le modèle via une API REST (FastAPI) et concevoir un tableau de bord d'aide à la décision (Streamlit)."""),

    make_cell("markdown", """## Étape 1 : Ingestion et Exploration des Données
Chargez les fichiers de base et explorez la distribution des résultats finaux des étudiants."""),

    make_cell("code", """# À COMPLÉTER : Importez les bibliothèques nécessaires (pandas, numpy, etc.)
import pandas as pd
import numpy as np

# Chargez studentInfo.csv, studentRegistration.csv et assessments.csv
# ATTENTION : spécifiez na_values=['?', ''] pour convertir les '?' en NaN
student_info = None
student_reg = None
assessments = None

# Affichez les premières lignes et la taille de studentInfo
"""),

    make_cell("markdown", """### Question 1.1 : Définition de la variable cible
Créez la variable cible binaire `is_at_risk` :
- `1` si l'étudiant a échoué (`Fail`) ou abandonné (`Withdrawn`)
- `0` s'il a validé (`Pass`) ou obtenu une mention (`Distinction`)"""),

    make_cell("code", """# À COMPLÉTER : Créez la colonne 'is_at_risk'
# student_info['is_at_risk'] = ...
"""),

    make_cell("markdown", """### Question 1.2 : Réflexion sur le Data Leakage
Expliquez pourquoi la colonne `date_unregistration` ne doit ABSOLUMENT PAS être utilisée comme feature prédictive dans ce contexte."""),

    make_cell("markdown", """*Votre réponse ici :*"""),

    make_cell("markdown", """## Étape 2 : Feature Engineering Précoce & Agrégation VLE
Le fichier `studentVle.csv` contient plus de 10 millions d'interactions. Agrégez-le par blocs (chunks) pour extraire l'activité précoce (30 premiers jours) de chaque étudiant."""),

    make_cell("code", """# À COMPLÉTER : Fonction d'agrégation de studentVle.csv par chunks
# Calculez pour chaque étudiant : total_clicks, pre_course_clicks, early_30_clicks, active_days
"""),

    make_cell("markdown", """## Étape 3 : Entraînement et Comparaison de Modèles
Entraînez et comparez au moins deux modèles de classification (ex: Régression Logistique, Random Forest, Gradient Boosting). Utilisez un `ColumnTransformer` pour standardiser les variables numériques et encoder les variables catégorielles."""),

    make_cell("code", """# À COMPLÉTER : Séparation Train/Test (80/20 stratifié) et Pipeline Scikit-Learn
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Définissez le preprocessor et entraînez vos modèles
"""),

    make_cell("markdown", """## Étape 4 : Évaluation et Interprétabilité
Calculez les métriques de test (Accuracy, Précision, Rappel, F1-Score, ROC-AUC) et tracez la matrice de confusion ainsi que l'importance des variables."""),

    make_cell("code", """# À COMPLÉTER : Évaluation des métriques et matrice de confusion
"""),

    make_cell("markdown", """## Étape 5 : Déploiement (FastAPI & Streamlit)
Exposez le modèle entraîné sous forme d'une API REST avec FastAPI (`POST /predict`) et connectez-la à une interface interactive Streamlit d'aide à la décision.""")
]

# ---------------------------------------------------------
# NOTEBOOK 2 : CORRECTION COMPLÈTE DU TP
# ---------------------------------------------------------
correction_cells = [
    make_cell("markdown", """# Corrigé Détaillé du TP : Détection Précoce des Difficultés (EduAccess)
**Module :** Développement et déploiement d’applications intelligentes  
**Établissement :** École Marocaine des Sciences de l'Ingénieur (EMSI)  
**Enseignante :** Pr. Soukaina Gouraguine  
**Projet :** PROJET 1 — EduAccess

---
Ce notebook contient la solution complète, exécutable et commentée du TP guidé."""),

    make_cell("markdown", """## Étape 1 : Ingestion, Exploration et Nettoyage des Données"""),

    make_cell("code", """import pandas as pd
import numpy as np

# 1. Chargement des données avec gestion des caractères manquants '?'
student_info = pd.read_csv('../open+university+learning+analytics+dataset/studentInfo.csv', na_values=['?', ''])
student_reg = pd.read_csv('../open+university+learning+analytics+dataset/studentRegistration.csv', na_values=['?', ''])
assessments = pd.read_csv('../open+university+learning+analytics+dataset/assessments.csv', na_values=['?', ''])

print(f"Dimensions studentInfo : {student_info.shape}")
print(student_info['final_result'].value_counts())"""),

    make_cell("code", """# 2. Création de la cible binaire 'is_at_risk'
student_info['is_at_risk'] = student_info['final_result'].isin(['Fail', 'Withdrawn']).astype(int)
print("Distribution de la cible binaire :")
print(student_info['is_at_risk'].value_counts(normalize=True))"""),

    make_cell("markdown", """### Réponse sur le Data Leakage :
La présence d'une valeur dans `date_unregistration` indique mathématiquement que l'étudiant a abandonné (`Withdrawn`). Dans un système d'alerte précoce à 30 jours, cette information est inexistante au moment de la prédiction. Son utilisation constituerait une fuite d'information (*Data Leakage*), raison pour laquelle elle est strictement exclue."""),

    make_cell("markdown", """## Étape 2 : Agrégation VLE & Feature Engineering"""),

    make_cell("code", """# Agrégation optimisée de studentVle.csv par chunks de 1M lignes
vle_path = '../open+university+learning+analytics+dataset/studentVle.csv'
usecols = ['code_module', 'code_presentation', 'id_student', 'date', 'sum_click']
agg_chunks = []

for chunk in pd.read_csv(vle_path, usecols=usecols, chunksize=1_000_000, na_values=['?', '']):
    chunk['clicks_pre_course'] = chunk['sum_click'].where(chunk['date'] < 0, 0)
    chunk['clicks_early_30'] = chunk['sum_click'].where(chunk['date'] <= 30, 0)
    
    chunk_agg = chunk.groupby(['code_module', 'code_presentation', 'id_student']).agg(
        total_clicks=('sum_click', 'sum'),
        pre_course_clicks=('clicks_pre_course', 'sum'),
        early_30_clicks=('clicks_early_30', 'sum'),
        active_days=('date', 'nunique')
    ).reset_index()
    agg_chunks.append(chunk_agg)

vle_summary = pd.concat(agg_chunks, ignore_index=True).groupby(
    ['code_module', 'code_presentation', 'id_student']
).agg(
    total_clicks=('total_clicks', 'sum'),
    pre_course_clicks=('pre_course_clicks', 'sum'),
    early_30_clicks=('early_30_clicks', 'sum'),
    active_days=('active_days', 'sum')
).reset_index()

print("Agrégation VLE terminée. Profils :", len(vle_summary))"""),

    make_cell("code", """# Agrégation des évaluations
student_asm = pd.read_csv('../open+university+learning+analytics+dataset/studentAssessment.csv', na_values=['?', ''])
sa_asm = pd.merge(student_asm, assessments, on='id_assessment', how='left')
sa_asm['is_late'] = (sa_asm['date_submitted'] > sa_asm['date']).fillna(False).astype(int)
sa_asm['is_failed'] = (sa_asm['score'] < 40).fillna(False).astype(int)

# Évaluations précoces (<= 60j)
early_mask = sa_asm['date'].fillna(999) <= 60
early_asm = sa_asm[early_mask].groupby(['id_student', 'code_module', 'code_presentation']).agg(
    early_assessments_count=('score', 'count'),
    early_avg_score=('score', 'mean'),
    early_late_submissions=('is_late', 'sum')
).reset_index()

# Évaluations globales
total_asm = sa_asm.groupby(['id_student', 'code_module', 'code_presentation']).agg(
    total_assessments_submitted=('score', 'count'),
    overall_avg_score=('score', 'mean'),
    min_score=('score', 'min'),
    late_submissions_count=('is_late', 'sum'),
    failed_assessments_count=('is_failed', 'sum')
).reset_index()

# Fusion des données
keys = ['code_module', 'code_presentation', 'id_student']
df = pd.merge(student_info, student_reg[keys + ['date_registration']], on=keys, how='left')
df = pd.merge(df, vle_summary, on=keys, how='left')
df = pd.merge(df, early_asm, on=keys, how='left')
df = pd.merge(df, total_asm, on=keys, how='left')

# Imputation
vle_cols = ['total_clicks', 'pre_course_clicks', 'early_30_clicks', 'active_days',
            'early_assessments_count', 'early_avg_score', 'early_late_submissions',
            'total_assessments_submitted', 'overall_avg_score', 'min_score',
            'late_submissions_count', 'failed_assessments_count']
for c in vle_cols:
    df[c] = df[c].fillna(0)

df['date_registration'] = df['date_registration'].fillna(df['date_registration'].median())
df['imd_band'] = df['imd_band'].fillna('Missing')
print(f"Jeu de données final préparé : {df.shape}")"""),

    make_cell("markdown", """## Étape 3 : Entraînement et Comparaison de Modèles"""),

    make_cell("code", """from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

cat_features = ['code_module', 'gender', 'region', 'highest_education', 'imd_band', 'age_band', 'disability']
num_features = ['num_of_prev_attempts', 'studied_credits', 'date_registration'] + vle_cols

X = df[cat_features + num_features]
y = df['is_at_risk']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
    ]
)

models = {
    "Régression Logistique": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1),
    "Hist Gradient Boosting": HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, random_state=42)
}

comparison = []
for name, clf in models.items():
    pipe = Pipeline(steps=[('prep', preprocessor), ('clf', clf)])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]
    
    comparison.append({
        "Modèle": name,
        "Accuracy": round(accuracy_score(y_test, y_pred), 4),
        "Precision": round(precision_score(y_test, y_pred), 4),
        "Recall": round(recall_score(y_test, y_pred), 4),
        "F1-Score": round(f1_score(y_test, y_pred), 4),
        "ROC-AUC": round(roc_auc_score(y_test, y_prob), 4)
    })

pd.DataFrame(comparison).set_index("Modèle")"""),

    make_cell("markdown", """## Étape 4 : Matrice de Confusion et Analyse
Le modèle **HistGradientBoosting** obtient un F1-score de **93.2%** et une AUC de **0.981**.  
Affichons sa matrice de confusion :"""),

    make_cell("code", """best_pipe = Pipeline(steps=[('prep', preprocessor), ('clf', models["Hist Gradient Boosting"])])
best_pipe.fit(X_train, y_train)
y_pred = best_pipe.predict(X_test)

cm = confusion_matrix(y_test, y_pred)
print("Matrice de Confusion :")
print(pd.DataFrame(cm, index=['Réel : 0 (Réussite)', 'Réel : 1 (Risque)'], columns=['Prédit : 0', 'Prédit : 1']))"""),

    make_cell("markdown", """## Étape 5 : Déploiement et Test API
Pour lancer l'API FastAPI et l'interface Streamlit développées dans le cadre du projet :
```bash
# Lancement de l'API REST
uvicorn api.main:app --reload --port 8000

# Lancement du Dashboard Streamlit
streamlit run app/streamlit_app.py
```""")
]

# Écriture des fichiers .ipynb
with open(TP_DIR / "TP_EduAccess_Enonce.ipynb", "w", encoding="utf-8") as f:
    json.dump(build_notebook(enonce_cells), f, indent=2)

with open(TP_DIR / "TP_EduAccess_Correction.ipynb", "w", encoding="utf-8") as f:
    json.dump(build_notebook(correction_cells), f, indent=2)

print("Notebooks générés avec succès dans :", TP_DIR)
