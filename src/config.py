"""
Configuration centralisée du projet EduAccess.
Définit les chemins de données, les colonnes caractéristiques et les hyperparamètres globaux.
"""

from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "open+university+learning+analytics+dataset"
PROCESSED_DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DOCS_DIR = BASE_DIR / "docs"

# Fichiers de données
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "processed_students.csv"
FEATURE_METADATA_PATH = PROCESSED_DATA_DIR / "feature_metadata.json"

# Modèles sauvegardés
BEST_MODEL_PATH = MODELS_DIR / "best_model.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

# Définition des variables explicatives
CATEGORICAL_FEATURES = [
    "code_module",
    "gender",
    "region",
    "highest_education",
    "imd_band",
    "age_band",
    "disability"
]

NUMERICAL_FEATURES = [
    "num_of_prev_attempts",
    "studied_credits",
    "date_registration",
    "pre_course_clicks",
    "early_30_clicks",
    "total_clicks",
    "active_days",
    "early_assessments_count",
    "early_avg_score",
    "early_late_submissions",
    "total_assessments_submitted",
    "overall_avg_score",
    "min_score",
    "late_submissions_count",
    "failed_assessments_count"
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

# Définition de la cible binaire
# 1 = Profil à risque (Fail ou Withdrawn)
# 0 = Profil en réussite (Pass ou Distinction)
TARGET_COLUMN = "is_at_risk"

# Seuils pour l'alerte précoce
RISK_THRESHOLD_LOW = 0.35
RISK_THRESHOLD_HIGH = 0.65
