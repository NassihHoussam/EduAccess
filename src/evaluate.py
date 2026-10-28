"""
Module d'évaluation et de diagnostic des modèles pour EduAccess.
Fournit des fonctions pour analyser les performances, générer des visualisations et diagnostiquer des erreurs.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    classification_report
)

from src.config import BEST_MODEL_PATH, METRICS_PATH, ALL_FEATURES
from src.feature_engineering import prepare_train_test_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_best_model():
    """
    Charge le modèle optimal sauvegardé.
    """
    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Le modèle {BEST_MODEL_PATH} n'existe pas. Veuillez lancer l'entraînement.")
    return joblib.load(BEST_MODEL_PATH)


def load_metrics() -> Dict[str, Any]:
    """
    Charge les métriques pré-calculées depuis le fichier JSON.
    """
    if not METRICS_PATH.exists():
        raise FileNotFoundError(f"Le fichier de métriques {METRICS_PATH} n'existe pas.")
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_roc_curve_data(model=None) -> Dict[str, Any]:
    """
    Calcule les points (FPR, TPR, seuils) de la courbe ROC sur l'ensemble de test.
    """
    if model is None:
        model = load_best_model()

    _, X_test, _, y_test = prepare_train_test_data(test_size=0.2, random_state=42)
    y_prob = model.predict_proba(X_test)[:, 1]

    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    auc_score = float(roc_auc_score(y_test, y_prob))

    # Échantillonnage pour un rendu graphique fluide
    indices = np.linspace(0, len(fpr) - 1, min(100, len(fpr))).astype(int)
    
    return {
        "fpr": fpr[indices].tolist(),
        "tpr": tpr[indices].tolist(),
        "thresholds": thresholds[indices].tolist(),
        "auc": round(auc_score, 4)
    }


def evaluate_threshold_impact(model=None, thresholds: list = None) -> list:
    """
    Simule l'impact de différents seuils de décision (ex: 0.3, 0.4, 0.5, 0.6, 0.7)
    sur la Précision et le Rappel pour l'aide à la décision.
    """
    if model is None:
        model = load_best_model()

    if thresholds is None:
        thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    _, X_test, _, y_test = prepare_train_test_data(test_size=0.2, random_state=42)
    y_prob = model.predict_proba(X_test)[:, 1]

    impact_table = []
    for th in thresholds:
        y_pred_th = (y_prob >= th).astype(int)
        acc = accuracy_score(y_test, y_pred_th)
        prec = precision_score(y_test, y_pred_th, zero_division=0)
        rec = recall_score(y_test, y_pred_th, zero_division=0)
        f1 = f1_score(y_test, y_pred_th, zero_division=0)

        impact_table.append({
            "seuil": round(th, 2),
            "precision": round(float(prec), 4),
            "rappel": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "accuracy": round(float(acc), 4)
        })

    return impact_table


if __name__ == "__main__":
    metrics = load_metrics()
    print("Modèle retenu :", metrics["best_model"])
    print("Métriques de test :", metrics["models"][metrics["best_model"]]["test_metrics"])
