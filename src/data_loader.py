"""
Module de chargement, nettoyage et préparation des données OULAD pour le projet EduAccess.
Traite les données brutes multi-tables et génère une vue unifiée orientée étudiant.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_PATH,
    FEATURE_METADATA_PATH,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    TARGET_COLUMN
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def aggregate_vle_data(vle_path: Path, chunk_size: int = 1_000_000) -> pd.DataFrame:
    """
    Agrège les interactions avec le VLE (Virtual Learning Environment) par étudiant et module.
    Calcule l'engagement précoce (avant le début du cours, premiers 30 jours, et total).
    """
    logger.info("Agrégation des interactions VLE par morceaux (chunks)...")
    usecols = ["code_module", "code_presentation", "id_student", "date", "sum_click"]
    agg_chunks = []

    for chunk in pd.read_csv(vle_path, usecols=usecols, chunksize=chunk_size, na_values=["?", ""]):
        chunk["clicks_pre_course"] = chunk["sum_click"].where(chunk["date"] < 0, 0)
        chunk["clicks_early_30"] = chunk["sum_click"].where(chunk["date"] <= 30, 0)

        chunk_agg = chunk.groupby(["code_module", "code_presentation", "id_student"]).agg(
            total_clicks=("sum_click", "sum"),
            pre_course_clicks=("clicks_pre_course", "sum"),
            early_30_clicks=("clicks_early_30", "sum"),
            active_days=("date", "nunique")
        ).reset_index()
        agg_chunks.append(chunk_agg)

    combined = pd.concat(agg_chunks, ignore_index=True)
    vle_summary = combined.groupby(["code_module", "code_presentation", "id_student"]).agg(
        total_clicks=("total_clicks", "sum"),
        pre_course_clicks=("pre_course_clicks", "sum"),
        early_30_clicks=("early_30_clicks", "sum"),
        active_days=("active_days", "sum")
    ).reset_index()

    logger.info("Agrégation VLE terminée avec succès. %d profils agrégés.", len(vle_summary))
    return vle_summary


def aggregate_assessment_data(student_asm_path: Path, assessments_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Agrège les résultats aux évaluations (notes, retards, échecs partiels).
    Distingue les évaluations précoces (date <= 60 jours) du bilan global.
    """
    logger.info("Agrégation des évaluations étudiants...")
    sa = pd.read_csv(student_asm_path, na_values=["?", ""])
    asm = pd.read_csv(assessments_path, na_values=["?", ""])

    sa_asm = pd.merge(sa, asm, on="id_assessment", how="left")
    
    # Indicateurs de retard et d'échec
    sa_asm["is_late"] = (sa_asm["date_submitted"] > sa_asm["date"]).fillna(False).astype(int)
    sa_asm["is_failed"] = (sa_asm["score"] < 40).fillna(False).astype(int)

    # Évaluations précoces (échéance <= 60 jours)
    early_mask = sa_asm["date"].fillna(999) <= 60
    early_asm = sa_asm[early_mask]

    early_agg = early_asm.groupby(["id_student", "code_module", "code_presentation"]).agg(
        early_assessments_count=("score", "count"),
        early_avg_score=("score", "mean"),
        early_late_submissions=("is_late", "sum")
    ).reset_index()

    # Évaluations globales
    total_agg = sa_asm.groupby(["id_student", "code_module", "code_presentation"]).agg(
        total_assessments_submitted=("score", "count"),
        overall_avg_score=("score", "mean"),
        min_score=("score", "min"),
        late_submissions_count=("is_late", "sum"),
        failed_assessments_count=("is_failed", "sum")
    ).reset_index()

    logger.info("Agrégation des évaluations terminée.")
    return early_agg, total_agg


def build_unified_dataset(force_recompute: bool = False) -> pd.DataFrame:
    """
    Construit le jeu de données unifié en fusionnant les tables OULAD.
    Met en cache le résultat sous `data/processed_students.csv` pour des chargements rapides.
    """
    if PROCESSED_DATA_PATH.exists() and not force_recompute:
        logger.info("Chargement du jeu de données depuis le cache: %s", PROCESSED_DATA_PATH)
        return pd.read_csv(PROCESSED_DATA_PATH)

    logger.info("Génération du jeu de données consolidé depuis les fichiers sources...")
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    si_path = RAW_DATA_DIR / "studentInfo.csv"
    sr_path = RAW_DATA_DIR / "studentRegistration.csv"
    sa_path = RAW_DATA_DIR / "studentAssessment.csv"
    asm_path = RAW_DATA_DIR / "assessments.csv"
    vle_path = RAW_DATA_DIR / "studentVle.csv"

    # Vérification d'existence des fichiers
    for p in [si_path, sr_path, sa_path, asm_path, vle_path]:
        if not p.exists():
            raise FileNotFoundError(f"Le fichier {p} est introuvable. Vérifiez l'arborescence des données OULAD.")

    student_info = pd.read_csv(si_path, na_values=["?", ""])
    student_reg = pd.read_csv(sr_path, na_values=["?", ""])

    vle_agg = aggregate_vle_data(vle_path)
    early_asm_agg, total_asm_agg = aggregate_assessment_data(sa_path, asm_path)

    # Fusion des tables
    merge_keys = ["code_module", "code_presentation", "id_student"]
    df = pd.merge(student_info, student_reg[merge_keys + ["date_registration"]], on=merge_keys, how="left")
    df = pd.merge(df, vle_agg, on=merge_keys, how="left")
    df = pd.merge(df, early_asm_agg, on=merge_keys, how="left")
    df = pd.merge(df, total_asm_agg, on=merge_keys, how="left")

    # Nettoyage et imputation des valeurs manquantes
    # 1. Variables VLE
    for col in ["total_clicks", "pre_course_clicks", "early_30_clicks", "active_days"]:
        df[col] = df[col].fillna(0).astype(float)

    # 2. Variables évaluations
    for col in ["early_assessments_count", "early_avg_score", "early_late_submissions",
                "total_assessments_submitted", "overall_avg_score", "min_score",
                "late_submissions_count", "failed_assessments_count"]:
        df[col] = df[col].fillna(0).astype(float)

    # 3. Variable inscription : médiane
    med_reg = df["date_registration"].median()
    df["date_registration"] = df["date_registration"].fillna(med_reg).astype(float)

    # 4. Variable imd_band : 'Missing'
    df["imd_band"] = df["imd_band"].fillna("Missing")

    # 5. Variable cible binaire (At-Risk = 1 pour Fail ou Withdrawn, 0 sinon)
    df[TARGET_COLUMN] = df["final_result"].isin(["Fail", "Withdrawn"]).astype(int)

    # Sauvegarde du jeu de données nettoyé
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info("Données unifiées sauvegardées avec succès dans: %s (Total lignes: %d)", PROCESSED_DATA_PATH, len(df))

    # Sauvegarde des métadonnées des variables
    metadata = {
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "target_column": TARGET_COLUMN,
        "total_rows": int(len(df)),
        "class_counts": {str(k): int(v) for k, v in df[TARGET_COLUMN].value_counts().items()},
        "final_result_distribution": {str(k): int(v) for k, v in df["final_result"].value_counts().items()}
    }
    with open(FEATURE_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    return df


if __name__ == "__main__":
    build_unified_dataset(force_recompute=True)
