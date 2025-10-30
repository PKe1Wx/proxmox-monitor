FROM python:3.11-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de l'application
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script
COPY proxmox_monitor.py .

# Créer le répertoire pour les données persistantes
RUN mkdir -p /data

# Rendre le script exécutable
RUN chmod +x proxmox_monitor.py

# Définir les variables d'environnement par défaut
ENV CHECK_INTERVAL=60
ENV DAILY_REPORT_TIME=09:00

# Volume pour les données persistantes
VOLUME ["/data"]

# Lancer le script
CMD ["python", "-u", "proxmox_monitor.py"]
