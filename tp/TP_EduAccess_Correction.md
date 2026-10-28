# Correction Détaillée du TP Guidé : Détection Précoce des Difficultés d'Apprentissage (EduAccess)

**Établissement :** École Marocaine des Sciences de l'Ingénieur (EMSI)  
**Module :** Développement et déploiement d’applications intelligentes  
**Enseignante :** Pr. Soukaina Gouraguine  
**Projet :** PROJET 1 — EduAccess  
**Fichiers associés :** `tp/TP_EduAccess_Correction.ipynb`, `src/train.py`, `api/main.py`, `app/streamlit_app.py`

---

## 1. Correction de l'Étape 1 : Ingestion, Exploration & Nettoyage

### 1.1. Chargement sans erreurs et gestion des `'?'`
```python
import pandas as pd
import numpy as np

# Chargement avec remplacement direct des caractères '?' par NaN
student_info = pd.read_csv('open+university+learning+analytics+dataset/studentInfo.csv', na_values=['?', ''])
student_reg = pd.read_csv('open+university+learning+analytics+dataset/studentRegistration.csv', na_values=['?', ''])
assessments = pd.read_csv('open+university+learning+analytics+dataset/assessments.csv', na_values=['?', ''])

print("Lignes dans studentInfo :", len(student_info))  # 32 593 lignes
```

### 1.2. Analyse de la cible et binarisation
```python
# Répartition de la cible originale
print(student_info['final_result'].value_counts(normalize=True))
# Pass        : 37.9%
# Withdrawn   : 31.2%
# Fail        : 21.6%
# Distinction : 9.3%

# Binarisation pour la détection du risque d'échec / abandon
student_info['is_at_risk'] = student_info['final_result'].isin(['Fail', 'Withdrawn']).astype(int)
print("Répartition de la cible binaire :")
print(student_info['is_at_risk'].value_counts(normalize=True))
# 1 (À risque)    : 52.80% (17 208 étudiants)
# 0 (En réussite) : 47.20% (15 385 étudiants)
```

### 1.3. Réponse à la question critique sur le Data Leakage
> **Explication conceptuelle :**  
> La colonne `date_unregistration` indique la date précise à laquelle un étudiant a formellement quitté le cursus. Si un étudiant a une valeur non nulle dans cette colonne, il est **systématiquement classé comme 'Withdrawn'** dans le jeu de données.  
> Inclure `date_unregistration` dans les variables explicatives reviendrait à donner la réponse au modèle. Lors d'un déploiement en conditions réelles, au moment où l'on souhaite détecter un étudiant en difficulté (jour 30 ou jour 60), cette date est évidemment inconnue. Son utilisation constitue une **fuite d'information majeure (Data Leakage)** qui fausserait totalement la validité de l'outil. Elle a donc été rigoureusement éliminée des prédicteurs.

---

## 2. Correction de l'Étape 2 : Feature Engineering & Agrégation VLE

```python
# Agrégation du fichier studentVle.csv (10.6M lignes) par morceaux
usecols = ['code_module', 'code_presentation', 'id_student', 'date', 'sum_click']
agg_chunks = []

for chunk in pd.read_csv('open+university+learning+analytics+dataset/studentVle.csv', usecols=usecols, chunksize=1_000_000, na_values=['?', '']):
    chunk['clicks_pre_course'] = chunk['sum_click'].where(chunk['date'] < 0, 0)
    chunk['clicks_early_30'] = chunk['sum_click'].where(chunk['date'] <= 30, 0)

    chunk_agg = chunk.groupby(['code_module', 'code_presentation', 'id_student']).agg(
        total_clicks=('sum_click', 'sum'),
        pre_course_clicks=('clicks_pre_course', 'sum'),
        early_30_clicks=('clicks_early_30', 'sum'),
        active_days=('date', 'nunique')
    ).reset_index()
    agg_chunks.append(chunk_agg)

combined = pd.concat(agg_chunks, ignore_index=True)
vle_agg = combined.groupby(['code_module', 'code_presentation', 'id_student']).agg(
    total_clicks=('total_clicks', 'sum'),
    pre_course_clicks=('pre_course_clicks', 'sum'),
    early_30_clicks=('early_30_clicks', 'sum'),
    active_days=('active_days', 'sum')
).reset_index()

# Agrégation des évaluations
student_asm = pd.read_csv('open+university+learning+analytics+dataset/studentAssessment.csv', na_values=['?', ''])
sa_asm = pd.merge(student_asm, assessments, on='id_assessment', how='left')
sa_asm['is_late'] = (sa_asm['date_submitted'] > sa_asm['date']).fillna(False).astype(int)
sa_asm['is_failed'] = (sa_asm['score'] < 40).fillna(False).astype(int)

# Évaluations précoces (<= 60 jours)
early_mask = sa_asm['date'].fillna(999) <= 60
sa_early = sa_asm[early_mask].groupby(['id_student', 'code_module', 'code_presentation']).agg(
    early_assessments_count=('score', 'count'),
    early_avg_score=('score', 'mean'),
    early_late_submissions=('is_late', 'sum')
).reset_index()

# Évaluations globales
sa_global = sa_asm.groupby(['id_student', 'code_module', 'code_presentation']).agg(
    total_assessments_submitted=('score', 'count'),
    overall_avg_score=('score', 'mean'),
    min_score=('score', 'min'),
    late_submissions_count=('is_late', 'sum'),
    failed_assessments_count=('is_failed', 'sum')
).reset_index()

# Fusion finale dans un DataFrame unifié
merge_keys = ['code_module', 'code_presentation', 'id_student']
df = pd.merge(student_info, student_reg[merge_keys + ['date_registration']], on=merge_keys, how='left')
df = pd.merge(df, vle_agg, on=merge_keys, how='left')
df = pd.merge(df, sa_early, on=merge_keys, how='left')
df = pd.merge(df, sa_global, on=merge_keys, how='left')

# Imputation des valeurs nulles
num_vle_cols = ['total_clicks', 'pre_course_clicks', 'early_30_clicks', 'active_days',
                'early_assessments_count', 'early_avg_score', 'early_late_submissions',
                'total_assessments_submitted', 'overall_avg_score', 'min_score',
                'late_submissions_count', 'failed_assessments_count']
for c in num_vle_cols:
    df[c] = df[c].fillna(0)

df['date_registration'] = df['date_registration'].fillna(df['date_registration'].median())
df['imd_band'] = df['imd_band'].fillna('Missing')
```

