"""
Application FastAPI pour le projet EduAccess.
Fournit une API REST documentée (Swagger /docs) pour l'inférence de risque académique,
le monitoring des métriques, et l'analyse de cohortes d'étudiants.
"""

from contextlib import asynccontextmanager
import io
import json
import logging
from typing import List, Dict, Any
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import BEST_MODEL_PATH, METRICS_PATH, ALL_FEATURES
from src.feature_engineering import evaluate_risk_level, generate_recommendations
from api.schemas import (
    StudentProfileInput,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Cache du modèle et des métriques
model_cache = {}


def get_model():
    """Charge le modèle en mémoire de façon singleton."""
    if "pipeline" not in model_cache:
        if not BEST_MODEL_PATH.exists():
            logger.error("Le modèle n'existe pas sous %s", BEST_MODEL_PATH)
            raise RuntimeError("Le modèle n'a pas encore été entraîné.")
        logger.info("Chargement du modèle depuis: %s", BEST_MODEL_PATH)
        model_cache["pipeline"] = joblib.load(BEST_MODEL_PATH)

        if METRICS_PATH.exists():
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                model_cache["metrics"] = json.load(f)
        else:
            model_cache["metrics"] = {"best_model": "Gradient Boosting", "models": {}}

    return model_cache["pipeline"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise le modèle au démarrage de l'API."""
    try:
        get_model()
        logger.info("EduAccess API prête à recevoir des requêtes.")
    except Exception as e:
        logger.warning("Modèle non chargé au démarrage : %s", e)
    yield


# Initialisation de l'application FastAPI
app = FastAPI(
    title="EduAccess API",
    description=(
        "API d'aide à la décision pour la détection précoce des difficultés d'apprentissage "
        "sur le jeu de données OULAD (Open University Learning Analytics Dataset)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Général"])
def root():
    """Point d'entrée racine avec informations sur l'API."""
    return {
        "projet": "EduAccess - Détection précoce des difficultés d'apprentissage",
        "description": "Outil d'aide à l'analyse et à l'accompagnement pédagogique",
        "documentation_swagger": "/docs",
        "documentation_redoc": "/redoc",
        "endpoints_principaux": [
            "GET /health",
            "GET /metrics",
            "GET /sample_profiles",
            "POST /predict",
            "POST /predict_batch",
            "POST /predict_csv"
        ]
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health_check():
    """Vérifie l'état de santé du service et du modèle."""
    is_loaded = BEST_MODEL_PATH.exists()
    model_name = "Gradient Boosting"
    if METRICS_PATH.exists():
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                m = json.load(f)
                model_name = m.get("best_model", model_name)
        except Exception:
            pass

    return HealthResponse(
        status="healthy" if is_loaded else "degraded",
        service="EduAccess ML Service",
        model_loaded=is_loaded,
        best_model_name=model_name,
        version="1.0.0"
    )


@app.get("/metrics", tags=["Modèles & Évaluation"])
def get_metrics():
    """Retourne les métriques comparatives complètes de tous les modèles entraînés."""
    if not METRICS_PATH.exists():
        raise HTTPException(status_code=404, detail="Fichier de métriques introuvable.")
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)
    return metrics_data


@app.get("/sample_profiles", tags=["Exemples"])
def get_sample_profiles():
    """Retourne des profils étudiants types (Risque Faible, Modéré, Élevé) pour tests rapides."""
    return {
        "profil_reussite_faible_risque": {
            "id_student": 101,
            "code_module": "BBB",
            "gender": "F",
            "region": "London Region",
            "highest_education": "HE Qualification",
            "imd_band": "60-70%",
            "age_band": "0-35",
            "disability": "N",
            "num_of_prev_attempts": 0,
            "studied_credits": 60,
            "date_registration": -35.0,
            "pre_course_clicks": 120.0,
            "early_30_clicks": 450.0,
            "total_clicks": 1800.0,
            "active_days": 45.0,
            "early_assessments_count": 2.0,
            "early_avg_score": 82.0,
            "early_late_submissions": 0.0,
            "total_assessments_submitted": 5.0,
            "overall_avg_score": 80.0,
            "min_score": 75.0,
            "late_submissions_count": 0.0,
            "failed_assessments_count": 0.0
        },
        "profil_difficulte_eleve_risque": {
            "id_student": 202,
            "code_module": "BBB",
            "gender": "M",
            "region": "North Western Region",
            "highest_education": "Lower Than A Level",
            "imd_band": "10-20%",
            "age_band": "0-35",
            "disability": "N",
            "num_of_prev_attempts": 1,
            "studied_credits": 120,
            "date_registration": 5.0,
            "pre_course_clicks": 0.0,
            "early_30_clicks": 25.0,
            "total_clicks": 80.0,
            "active_days": 4.0,
            "early_assessments_count": 1.0,
            "early_avg_score": 32.0,
            "early_late_submissions": 1.0,
            "total_assessments_submitted": 1.0,
            "overall_avg_score": 32.0,
            "min_score": 32.0,
            "late_submissions_count": 1.0,
            "failed_assessments_count": 1.0
        },
        "profil_intermediaire_modere": {
            "id_student": 303,
            "code_module": "AAA",
            "gender": "F",
            "region": "South Region",
            "highest_education": "A Level or Equivalent",
            "imd_band": "40-50%",
            "age_band": "35-55",
            "disability": "N",
            "num_of_prev_attempts": 0,
            "studied_credits": 60,
            "date_registration": -10.0,
            "pre_course_clicks": 20.0,
            "early_30_clicks": 190.0,
            "total_clicks": 520.0,
            "active_days": 18.0,
            "early_assessments_count": 2.0,
            "early_avg_score": 52.0,
            "early_late_submissions": 1.0,
            "total_assessments_submitted": 3.0,
            "overall_avg_score": 54.0,
            "min_score": 45.0,
            "late_submissions_count": 1.0,
            "failed_assessments_count": 0.0
        }
    }


def predict_single_profile(model, profile_dict: Dict[str, Any], model_name: str) -> PredictionResponse:
    """Effectue l'inférence pour un profil individuel."""
    row_df = pd.DataFrame([profile_dict])[ALL_FEATURES]

    probabilities = model.predict_proba(row_df)[0]
    risk_prob = float(probabilities[1])
    is_at_risk = bool(risk_prob >= 0.5)
    risk_level = evaluate_risk_level(risk_prob)

    confidence = float(max(probabilities))
    recs = generate_recommendations(profile_dict, risk_prob)

    return PredictionResponse(
        id_student=profile_dict.get("id_student"),
        is_at_risk=is_at_risk,
        risk_probability=round(risk_prob, 4),
        risk_percentage=round(risk_prob * 100, 2),
        risk_level=risk_level,
        confidence=round(confidence, 4),
        recommendations=recs,
        model_used=model_name
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prédiction"])
def predict(profile: StudentProfileInput):
    """
    Prédit le risque d'échec ou d'abandon pour un profil étudiant.
    Fournit le score de risque, le niveau d'alerte et les actions d'accompagnement.
    """
    try:
        model = get_model()
        model_name = model_cache.get("metrics", {}).get("best_model", "Gradient Boosting")
        data_dict = profile.model_dump()
        return predict_single_profile(model, data_dict, model_name)
    except Exception as e:
        logger.exception("Erreur lors de la prédiction : %s", e)
        raise HTTPException(status_code=500, detail=f"Erreur d'inférence: {str(e)}")


@app.post("/predict_batch", response_model=BatchPredictionResponse, tags=["Prédiction"])
def predict_batch(batch_request: BatchPredictionRequest):
    """
    Analyse un ensemble d'étudiants (cohorte) et calcule les indicateurs globaux et individuels.
    """
    try:
        model = get_model()
        model_name = model_cache.get("metrics", {}).get("best_model", "Gradient Boosting")

        predictions = []
        at_risk_count = 0

        for student_input in batch_request.students:
            res = predict_single_profile(model, student_input.model_dump(), model_name)
            if res.is_at_risk:
                at_risk_count += 1
            predictions.append(res)

        total = len(predictions)
        risk_rate = (at_risk_count / total * 100) if total > 0 else 0.0

        return BatchPredictionResponse(
            total_analyzed=total,
            total_at_risk=at_risk_count,
            risk_rate_percentage=round(risk_rate, 2),
            predictions=predictions
        )
    except Exception as e:
        logger.exception("Erreur lors de la prédiction batch : %s", e)
        raise HTTPException(status_code=500, detail=f"Erreur batch: {str(e)}")


@app.post("/predict_csv", tags=["Prédiction"])
async def predict_csv(file: UploadFile = File(...)):
    """
    Permet de téléverser un fichier CSV contenant des étudiants
    et retourne le tableau enrichi avec le score de risque et le diagnostic.
    """
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        missing = [c for c in ALL_FEATURES if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Le fichier CSV ne contient pas les colonnes requises: {missing}"
            )

        model = get_model()
        probs = model.predict_proba(df[ALL_FEATURES])[:, 1]
        df["risk_probability"] = (probs).round(4)
        df["risk_percentage"] = (probs * 100).round(2)
        df["risk_level"] = [evaluate_risk_level(p) for p in probs]
        df["is_at_risk"] = probs >= 0.5

        return JSONResponse(content={
            "total_rows": len(df),
            "at_risk_count": int(df["is_at_risk"].sum()),
            "risk_rate": round(float(df["is_at_risk"].mean() * 100), 2),
            "sample_results": df[["risk_percentage", "risk_level", "is_at_risk"] + ALL_FEATURES[:5]].head(10).to_dict(orient="records")
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse CSV: {str(e)}")
