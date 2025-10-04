# Étape 1 : Builder (contient les outils de construction)
FROM python:3.13-slim-bookworm AS builder

# Correction de sécurité 1 : Mise à jour complète du système d'exploitation (OS)
# Corrige les failles dans libc6, libexpat1, etc.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libgirepository-1.0-1 \
    libpango-1.0-0 \
    libharfbuzz0b \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libxml2-dev \
    libxslt1-dev \
    libpangoft2-1.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie requirements.txt avant le reste du code.
COPY requirements.txt .

# Correction de sécurité 2 : Mise à jour des outils Python
# Corrige la faille HIGH dans setuptools (CVE-2025-47273)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Installation des dépendances de l'application
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code de l'application.
COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY pdf_templates/ pdf_templates/

# Étape 2 : Image finale (plus petite pour la production)
FROM python:3.13-slim-bookworm

# Installe les dépendances système nécessaires à l'exécution de l'application.
RUN apt-get update && \
    # Correction de sécurité 1 (bis) : Mise à jour du système d'exploitation pour l'image finale
    apt-get dist-upgrade -y && \
    apt-get install -y --no-install-recommends \
    libgirepository-1.0-1 \
    libpango-1.0-0 \
    libharfbuzz0b \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libxml2-dev \
    libxslt1-dev \
    libpangoft2-1.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie les fichiers de l'étape de construction vers l'étape finale.
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]