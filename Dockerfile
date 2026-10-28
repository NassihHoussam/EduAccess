# Dockerfile multi-services pour EduAccess
FROM python:3.11-slim

# Configuration des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des exigences Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source et des données
COPY . .

# Exposer les ports API (8000) et Streamlit (8501)
EXPOSE 8000 8501

# Commande par défaut (démarrage de l'API)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
