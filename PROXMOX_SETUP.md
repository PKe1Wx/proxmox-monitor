# Guide de configuration Proxmox

## 🔐 Création d'un utilisateur dédié (Méthode recommandée)

### Méthode 1 : Via l'interface Web Proxmox

1. **Créer un utilisateur**
   - Allez dans `Datacenter` → `Permissions` → `Users`
   - Cliquez sur `Add`
   - User name: `monitoring`
   - Realm: `Proxmox VE authentication server` (pve)
   - Laissez le mot de passe vide (on utilisera un token)

2. **Créer un rôle personnalisé** (optionnel, pour plus de sécurité)
   - Allez dans `Datacenter` → `Permissions` → `Roles`
   - Cliquez sur `Create`
   - Name: `Monitoring`
   - Privilèges à cocher :
     - `VM.Audit` - Voir les VM
     - `Datastore.Audit` - Voir les datastores
     - `Sys.Audit` - Voir les informations système

3. **Attribuer les permissions**
   - Allez dans `Datacenter` → `Permissions`
   - Cliquez sur `Add` → `User Permission`
   - Path: `/`
   - User: `monitoring@pve`
   - Role: `PVEAuditor` (ou votre rôle custom `Monitoring`)

4. **Créer un token API**
   - Allez dans `Datacenter` → `Permissions` → `API Tokens`
   - Cliquez sur `Add`
   - User: `monitoring@pve`
   - Token ID: `monitor`
   - Décochez `Privilege Separation` (pour hériter des permissions de l'utilisateur)
   - Cliquez sur `Add`
   - **⚠️ IMPORTANT** : Copiez le token secret immédiatement, il ne sera plus affiché !

### Méthode 2 : Via la ligne de commande (SSH sur Proxmox)

```bash
# Se connecter en SSH sur votre serveur Proxmox

# Créer l'utilisateur
pveum user add monitoring@pve --comment "Monitoring user for alerts"

# Attribuer le rôle PVEAuditor (lecture seule)
pveum aclmod / -user monitoring@pve -role PVEAuditor

# Créer un token API
pveum user token add monitoring@pve monitor -privsep 0

# La sortie affichera quelque chose comme :
# ┌──────────────┬──────────────────────────────────────┐
# │ key          │ value                                │
# ╞══════════════╪══════════════════════════════════════╡
# │ full-tokenid │ monitoring@pve!monitor               │
# ├──────────────┼──────────────────────────────────────┤
# │ info         │ {"privsep":"0"}                      │
# ├──────────────┼──────────────────────────────────────┤
# │ value        │ xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx │
# └──────────────┴──────────────────────────────────────┘

# Sauvegardez le 'value' du token !
```

## 📝 Configuration dans le script

Après avoir créé le token, ajoutez-le dans votre fichier `.env` :

```env
PROXMOX_HOST=https://192.168.1.100:8006
PROXMOX_TOKEN_ID=monitoring@pve!monitor
PROXMOX_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Ou dans le `docker-compose.yml` :

```yaml
environment:
  PROXMOX_HOST: "https://192.168.1.100:8006"
  PROXMOX_TOKEN_ID: "monitoring@pve!monitor"
  PROXMOX_TOKEN_SECRET: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

## 🔧 Installation de QEMU Guest Agent

Pour que le script puisse récupérer les adresses IP des VM, installez l'agent QEMU dans chaque VM :

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install qemu-guest-agent
sudo systemctl enable qemu-guest-agent
sudo systemctl start qemu-guest-agent
```

### CentOS / Rocky Linux / AlmaLinux

```bash
sudo yum install qemu-guest-agent
sudo systemctl enable qemu-guest-agent
sudo systemctl start qemu-guest-agent
```

### Fedora

```bash
sudo dnf install qemu-guest-agent
sudo systemctl enable qemu-guest-agent
sudo systemctl start qemu-guest-agent
```

### Windows

1. Téléchargez les drivers VirtIO depuis : https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/
2. Installez `qemu-ga-x64.msi` ou `qemu-ga-x86.msi`
3. Le service démarre automatiquement

### Activer l'agent dans Proxmox

Après installation dans la VM :

**Via l'interface Web :**
1. Sélectionnez votre VM
2. Allez dans `Options`
3. Double-cliquez sur `QEMU Guest Agent`
4. Cochez `Use QEMU Guest Agent`
5. Cliquez sur `OK`
6. Redémarrez la VM

**Via CLI :**
```bash
qm set <vmid> --agent enabled=1
```

## 🐧 Conteneurs LXC

Pour les conteneurs LXC, l'IP est récupérée automatiquement via l'interface réseau. Aucune configuration supplémentaire n'est nécessaire.

## 🧪 Test de la configuration

### Vérifier la connexion à l'API Proxmox

```bash
# Remplacez les valeurs par les vôtres
curl -k -H "Authorization: PVEAPIToken=monitoring@pve!monitor=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  https://192.168.1.100:8006/api2/json/version
```

Si la connexion fonctionne, vous devriez voir la version de Proxmox en JSON.

### Tester depuis le conteneur Docker

```bash
# Démarrer le conteneur
docker-compose up -d

# Voir les logs en temps réel
docker-compose logs -f

# Vous devriez voir :
# - "Authentification réussie"
# - La liste des machines détectées
# - Le rapport quotidien envoyé
```

## 🔐 Sécurité

### Bonnes pratiques

1. **Utilisez toujours un token API** plutôt qu'un mot de passe
2. **Permissions minimales** : Le rôle `PVEAuditor` est suffisant (lecture seule)
3. **Ne partagez jamais** vos tokens
4. **Rotation des tokens** : Changez régulièrement vos tokens API
5. **Réseau sécurisé** : Assurez-vous que votre Raspberry Pi est sur un réseau de confiance

### Révoquer un token

Si vous pensez qu'un token a été compromis :

**Via l'interface Web :**
1. `Datacenter` → `Permissions` → `API Tokens`
2. Sélectionnez le token
3. Cliquez sur `Remove`

**Via CLI :**
```bash
pveum user token remove monitoring@pve monitor
```

Puis créez un nouveau token et mettez à jour votre configuration.

## 📊 Permissions détaillées

Le rôle `PVEAuditor` inclut les permissions suivantes (lecture seule) :

- `Datastore.Audit` : Voir les datastores
- `Pool.Audit` : Voir les pools
- `SDN.Audit` : Voir la configuration SDN
- `Sys.Audit` : Voir les informations système
- `VM.Audit` : Voir les VM et conteneurs

Ces permissions sont parfaites pour un monitoring non-intrusif.

## 🌐 Configuration réseau

### Firewall Proxmox

Si le firewall est activé sur Proxmox, assurez-vous d'autoriser les connexions depuis votre Raspberry Pi :

1. `Datacenter` → `Firewall` → `Add`
2. Direction: `in`
3. Action: `ACCEPT`
4. Protocol: `tcp`
5. Dest. port: `8006`
6. Source: IP de votre Raspberry Pi

### Certificat SSL auto-signé

Le script désactive automatiquement la vérification SSL, ce qui est normal pour Proxmox avec un certificat auto-signé.

Si vous voulez utiliser un vrai certificat :
1. Installez Let's Encrypt sur Proxmox
2. Ou importez votre propre certificat dans Proxmox

## ❓ Problèmes courants

### "Connection refused"
- Vérifiez que vous pouvez accéder à l'interface Web Proxmox depuis votre Raspberry Pi
- Vérifiez l'URL (doit être `https://` et inclure le port `:8006`)

### "Authentication failed"
- Vérifiez le token ID et secret
- Vérifiez que le token n'a pas été révoqué
- Vérifiez que l'utilisateur existe et a les bonnes permissions

### IP affichée "N/A"
- Pour les VM : installez et activez qemu-guest-agent
- Pour les LXC : vérifiez que le conteneur est bien démarré
- Attendez quelques secondes après le démarrage pour que l'IP soit détectée

### "Permission denied"
- Vérifiez que le rôle `PVEAuditor` est bien attribué
- Vérifiez que `-privsep 0` a été utilisé lors de la création du token
