FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers dans le conteneur
COPY . .

# Installer les dépendances Python
RUN pip install -r requirements.txt

# Commande pour exécuter le script Python
CMD ["python", "process_data.py"]
