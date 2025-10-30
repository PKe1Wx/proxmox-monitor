# 🖥️ Proxmox Monitor - Monitoring léger avec notifications Discord

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Proxmox](https://img.shields.io/badge/Proxmox-VE-orange.svg)](https://www.proxmox.com/)

Script de monitoring léger pour Proxmox VE qui envoie des notifications Discord lors de la création de VM/LXC, leur démarrage, et un rapport quotidien de l'état de toutes vos machines.

![Discord Notification Example](https://via.placeholder.com/600x200/5865F2/FFFFFF?text=Discord+Notification+Example)

---

## ✨ Fonctionnalités

- 🆕 **Détection automatique** des nouvelles VM et conteneurs LXC
- 🚀 **Notification au démarrage** des machines (passage de stopped → running)
- 📊 **Rapport quotidien** à l'heure de votre choix avec l'état de toutes vos machines
- 🌐 **Récupération automatique des adresses IP**
  - VM : via QEMU Guest Agent
  - LXC : via les interfaces réseau (automatique)
- 🔔 **Notifications Discord** avec embeds colorés
- 💾 **Persistance des données** pour suivre l'historique des machines
- 🐳 **Dockerisé** et optimisé pour Raspberry Pi
- 🔐 **Support Token API** Proxmox (sécurisé)
- 🌍 **Multi-nœuds** : supporte les clusters Proxmox

---

## 📋 Prérequis

- **Proxmox VE** 7.x ou 8.x
- **Docker** et **Docker Compose** installés
- **Webhook Discord** (gratuit)
- Accès à l'API Proxmox (token ou mot de passe root)

---

## 🚀 Installation rapide

### 1. Cloner le projet

```bash
git clone https://github.com/PKe1Wx/proxmox-monitor
cd proxmox-monitor
```

### 2. Créer un token API Proxmox (recommandé)

Sur votre serveur Proxmox, en SSH :

```bash
# Créer un utilisateur dédié
pveum user add monitoring@pve

# Donner les droits de lecture seule
pveum aclmod / -user monitoring@pve -role PVEAuditor

# Créer le token API
pveum user token add monitoring@pve monitor -privsep 0
```

**📝 Notez le token secret affiché** (vous ne le reverrez plus !)

### 3. Créer un webhook Discord

1. Ouvrez Discord
2. Clic droit sur un salon → **Modifier le salon**
3. **Intégrations** → **Webhooks** → **Nouveau Webhook**
4. Copiez l'URL du webhook

### 4. Configurer

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer la configuration
nano .env
```

Modifiez les valeurs :

```env
# Proxmox
PROXMOX_HOST=https://192.168.1.100:8006
PROXMOX_TOKEN_ID=monitoring@pve!monitor
PROXMOX_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Discord
NOTIFICATION_TYPE=discord
NOTIFICATION_URL=https://discord.com/api/webhooks/VOTRE_WEBHOOK_URL

# Paramètres
CHECK_INTERVAL=60
DAILY_REPORT_TIME=09:00
TZ=Europe/Paris
```

Ou éditez directement `docker-compose.yml`.

### 5. Lancer

```bash
# Créer le dossier de données
mkdir -p data

# Lancer le conteneur
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

Vous devriez recevoir immédiatement un rapport sur Discord ! 🎉

---

## 📱 Types de notifications

### 🆕 Nouvelle machine créée

```
🆕 Nouvelle machine détectée!

Nom: ubuntu-server
Type: VM
VMID: 102
Nœud: pve
État: running
IP: 192.168.1.150
```

### ✅ Machine démarrée

```
✅ Machine démarrée!

Nom: debian-lxc
Type: LXC
État: running
IP: 192.168.1.151
```

### 📊 Rapport quotidien

```
📊 Rapport quotidien Proxmox

🖥️ Machines Virtuelles:
✅ ubuntu-server - 192.168.1.150 (running)
✅ windows-10 - 192.168.1.151 (running)
⭕ test-vm - N/A (stopped)

📦 Conteneurs LXC:
✅ debian-lxc - 192.168.1.152 (running)
✅ docker-host - 192.168.1.153 (running)

📈 Total: 5 machines (4 up, 1 down)
```

---

## ⚙️ Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `PROXMOX_HOST` | URL de Proxmox | `https://proxmox.local:8006` |
| `PROXMOX_USER` | Utilisateur Proxmox | `root@pam` |
| `PROXMOX_PASSWORD` | Mot de passe | - |
| `PROXMOX_TOKEN_ID` | Token API (recommandé) | - |
| `PROXMOX_TOKEN_SECRET` | Secret du token | - |
| `NOTIFICATION_TYPE` | Type de notification | `discord` |
| `NOTIFICATION_URL` | URL du webhook Discord | - |
| `CHECK_INTERVAL` | Intervalle de vérification (secondes) | `60` |
| `DAILY_REPORT_TIME` | Heure du rapport quotidien (HH:MM) | `09:00` |
| `TZ` | Fuseau horaire | `Europe/Paris` |

### Autres types de notifications supportés

En plus de Discord, le script supporte :

- **Gotify** (auto-hébergé)
- **ntfy** (auto-hébergé ou cloud)
- **Webhook personnalisé** (pour Home Assistant, etc.)

Voir la [documentation complète](ADVANCED.md) pour plus de détails.

---

## 🌐 Récupération des adresses IP

### Pour les VM (machines virtuelles)

Installez **QEMU Guest Agent** dans chaque VM :

```bash
# Debian/Ubuntu
sudo apt install qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent

# CentOS/Rocky Linux
sudo yum install qemu-guest-agent
sudo systemctl enable --now qemu-guest-agent

# Windows
# Télécharger et installer virtio-win-guest-tools.exe
```

Puis dans Proxmox :
1. VM → **Options** → **QEMU Guest Agent**
2. Cochez **Use QEMU Guest Agent**
3. Redémarrez la VM

### Pour les LXC (conteneurs)

**Aucune configuration nécessaire !** L'IP est détectée automatiquement. 🎉

---

## 🔧 Commandes utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Redémarrer le monitoring
docker-compose restart

# Forcer l'envoi d'un rapport maintenant
docker-compose restart

# Arrêter
docker-compose stop

# Démarrer
docker-compose start

# Voir l'état
docker-compose ps

# Voir les fichiers générés
ls -lh data/

# Voir l'état des machines
cat data/machines_state.json
```

---

## 📂 Structure du projet

```
proxmox-monitor/
├── proxmox_monitor.py      # Script Python principal
├── Dockerfile              # Configuration Docker
├── docker-compose.yml      # Orchestration Docker
├── requirements.txt        # Dépendances Python
├── .env.example           # Exemple de configuration
├── install.sh             # Script d'installation interactif
├── test_discord.sh        # Script de test du webhook
├── data/                  # Données persistantes (créé automatiquement)
│   ├── machines_state.json
│   └── proxmox_monitor.log
├── README.md              # Ce fichier
├── PROXMOX_SETUP.md       # Guide configuration Proxmox
├── DISCORD_SETUP.md       # Guide configuration Discord
├── ADVANCED.md            # Fonctionnalités avancées
└── QUICK_START.md         # Guide de démarrage rapide
```

---

## 🐛 Dépannage

### Le conteneur ne démarre pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier la configuration
cat docker-compose.yml
```

### Erreur d'authentification Proxmox

- Vérifiez l'URL de Proxmox (doit inclure `https://` et `:8006`)
- Vérifiez le token API ou le mot de passe
- Testez la connexion : `curl -k https://VOTRE-IP-PROXMOX:8006`

### IP affichée "N/A"

**Pour les VM :**
- Installez QEMU Guest Agent dans la VM
- Activez-le dans Proxmox (Options → QEMU Guest Agent)
- Attendez 30-60 secondes

**Pour les LXC :**
- L'IP devrait être détectée automatiquement
- Vérifiez que le conteneur est bien démarré

### Pas de notifications Discord

- Vérifiez que l'URL du webhook est correcte
- Testez le webhook : `./test_discord.sh`
- Vérifiez les logs : `docker-compose logs -f`

---

## 🔒 Sécurité

- ✅ Utilisez de préférence un **token API** plutôt qu'un mot de passe
- ✅ Le token a des **permissions en lecture seule** (PVEAuditor)
- ✅ Le script **désactive la vérification SSL** pour Proxmox (certificats auto-signés)
- ✅ Ne partagez **jamais** votre webhook Discord ou token API
- ✅ Ajoutez `.env` dans `.gitignore` si vous versionnez votre config

---

## 🚀 Utilisation avancée

### Filtrer certaines machines

Éditez `proxmox_monitor.py` pour filtrer par nom, type, ou nœud :

```python
# Ligne ~210, dans check_for_changes()
import re
pattern = re.compile(r'^(prod|staging)-.*')
current_machines = [m for m in current_machines if pattern.match(m['name'])]
```

### Plusieurs serveurs Proxmox

Créez plusieurs services dans `docker-compose.yml` :

```yaml
services:
  proxmox-monitor-pve1:
    build: .
    env_file: .env.pve1
    volumes:
      - ./data/pve1:/data
  
  proxmox-monitor-pve2:
    build: .
    env_file: .env.pve2
    volumes:
      - ./data/pve2:/data
```

Voir [ADVANCED.md](ADVANCED.md) pour plus d'exemples.

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -am 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

---

## 📝 TODO / Roadmap

- [ ] Support Telegram
- [ ] Support Slack
- [ ] Interface web de visualisation
- [ ] Alertes sur l'utilisation des ressources (CPU/RAM)
- [ ] Intégration Home Assistant
- [ ] Support des snapshots automatiques
- [ ] Notifications par email
- [ ] Grafana dashboard

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [Proxmox VE](https://www.proxmox.com/) - La meilleure plateforme de virtualisation open-source
- [Discord](https://discord.com/) - Pour les webhooks gratuits
- [Docker](https://www.docker.com/) - Pour la conteneurisation

---

## 📧 Support

- 🐛 **Issues** : [GitHub Issues](https://github.com/VOTRE-USERNAME/proxmox-monitor/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/VOTRE-USERNAME/proxmox-monitor/discussions)
- 📖 **Documentation** : [Wiki](https://github.com/VOTRE-USERNAME/proxmox-monitor/wiki)

---

## ⭐ Star History

Si ce projet vous aide, n'oubliez pas de mettre une ⭐ !

[![Star History Chart](https://api.star-history.com/svg?repos=VOTRE-USERNAME/proxmox-monitor&type=Date)](https://star-history.com/#VOTRE-USERNAME/proxmox-monitor&Date)

---

## 📊 Statistiques

![GitHub last commit](https://img.shields.io/github/last-commit/VOTRE-USERNAME/proxmox-monitor)
![GitHub issues](https://img.shields.io/github/issues/VOTRE-USERNAME/proxmox-monitor)
![GitHub pull requests](https://img.shields.io/github/issues-pr/VOTRE-USERNAME/proxmox-monitor)
![Docker Pulls](https://img.shields.io/docker/pulls/VOTRE-USERNAME/proxmox-monitor)

---

<div align="center">
  Fait avec ❤️ pour la communauté Homelab
  
  [⬆ Retour en haut](#-proxmox-monitor---monitoring-léger-avec-notifications-discord)
</div>