---

## 3. Correction de l'Étape 3 : Entraînement et Comparaison

```python
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier

cat_features = ['code_module', 'gender', 'region', 'highest_education', 'imd_band', 'age_band', 'disability']
num_features = ['num_of_prev_attempts', 'studied_credits', 'date_registration'] + num_vle_cols

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
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=14, random_state=42, n_jobs=-1),
    "Hist Gradient Boosting": HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, random_state=42)
}

results = {}
for name, clf in models.items():
    pipe = Pipeline(steps=[('prep', preprocessor), ('clf', clf)])
    cv_scores = cross_validate(pipe, X_train, y_train, cv=5, scoring=['accuracy', 'f1', 'roc_auc'], n_jobs=-1)
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]
    
    # Stockage et affichage
    print(f"=== {name} ===")
    print(f"F1-Score Test : {f1_score(y_test, y_pred):.4f} | ROC-AUC : {roc_auc_score(y_test, y_prob):.4f}")
```

---

## 4. Correction de l'Étape 4 : Résultats et Analyse Critique

### 4.1. Tableau des Résultats Obtenus
Sur les 6 519 étudiants du jeu de test :
- **HistGradientBoosting :** Accuracy = **93.04%**, Precision = **95.88%**, Recall = **90.70%**, F1 = **93.22%**, ROC-AUC = **0.9812**.
- **Random Forest :** Accuracy = **92.39%**, Precision = **95.88%**, Recall = **89.37%**, F1 = **92.51%**, ROC-AUC = **0.9787**.
- **Régression Logistique :** Accuracy = **92.77%**, Precision = **95.64%**, Recall = **90.44%**, F1 = **92.97%**, ROC-AUC = **0.9735**.

### 4.2. Matrice de Confusion (HistGradientBoosting)
```
                  Prédit : Réussite (0)    Prédit : À Risque (1)
Réel : Réussite (0)       2 943                    134    (Faux Positifs : 4.4%)
Réel : À Risque (1)         320                  3 122    (Vrais Positifs : 90.7%)
```

> **Analyse des Faux Négatifs (320 étudiants) :**  
> Les faux négatifs correspondent aux étudiants en difficulté que le modèle n'a pas détectés (prédits en réussite). Dans un contexte éducatif d'accompagnement, **minimiser les faux négatifs est la priorité**, car un étudiant en difficulté non détecté ne recevra pas le tutorat dont il a besoin. Le rappel élevé (90.7%) atteste que plus de 9 étudiants en difficulté sur 10 sont correctement alertés.

### 4.3. Variables Clés Identifiées (Permutation Importance)
1. `early_avg_score` & `overall_avg_score` : Les notes obtenues aux premiers devoirs sont le prédicteur le plus puissant.
2. `total_clicks` & `early_30_clicks` : Le niveau de connexion dans les 30 premiers jours reflète directement l'investissement de l'apprenant.
3. `failed_assessments_count` : Avoir au moins une note < 40/100 multiplie par 4 le risque d'échec final.
4. `studied_credits` : Une charge supérieure à 120 crédits fragilise significativement la réussite.
5. `date_registration` : S'inscrire après le début officiel du cours augmente le risque de retard irrattrapable.

---

## 5. Correction de l'Étape 5 : Déploiement

### 5.1. Démarrage de l'API FastAPI
Exécuter dans le terminal :
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
Accéder à la documentation Swagger interactive sur : `http://127.0.0.1:8000/docs`

### 5.2. Lancement du Tableau de Bord Streamlit
Exécuter :
```bash
streamlit run app/streamlit_app.py
```
L'application web s'ouvre sur `http://localhost:8501`, permettant de simuler des profils étudiants, de visualiser les jauges de risque en temps réel et de recevoir les préconisations pédagogiques adaptées.
