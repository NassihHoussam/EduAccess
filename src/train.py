"""
Module d'entraînement et de comparaison des modèles de classification pour EduAccess.
Entraîne et compare au moins 3 modèles (Régression Logistique, Random Forest, Gradient Boosting),
calcule les métriques d'évaluation, et exporte le meilleur modèle ainsi que les métriques.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline

from src.config import (
    MODELS_DIR,
    BEST_MODEL_PATH,
    METRICS_PATH,
    ALL_FEATURES
)
from src.feature_engineering import get_preprocessor, prepare_train_test_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def train_and_compare_models() -> Dict[str, Any]:
    """
    Exécute le pipeline d'entraînement et de comparaison multi-modèles.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Chargement et préparation des données d'entraînement/test...")
    X_train, X_test, y_train, y_test = prepare_train_test_data(test_size=0.2, random_state=42)

    preprocessor = get_preprocessor()

    # Définition des modèles candidats
    candidate_models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=120, max_depth=14, min_samples_split=5, random_state=42, n_jobs=-1),
        "Gradient Boosting": HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, max_depth=8, random_state=42)
    }

    results = {}
    best_f1 = -1.0
    best_model_name = None
    best_pipeline = None

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    logger.info("Début de l'entraînement comparatif des modèles...")

    for name, clf in candidate_models.items():
        logger.info("--- Évaluation du modèle : %s ---", name)
        pipe = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])

        # Validation croisée 5-folds
        cv_scores = cross_validate(
            pipe, X_train, y_train,
            cv=cv,
            scoring=["accuracy", "precision", "recall", "f1", "roc_auc"],
            n_jobs=-1
        )

        # Entraînement complet sur le train set
        pipe.fit(X_train, y_train)

        # Prédictions sur le test set
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred))
        rec = float(recall_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred))
        auc = float(roc_auc_score(y_test, y_prob))
        cm = confusion_matrix(y_test, y_pred).tolist()
        report = classification_report(y_test, y_pred, output_dict=True)

        model_results = {
            "name": name,
            "test_metrics": {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "roc_auc": round(auc, 4)
            },
            "cv_metrics_mean": {
                "accuracy": round(float(np.mean(cv_scores["test_accuracy"])), 4),
                "precision": round(float(np.mean(cv_scores["test_precision"])), 4),
                "recall": round(float(np.mean(cv_scores["test_recall"])), 4),
                "f1_score": round(float(np.mean(cv_scores["test_f1"])), 4),
                "roc_auc": round(float(np.mean(cv_scores["test_roc_auc"])), 4)
            },
            "confusion_matrix": cm,
            "classification_report": report
        }
        results[name] = model_results

        # Sauvegarde individuelle du modèle
        slug = name.lower().replace(" ", "_")
        model_file = MODELS_DIR / f"model_{slug}.joblib"
        joblib.dump(pipe, model_file)
        logger.info("Modèle %s sauvegardé sous: %s", name, model_file)
        logger.info("%s -> Test F1: %.4f | AUC: %.4f | Acc: %.4f", name, f1, auc, acc)

        # Critère de sélection : meilleur F1-score (bon compromis précision/rappel sur le risque)
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_pipeline = pipe

    logger.info("Meilleur modèle sélectionné : %s (F1-score = %.4f)", best_model_name, best_f1)

    # Calcul de l'importance des variables sur un échantillon test pour l'interprétabilité
    logger.info("Calcul de l'importance des variables (Permutation Importance)...")
    sample_indices = np.random.choice(len(X_test), size=min(1500, len(X_test)), replace=False)
    X_test_sub = X_test.iloc[sample_indices]
    y_test_sub = y_test.iloc[sample_indices]

    perm_importance = permutation_importance(
        best_pipeline, X_test_sub, y_test_sub,
        n_repeats=5, random_state=42, n_jobs=-1, scoring="f1"
    )

    feature_importances = []
    for idx, feature_name in enumerate(ALL_FEATURES):
        feature_importances.append({
            "feature": feature_name,
            "importance": round(float(perm_importance.importances_mean[idx]), 5)
        })

    # Trier par ordre décroissant
    feature_importances.sort(key=lambda x: x["importance"], reverse=True)

    # Sauvegarde du meilleur modèle
    joblib.dump(best_pipeline, BEST_MODEL_PATH)
    logger.info("Meilleur modèle sauvegardé sous: %s", BEST_MODEL_PATH)

    # Sauvegarde globale des métriques
    payload = {
        "best_model": best_model_name,
        "models": results,
        "feature_importances": feature_importances,
        "features_list": ALL_FEATURES
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)

    logger.info("Métriques comparatives sauvegardées dans: %s", METRICS_PATH)
    return payload


if __name__ == "__main__":
    train_and_compare_models()
