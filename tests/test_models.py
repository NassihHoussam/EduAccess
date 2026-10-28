"""
Tests unitaires pour les modèles de Machine Learning (src.train & src.evaluate).
"""

import pytest
import numpy as np
import pandas as pd
from src.config import BEST_MODEL_PATH, METRICS_PATH, ALL_FEATURES
from src.evaluate import load_best_model, load_metrics
from src.feature_engineering import evaluate_risk_level, generate_recommendations


def test_model_artifact_exists():
    """Vérifie que le modèle sérialisé et les métriques existent."""
    assert BEST_MODEL_PATH.exists(), "Le fichier best_model.joblib doit exister."
    assert METRICS_PATH.exists(), "Le fichier metrics.json doit exister."


def test_model_prediction_shape_and_probability_bounds():
    """Vérifie que le modèle peut prédire sur un DataFrame et renvoie des probabilités valides."""
    model = load_best_model()

    # Création d'un profil fictif
    dummy_input = pd.DataFrame([{
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
        "pre_course_clicks": 50.0,
        "early_30_clicks": 300.0,
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
    }])[ALL_FEATURES]

    pred = model.predict(dummy_input)
    proba = model.predict_proba(dummy_input)

    assert len(pred) == 1
    assert pred[0] in [0, 1]
    assert proba.shape == (1, 2)
    assert 0.0 <= proba[0, 1] <= 1.0


def test_risk_level_categories():
    """Vérifie la cohérence du calcul des niveaux de risque."""
    assert evaluate_risk_level(0.85) == "Élevé"
    assert evaluate_risk_level(0.50) == "Modéré"
    assert evaluate_risk_level(0.15) == "Faible"


def test_recommendation_generation():
    """Vérifie que le générateur de recommandations produit des actions pertinentes."""
    at_risk_profile = {
        "early_30_clicks": 20.0,
        "pre_course_clicks": 0.0,
        "early_assessments_count": 0.0,
        "early_avg_score": 0.0,
        "studied_credits": 140,
        "disability": "Y"
    }
    recs = generate_recommendations(at_risk_profile, risk_prob=0.88)
    assert len(recs) >= 3
    # Doit contenir des alertes d'accès VLE, évaluation manquante et handicap
    joined = " ".join(recs)
    assert "VLE" in joined
    assert "évaluation" in joined or "évaluation(s)" in joined or "échéance" in joined
    assert "handicap" in joined or "accessibilité" in joined
