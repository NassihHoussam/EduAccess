"""
Schémas Pydantic pour la validation des requêtes et réponses de l'API EduAccess.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StudentProfileInput(BaseModel):
    id_student: Optional[int] = Field(None, description="Identifiant unique de l'étudiant (optionnel)")
    code_module: str = Field("AAA", description="Code du module (ex: AAA, BBB, CCC, DDD, EEE, FFF, GGG)")
    gender: str = Field("M", description="Genre de l'étudiant ('M' ou 'F')")
    region: str = Field("East Anglian Region", description="Région géographique")
    highest_education: str = Field("HE Qualification", description="Niveau d'études initial")
    imd_band: str = Field("50-60%", description="Indice de défavorisation multiple (ex: '0-10%', '50-60%', 'Missing')")
    age_band: str = Field("0-35", description="Tranche d'âge ('0-35', '35-55', '55<=')")
    disability: str = Field("N", description="Handicap déclaré ('Y' ou 'N')")

    num_of_prev_attempts: int = Field(0, ge=0, description="Nombre de tentatives antérieures sur ce module")
    studied_credits: int = Field(60, ge=0, description="Nombre de crédits étudiés simultanément")
    date_registration: float = Field(-30.0, description="Date d'inscription relative au début (jours)")

    # Engagement VLE
    pre_course_clicks: float = Field(50.0, ge=0, description="Clics VLE avant le début du cours")
    early_30_clicks: float = Field(250.0, ge=0, description="Clics VLE durant les 30 premiers jours")
    total_clicks: float = Field(800.0, ge=0, description="Total des clics VLE enregistrés")
    active_days: float = Field(25.0, ge=0, description="Nombre de jours distincts d'activité sur le VLE")

    # Résultats aux évaluations
    early_assessments_count: float = Field(2.0, ge=0, description="Nombre de devoirs rendus tôt (<= 60j)")
    early_avg_score: float = Field(72.0, ge=0, le=100, description="Note moyenne aux premières évaluations")
    early_late_submissions: float = Field(0.0, ge=0, description="Nombre de devoirs précoces rendus en retard")
    total_assessments_submitted: float = Field(4.0, ge=0, description="Total des devoirs soumis")
    overall_avg_score: float = Field(70.0, ge=0, le=100, description="Note moyenne globale")
    min_score: float = Field(60.0, ge=0, le=100, description="Note minimale obtenue")
    late_submissions_count: float = Field(0.0, ge=0, description="Total des devoirs rendus en retard")
    failed_assessments_count: float = Field(0.0, ge=0, description="Nombre de devoirs échoués (score < 40)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_student": 10001,
                "code_module": "BBB",
                "gender": "F",
                "region": "London Region",
                "highest_education": "A Level or Equivalent",
                "imd_band": "40-50%",
                "age_band": "0-35",
                "disability": "N",
                "num_of_prev_attempts": 0,
                "studied_credits": 60,
                "date_registration": -25.0,
                "pre_course_clicks": 35.0,
                "early_30_clicks": 180.0,
                "total_clicks": 450.0,
                "active_days": 18.0,
                "early_assessments_count": 1.0,
                "early_avg_score": 45.0,
                "early_late_submissions": 1.0,
                "total_assessments_submitted": 2.0,
                "overall_avg_score": 42.0,
                "min_score": 38.0,
                "late_submissions_count": 1.0,
                "failed_assessments_count": 1.0
            }
        }
    }


class PredictionResponse(BaseModel):
    id_student: Optional[int] = Field(None, description="Identifiant étudiant")
    is_at_risk: bool = Field(..., description="True si l'étudiant est identifié comme profil à risque")
    risk_probability: float = Field(..., description="Probabilité estimée d'être en difficulté (0 à 1)")
    risk_percentage: float = Field(..., description="Probabilité sous forme de pourcentage (0 à 100%)")
    risk_level: str = Field(..., description="Niveau catégoriel de risque ('Faible', 'Modéré', 'Élevé')")
    confidence: float = Field(..., description="Indice de confiance du modèle")
    recommendations: List[str] = Field(..., description="Actions d'accompagnement pédagogique suggérées")
    model_used: str = Field(..., description="Nom du modèle utilisé pour l'inférence")


class BatchPredictionRequest(BaseModel):
    students: List[StudentProfileInput] = Field(..., description="Liste de profils étudiants à analyser")


class BatchPredictionResponse(BaseModel):
    total_analyzed: int = Field(..., description="Nombre total d'étudiants analysés")
    total_at_risk: int = Field(..., description="Nombre d'étudiants identifiés à risque")
    risk_rate_percentage: float = Field(..., description="Pourcentage de profils à risque dans la cohorte")
    predictions: List[PredictionResponse] = Field(..., description="Résultats individuels détaillés")


class HealthResponse(BaseModel):
    status: str
    service: str
    model_loaded: bool
    best_model_name: str
    version: str
