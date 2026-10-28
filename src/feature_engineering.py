"""
Module de Feature Engineering et de prétraitement pour le projet EduAccess.
Fournit le pipeline de transformation des données et les fonctions d'interprétation des profils.
"""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET_COLUMN,
    RISK_THRESHOLD_LOW,
    RISK_THRESHOLD_HIGH
)
from src.data_loader import build_unified_dataset


def get_preprocessor() -> ColumnTransformer:
    """
    Construit le préprocesseur Scikit-learn :
    - Standardisation (moyenne 0, variance 1) pour les variables numériques.
    - Encodage One-Hot pour les variables catégorielles avec gestion des catégories inconnues.
    """
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )
    return preprocessor


def prepare_train_test_data(
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Charge les données consolidées et effectue une division train/test stratifiée sur la cible.
    """
    df = build_unified_dataset()

    features = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
    X = df[features]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    return X_train, X_test, y_train, y_test


def evaluate_risk_level(prob: float) -> str:
    """
    Associe un niveau de risque textuel en fonction de la probabilité prédite.
    """
    if prob >= RISK_THRESHOLD_HIGH:
        return "Élevé"
    elif prob >= RISK_THRESHOLD_LOW:
        return "Modéré"
    else:
        return "Faible"


def generate_recommendations(profile: Dict[str, Any], risk_prob: float) -> List[str]:
    """
    Génère des recommandations d'accompagnement pédagogique personnalisées
    en analysant les signaux faibles et facteurs de risque identifiés chez l'étudiant.
    """
    recommendations = []

    # 1. Analyse de l'engagement VLE
    early_clicks = float(profile.get("early_30_clicks", 0))
    pre_clicks = float(profile.get("pre_course_clicks", 0))
    active_days = float(profile.get("active_days", 0))

    if early_clicks < 100:
        recommendations.append(
            "Faible activité précoce sur la plateforme VLE (< 100 clics). "
            "Action recommandée : Prise de contact proactive par le tuteur pour vérifier l'accès aux ressources."
        )
    elif early_clicks < 300:
        recommendations.append(
            "Engagement modéré sur la plateforme VLE. "
            "Action recommandée : Envoyer des rappels d'auto-évaluation et encourager la participation aux forums."
        )

    if pre_clicks == 0:
        recommendations.append(
            "Aucune connexion enregistrée avant le début du cours. "
            "Action recommandée : Proposer un module de bienvenue ou tutoriel d'introduction."
        )

    # 2. Analyse des évaluations
    early_eval_count = float(profile.get("early_assessments_count", 0))
    early_avg = float(profile.get("early_avg_score", 0))
    failed_evals = float(profile.get("failed_assessments_count", 0))
    late_submissions = float(profile.get("late_submissions_count", 0))

    if early_eval_count == 0:
        recommendations.append(
            "Aucune évaluation soumise dans les premiers délais (60 jours). "
            "Action critique : Alerte pédagogique immédiate pour identifier d'éventuels blocages méthodologiques."
        )
    elif early_avg < 40:
        recommendations.append(
            f"Note moyenne précoce alarmante ({early_avg:.1f}/100 < seuil d'échec de 40). "
            "Action critique : Planifier une séance de tutorat individualisé ou de remise à niveau."
        )
    elif early_avg < 55:
        recommendations.append(
            f"Résultats initiaux fragiles ({early_avg:.1f}/100). "
            "Action recommandée : Proposer des exercices corrigés complémentaires et fiches de révision."
        )

    if late_submissions > 0:
        recommendations.append(
            f"{int(late_submissions)} devoir(s) soumis en retard. "
            "Action recommandée : Atelier de gestion du temps et réaménagement possible du calendrier d'étude."
        )

    if failed_evals > 0:
        recommendations.append(
            f"{int(failed_evals)} évaluation(s) non validée(s). "
            "Action recommandée : Proposer une session de feedback détaillée avec l'enseignant référent."
        )

    # 3. Facteurs de contexte académique
    credits = float(profile.get("studied_credits", 60))
    prev_attempts = float(profile.get("num_of_prev_attempts", 0))
    date_reg = float(profile.get("date_registration", 0))

    if credits > 120:
        recommendations.append(
            f"Charge académique très lourde ({int(credits)} crédits simultanés). "
            "Action recommandée : Conseiller un étalement du cursus pour prévenir l'épuisement."
        )

    if prev_attempts > 0:
        recommendations.append(
            f"Étudiant redoublant ce module ({int(prev_attempts)} tentative(s) antérieure(s)). "
            "Action recommandée : Analyser les causes des échecs précédents et adapter la progression."
        )

    if date_reg > 0:
        recommendations.append(
            f"Inscription tardive ({int(date_reg)} jours après le début officiel). "
            "Action recommandée : Fournir un kit d'intégration accéléré pour rattraper les modules initiaux."
        )

    # Support spécifique handicap
    if profile.get("disability") == "Y":
        recommendations.append(
            "Aménagement de cursus : Vérifier que les mesures d'accessibilité et tiers-temps sont bien effectifs."
        )

    # Si risque global élevé mais pas d'action spécifique identifiée
    if risk_prob >= RISK_THRESHOLD_HIGH and len(recommendations) == 0:
        recommendations.append(
            "Profil globalement à risque d'après les indicateurs combinés. "
            "Action conseillée : Entretien pédagogique de suivi semi-personnalisé."
        )
    elif risk_prob < RISK_THRESHOLD_LOW and len(recommendations) == 0:
        recommendations.append(
            "Profil régulier et engagé. Poursuivre le rythme actuel et encourager vers une mention (Distinction)."
        )

    return recommendations
