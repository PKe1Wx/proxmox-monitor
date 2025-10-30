#!/bin/bash

echo "========================================="
echo "Installation Proxmox Monitor"
echo "========================================="
echo ""

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Installation..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installé. Veuillez vous déconnecter et reconnecter pour appliquer les changements."
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Installation..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
fi

echo "✅ Docker et Docker Compose sont installés"
echo ""

# Créer le répertoire de données
mkdir -p data

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo "📝 Configuration initiale..."
    echo ""
    
    # Copier l'exemple
    cp .env.example .env
    
    # Demander les informations de base
    echo "Configuration Proxmox:"
    read -p "URL Proxmox (ex: https://192.168.1.100:8006): " PROXMOX_HOST
    
    echo ""
    echo "Choisissez le mode d'authentification:"
    echo "1) Token API (Recommandé)"
    echo "2) Mot de passe"
    read -p "Votre choix (1 ou 2): " AUTH_CHOICE
    
    if [ "$AUTH_CHOICE" = "1" ]; then
        read -p "Token ID (ex: monitoring@pve!monitor): " TOKEN_ID
        read -p "Token Secret: " TOKEN_SECRET
        
        sed -i "s|PROXMOX_HOST=.*|PROXMOX_HOST=$PROXMOX_HOST|" .env
        sed -i "s|# PROXMOX_TOKEN_ID=.*|PROXMOX_TOKEN_ID=$TOKEN_ID|" .env
        sed -i "s|# PROXMOX_TOKEN_SECRET=.*|PROXMOX_TOKEN_SECRET=$TOKEN_SECRET|" .env
        sed -i "s|PROXMOX_USER=.*|# PROXMOX_USER=root@pam|" .env
        sed -i "s|PROXMOX_PASSWORD=.*|# PROXMOX_PASSWORD=votre_mot_de_passe|" .env
    else
        read -p "Utilisateur (ex: root@pam): " PROXMOX_USER
        read -sp "Mot de passe: " PROXMOX_PASSWORD
        echo ""
        
        sed -i "s|PROXMOX_HOST=.*|PROXMOX_HOST=$PROXMOX_HOST|" .env
        sed -i "s|PROXMOX_USER=.*|PROXMOX_USER=$PROXMOX_USER|" .env
        sed -i "s|PROXMOX_PASSWORD=.*|PROXMOX_PASSWORD=$PROXMOX_PASSWORD|" .env
    fi
    
    echo ""
    echo "Configuration des notifications:"
    echo "1) Discord"
    echo "2) Gotify"
    echo "3) ntfy"
    echo "4) Webhook"
    read -p "Votre choix (1, 2, 3 ou 4): " NOTIF_CHOICE
    
    case $NOTIF_CHOICE in
        1)
            NOTIF_TYPE="discord"
            read -p "URL du webhook Discord: " NOTIF_URL
            NOTIF_TOKEN=""
            ;;
        2)
            NOTIF_TYPE="gotify"
            read -p "URL Gotify (ex: http://192.168.1.50:8080): " NOTIF_URL
            read -p "Token Gotify: " NOTIF_TOKEN
            ;;
        3)
            NOTIF_TYPE="ntfy"
            read -p "URL ntfy (ex: https://ntfy.sh/mon_topic): " NOTIF_URL
            NOTIF_TOKEN=""
            ;;
        4)
            NOTIF_TYPE="webhook"
            read -p "URL Webhook: " NOTIF_URL
            NOTIF_TOKEN=""
            ;;
    esac
    
    sed -i "s|NOTIFICATION_TYPE=.*|NOTIFICATION_TYPE=$NOTIF_TYPE|" .env
    sed -i "s|NOTIFICATION_URL=.*|NOTIFICATION_URL=$NOTIF_URL|" .env
    sed -i "s|NOTIFICATION_TOKEN=.*|NOTIFICATION_TOKEN=$NOTIF_TOKEN|" .env
    
    echo ""
    read -p "Heure du rapport quotidien (ex: 09:00): " REPORT_TIME
    sed -i "s|DAILY_REPORT_TIME=.*|DAILY_REPORT_TIME=$REPORT_TIME|" .env
    
    echo ""
    echo "✅ Configuration sauvegardée dans .env"
else
    echo "ℹ️  Fichier .env existant trouvé, utilisation de la configuration actuelle"
fi

echo ""
echo "🚀 Lancement du conteneur..."
docker-compose up -d --build

echo ""
echo "✅ Installation terminée !"
echo ""
echo "Commandes utiles:"
echo "  - Voir les logs:        docker-compose logs -f"
echo "  - Arrêter:              docker-compose stop"
echo "  - Redémarrer:           docker-compose restart"
echo "  - Supprimer:            docker-compose down"
echo ""
echo "Les logs sont aussi disponibles dans: ./data/proxmox_monitor.log"
echo ""
