# 🚀 Guide d'installation RAPIDE - Discord pré-configuré

Votre webhook Discord est déjà intégré dans les fichiers ! Il ne vous reste plus qu'à configurer Proxmox.

## ⚡ Installation en 5 minutes

### 1️⃣ Sur Proxmox (créer le token API)

Connectez-vous en SSH à votre serveur Proxmox :

```bash
ssh root@IP-DE-PROXMOX

# Créer l'utilisateur de monitoring
pveum user add monitoring@pve

# Donner les droits de lecture
pveum aclmod / -user monitoring@pve -role PVEAuditor

# Créer le token API
pveum user token add monitoring@pve monitor -privsep 0
```

**📝 IMPORTANT** : Notez le token secret affiché (vous ne le reverrez plus) !

Exemple de sortie :
```
┌──────────────┬──────────────────────────────────────┐
│ key          │ value                                │
├──────────────┼──────────────────────────────────────┤
│ full-tokenid │ monitoring@pve!monitor               │
│ value        │ xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx │ ← NOTEZ CECI !
└──────────────┴──────────────────────────────────────┘
```

---

### 2️⃣ Sur votre Raspberry Pi

```bash
# Connectez-vous en SSH
ssh pi@IP-DE-VOTRE-RPI

# Créez et allez dans le dossier
mkdir ~/proxmox-monitor
cd ~/proxmox-monitor

# Transférez l'archive ici (via scp, wget, clé USB, etc.)
# Si vous utilisez scp depuis votre PC :
# scp proxmox-monitor-discord.tar.gz pi@IP-RPI:/home/pi/proxmox-monitor/

# Extrayez l'archive
tar -xzf proxmox-monitor-discord.tar.gz

# Éditez le fichier de configuration
nano docker-compose.yml
```

---

### 3️⃣ Modifiez UNIQUEMENT ces 3 lignes dans docker-compose.yml

Cherchez la section `environment:` et modifiez :

```yaml
      # Configuration Proxmox
      PROXMOX_HOST: "https://IP-DE-PROXMOX:8006"  # ← Changez l'IP
      # PROXMOX_USER: "root@pam"  # ← Laissez commenté
      # PROXMOX_PASSWORD: "votre_mot_de_passe"  # ← Laissez commenté
      
      # Utilisez le token API (recommandé)
      PROXMOX_TOKEN_ID: "monitoring@pve!monitor"  # ← Laissez tel quel
      PROXMOX_TOKEN_SECRET: "COLLEZ-VOTRE-TOKEN-ICI"  # ← Collez le token de l'étape 1
```

**Discord est déjà configuré**, vous n'avez rien à changer dans cette section !

Sauvegardez : `Ctrl+O` puis `Entrée`, puis quittez : `Ctrl+X`

---

### 4️⃣ Lancez le conteneur

```bash
# Créez le dossier de données
mkdir -p data

# Lancez !
docker-compose up -d

# Vérifiez les logs
docker-compose logs -f
```

Vous devriez voir :
```
✓ Démarrage du monitoring Proxmox
✓ Authentification réussie
✓ Rapport quotidien envoyé
```

Et sur Discord, vous recevrez immédiatement le premier rapport ! 🎉

---

## 📋 Récapitulatif de ce que vous avez changé

1. **PROXMOX_HOST** : `https://192.168.1.XXX:8006` (votre IP Proxmox)
2. **PROXMOX_TOKEN_SECRET** : Le token créé à l'étape 1
3. C'est tout ! 😊

---

## ✅ Vérification

### Dans les logs du conteneur :
```bash
docker-compose logs -f
```

Vous devriez voir :
- `Authentification réussie`
- `Notification envoyée: Rapport quotidien Proxmox`
- Liste de vos machines

### Sur Discord :
Vous devriez recevoir un message avec toutes vos machines actuelles.

---

## 🎯 Ce qui va se passer maintenant

✅ **Nouvelle VM/LXC créée** → Notification instantanée sur Discord  
✅ **Machine démarrée** → Notification sur Discord  
✅ **Tous les jours à 9h** → Rapport complet sur Discord  

---

## 🔧 Commandes utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Redémarrer après un changement de config
docker-compose restart

# Arrêter
docker-compose stop

# Démarrer
docker-compose start

# Supprimer complètement
docker-compose down
```

---

## 🐛 Problèmes courants

### "Authentication failed"
- Vérifiez que le token est correct (sans espaces)
- Vérifiez que l'IP de Proxmox est correcte
- Vérifiez que vous pouvez accéder à Proxmox depuis le RPi : `curl -k https://IP-PROXMOX:8006`

### Pas de notification sur Discord
- Vérifiez les logs : `docker-compose logs`
- Le webhook Discord est déjà configuré, pas besoin de le changer

### IP affichée "N/A"
Pour que les IP soient détectées, installez dans vos VM :
```bash
# Debian/Ubuntu
sudo apt install qemu-guest-agent
sudo systemctl start qemu-guest-agent

# CentOS/Rocky
sudo yum install qemu-guest-agent
sudo systemctl start qemu-guest-agent
```

Puis dans Proxmox, activez l'agent QEMU dans les options de la VM.

---

## 📞 Besoin d'aide ?

Les logs sont votre ami :
```bash
docker-compose logs -f
```

Ils vous diront exactement ce qui se passe (authentification, connexion, notifications, etc.)

---

**Bonne installation ! 🚀**
