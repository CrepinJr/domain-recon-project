# Étape 1 : L'image de construction
# Utilise une image complète pour construire et installer les dépendances.
FROM python:3.11-bookworm AS builder

# Définit le répertoire de travail
WORKDIR /app

# Copie le fichier de dépendances et les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie ton code
COPY . .


# Étape 2 : L'image finale (l'image de production)
# Utilise une image minimale pour le déploiement final.
FROM python:3.11-slim-bookworm

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers de l'étape de construction vers l'étape finale
# On ne copie que ce qui est nécessaire (ton code et les dépendances).
COPY --from=builder /app /app

# Commande par défaut pour lancer l'application
CMD ["python", "main.py"]