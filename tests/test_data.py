"""
Tests unitaires pour le chargement et le prétraitement des données (src.data_loader).
"""

import pytest
import pandas as pd
from src.config import PROCESSED_DATA_PATH, ALL_FEATURES, TARGET_COLUMN
from src.data_loader import build_unified_dataset


def test_processed_dataset_exists_and_loads():
    """Vérifie que le jeu de données consolidé existe et se charge sans erreur."""
    assert PROCESSED_DATA_PATH.exists(), "Le fichier processed_students.csv doit exister."
    df = pd.read_csv(PROCESSED_DATA_PATH)
    assert len(df) > 10000, "Le dataset OULAD doit contenir plus de 10 000 étudiants."


def test_required_features_present():
    """Vérifie que toutes les caractéristiques explicatives et la cible sont présentes."""
    df = pd.read_csv(PROCESSED_DATA_PATH)
    for col in ALL_FEATURES:
        assert col in df.columns, f"La variable {col} doit être présente dans le dataset consolidé."
    assert TARGET_COLUMN in df.columns, f"La cible {TARGET_COLUMN} doit être présente."


def test_target_values_and_no_nulls_in_critical_features():
    """Vérifie que la cible est bien binaire (0 ou 1) et sans valeurs manquantes."""
    df = pd.read_csv(PROCESSED_DATA_PATH)
    unique_targets = set(df[TARGET_COLUMN].unique())
    assert unique_targets == {0, 1}, f"La cible doit être strictement binaire {0, 1}, reçu {unique_targets}"

    # Vérification des colonnes numériques clés (aucune valeur manquante tolérée après nettoyage)
    for num_col in ["total_clicks", "early_30_clicks", "studied_credits", "date_registration"]:
        assert df[num_col].isnull().sum() == 0, f"La colonne {num_col} ne doit contenir aucune valeur manquante."
