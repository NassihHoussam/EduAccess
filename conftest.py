import sys
from pathlib import Path

# Ajouter la racine du projet au sys.path pour pytest
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
