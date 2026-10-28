"""
Tests d'intégration pour l'API REST FastAPI (api.main).
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_api_root():
    """Vérifie le point d'entrée principal de l'API."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "EduAccess" in data["projet"]


def test_api_health():
    """Vérifie le healthcheck."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["model_loaded"] is True


def test_api_metrics():
    """Vérifie que l'endpoint des métriques renvoie bien les scores des modèles."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "best_model" in data
    assert "Logistic Regression" in data["models"]
    assert "Random Forest" in data["models"]
    assert "Gradient Boosting" in data["models"]


def test_api_sample_profiles():
    """Vérifie que des profils de démonstration sont disponibles."""
    response = client.get("/sample_profiles")
    assert response.status_code == 200
    data = response.json()
    assert "profil_reussite_faible_risque" in data
    assert "profil_difficulte_eleve_risque" in data


def test_api_predict_single_profile():
    """Vérifie la prédiction unitaire sur un profil."""
    payload = {
        "id_student": 9999,
        "code_module": "AAA",
        "gender": "M",
        "region": "London Region",
        "highest_education": "HE Qualification",
        "imd_band": "80-90%",
        "age_band": "0-35",
        "disability": "N",
        "num_of_prev_attempts": 0,
        "studied_credits": 60,
        "date_registration": -30.0,
        "pre_course_clicks": 80.0,
        "early_30_clicks": 350.0,
        "total_clicks": 1500.0,
        "active_days": 40.0,
        "early_assessments_count": 2.0,
        "early_avg_score": 85.0,
        "early_late_submissions": 0.0,
        "total_assessments_submitted": 5.0,
        "overall_avg_score": 82.0,
        "min_score": 75.0,
        "late_submissions_count": 0.0,
        "failed_assessments_count": 0.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "is_at_risk" in data
    assert "risk_probability" in data
    assert "risk_level" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert data["risk_probability"] <= 0.40  # Profil brillant -> risque faible


def test_api_predict_batch():
    """Vérifie la prédiction en lot (batch)."""
    samples = client.get("/sample_profiles").json()
    batch_payload = {
        "students": [
            samples["profil_reussite_faible_risque"],
            samples["profil_difficulte_eleve_risque"]
        ]
    }
    response = client.post("/predict_batch", json=batch_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_analyzed"] == 2
    assert len(data["predictions"]) == 2
    assert 0 <= data["total_at_risk"] <= 2
