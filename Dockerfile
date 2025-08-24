# Étape 1 : Builder (contient les outils de construction)
FROM python:3.11-slim-bookworm AS builder

# Installe les dépendances système de WeasyPrint.
# Ces paquets ne changent que très rarement.
RUN apt-get update && apt-get install -y --no-install-recommends \
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
# L'installation des dépendances Python est mise en cache tant que requirements.txt ne change pas.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste du code de l'application.
# Cette étape est exécutée seulement si le contenu de ces dossiers change.
COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY pdf_templates/ pdf_templates/

# Étape 2 : Image finale (plus petite pour la production)
FROM python:3.11-slim-bookworm

# Installe les dépendances système nécessaires à l'exécution de l'application.
# On n'a plus besoin des outils de "build" comme build-essential.
RUN apt-get update && apt-get install -y --no-install-recommends \
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