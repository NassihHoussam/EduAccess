"""
Script utilitaire CLI pour piloter le projet EduAccess.
Permet d'exécuter facilement les étapes clés : pipeline ETL, entraînement ML, tests et lancement des services.

Usage :
    python run_project.py prepare   # Prétraitement et agrégation des données
    python run_project.py train     # Entraînement et comparaison des modèles
    python run_project.py test      # Exécution des tests automatisés (pytest)
    python run_project.py api       # Lancement du serveur API FastAPI
    python run_project.py app       # Lancement de l'interface Streamlit
    python run_project.py full      # Exécute ETL + train + test
"""

import argparse
import subprocess
import sys


def run_cmd(command: list, description: str):
    print(f"\n[INFO] === {description} ===")
    print(f"Commande : {' '.join(command)}")
    res = subprocess.run(command)
    if res.returncode != 0:
        print(f"[ERREUR] Échec de l'étape : {description} (Code de retour {res.returncode})")
        sys.exit(res.returncode)
    print(f"[SUCCÈS] {description} terminée avec succès.\n")


def main():
    parser = argparse.ArgumentParser(description="Gestionnaire d'exécution EduAccess")
    parser.add_argument(
        "action",
        choices=["prepare", "train", "test", "api", "app", "full"],
        help="Action à exécuter"
    )
    args = parser.parse_args()

    if args.action == "prepare":
        run_cmd([sys.executable, "-m", "src.data_loader"], "Préparation des données OULAD")

    elif args.action == "train":
        run_cmd([sys.executable, "-m", "src.train"], "Entraînement et comparaison des modèles ML")

    elif args.action == "test":
        run_cmd([sys.executable, "-m", "pytest", "-v"], "Exécution de la suite de tests unitaires")

    elif args.action == "api":
        print("\n[INFO] Démarrage de l'API FastAPI sur http://127.0.0.1:8000 (Swagger docs sur http://127.0.0.1:8000/docs)")
        subprocess.run(["uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])

    elif args.action == "app":
        print("\n[INFO] Démarrage du tableau de bord Streamlit sur http://localhost:8501")
        subprocess.run(["streamlit", "run", "app/streamlit_app.py"])

    elif args.action == "full":
        run_cmd([sys.executable, "-m", "src.data_loader"], "1/3 Préparation des données")
        run_cmd([sys.executable, "-m", "src.train"], "2/3 Entraînement des modèles")
        run_cmd([sys.executable, "-m", "pytest", "-v"], "3/3 Exécution des tests")
        print("[SUCCÈS] Pipeline complet validé ! Vous pouvez maintenant lancer l'API (`python run_project.py api`) ou l'interface (`python run_project.py app`).")


if __name__ == "__main__":
    main()
