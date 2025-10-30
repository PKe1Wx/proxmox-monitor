# 🎮 Configuration Discord Webhook

## Création du webhook Discord

### Étape 1 : Créer le webhook sur Discord

1. **Ouvrez Discord** et allez sur votre serveur
2. **Clic droit** sur le canal où vous voulez recevoir les notifications (ex: #proxmox-alerts)
3. Cliquez sur **Modifier le salon**
4. Dans le menu de gauche, allez sur **Intégrations**
5. Cliquez sur **Webhooks** puis **Nouveau Webhook**
6. Personnalisez votre webhook :
   - Nom : `Proxmox Monitor`
   - Avatar : (optionnel, vous pouvez mettre une image)
7. **Copiez l'URL du webhook** (bouton "Copier l'URL du Webhook")
   - Format : `https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz1234567890`

⚠️ **IMPORTANT** : Ne partagez JAMAIS cette URL, c'est comme un mot de passe !

### Étape 2 : Configuration du monitoring

#### Option A : Avec le script d'installation

Quand `install.sh` vous demande le type de notification :
```
Configuration des notifications:
1) Discord
2) Gotify
3) ntfy
4) Webhook
Votre choix (1, 2, 3 ou 4): 1

URL du webhook Discord: https://discord.com/api/webhooks/VOTRE_URL_ICI
```

#### Option B : Configuration manuelle

Éditez le fichier `docker-compose.yml` :

```yaml
environment:
  # ...
  NOTIFICATION_TYPE: "discord"
  NOTIFICATION_URL: "https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz1234567890"
  NOTIFICATION_TOKEN: ""  # Laissez vide pour Discord
```

Ou créez/éditez le fichier `.env` :

```env
NOTIFICATION_TYPE=discord
NOTIFICATION_URL=https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz1234567890
NOTIFICATION_TOKEN=
```

## 📱 À quoi ressemblent les notifications

### Nouvelle machine détectée
```
[Embed Discord avec couleur ROUGE]
Titre : Nouvelle machine: ubuntu-server

🆕 Nouvelle machine détectée!

Nom: ubuntu-server
Type: VM
VMID: 102
Nœud: pve
État: running
IP: 192.168.1.150

Footer: Proxmox Monitor | Timestamp
```

### Machine démarrée
```
[Embed Discord avec couleur BLEUE]
Titre : Machine démarrée: debian-lxc

✅ Machine démarrée!

Nom: debian-lxc
Type: LXC
État: running
IP: 192.168.1.151

Footer: Proxmox Monitor | Timestamp
```

### Rapport quotidien
```
[Embed Discord avec couleur VERTE]
Titre : Rapport quotidien Proxmox

📊 Rapport quotidien Proxmox

🖥️ Machines Virtuelles:
✅ ubuntu-server - 192.168.1.150 (running)
⭕ test-vm - N/A (stopped)

📦 Conteneurs LXC:
✅ debian-lxc - 192.168.1.152 (running)

📈 Total: 3 machines (2 up, 1 down)

Footer: Proxmox Monitor | Timestamp
```

## 🎨 Personnalisation

### Changer les couleurs des embeds

Éditez `proxmox_monitor.py`, ligne ~154 :

```python
color_map = {
    "low": 3066993,      # Vert   (#2ECC71)
    "normal": 3447003,   # Bleu   (#3498DB)
    "high": 15158332     # Rouge  (#E74C3C)
}
```

Autres couleurs populaires :
- Orange : `16744448` (#FF8C00)
- Violet : `10181046` (#9B59B6)
- Jaune : `16776960` (#FFFF00)
- Noir : `2303786` (#23272A)

### Changer le nom d'utilisateur et l'avatar

Dans `proxmox_monitor.py`, ligne ~164 :

```python
payload = {
    "embeds": [embed],
    "username": "Proxmox Monitor",      # Changez le nom ici
    "avatar_url": "https://votre-image.png"  # Ajoutez une image
}
```

### Ajouter des champs dans les embeds

```python
embed = {
    "title": title,
    "description": message,
    "color": color_map.get(priority, 3447003),
    "timestamp": datetime.now().isoformat(),
    "fields": [
        {
            "name": "Nœud",
            "value": machine['node'],
            "inline": True
        },
        {
            "name": "VMID",
            "value": str(machine['vmid']),
            "inline": True
        }
    ],
    "footer": {
        "text": "Proxmox Monitor",
        "icon_url": "https://www.proxmox.com/images/proxmox/Proxmox_logo_standard_hex_400px.png"
    },
    "thumbnail": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/92/Proxmox-logo-860.png"
    }
}
```

## 🔔 Gestion des mentions

### Mentionner @everyone ou un rôle

Pour les alertes importantes (exemple : machine critique down) :

```python
payload = {
    "content": "@everyone Alerte importante !",  # ou "@here" ou "<@&ROLE_ID>"
    "embeds": [embed],
    "username": "Proxmox Monitor"
}
```

⚠️ **Attention** : Vérifiez que le webhook a la permission de mentionner @everyone

### Mentionner un utilisateur spécifique

```python
payload = {
    "content": "<@USER_ID> Ta machine vient de démarrer",
    "embeds": [embed]
}
```

## 🧪 Tester votre webhook

### Test avec curl

```bash
curl -X POST "https://discord.com/api/webhooks/VOTRE_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "embeds": [{
      "title": "Test Proxmox Monitor",
      "description": "Ceci est un test de notification",
      "color": 3447003
    }]
  }'
```

### Test depuis Python

```python
import requests
from datetime import datetime

webhook_url = "https://discord.com/api/webhooks/VOTRE_URL"

payload = {
    "embeds": [{
        "title": "🧪 Test de notification",
        "description": "Si vous voyez ce message, le webhook fonctionne !",
        "color": 3447003,
        "timestamp": datetime.now().isoformat(),
        "footer": {"text": "Proxmox Monitor"}
    }],
    "username": "Proxmox Monitor"
}

response = requests.post(webhook_url, json=payload)
print(f"Status: {response.status_code}")
```

## 🔒 Sécurité

### ⚠️ Bonnes pratiques

1. **Ne commitez JAMAIS votre webhook URL** dans Git
2. **Ajoutez `.env` dans `.gitignore`** si vous versionnez le projet
3. **Utilisez des variables d'environnement** (c'est déjà fait dans ce projet)
4. **Créez un canal dédié** pour les notifications (ex: #proxmox-alerts)
5. **Limitez les permissions du canal** si nécessaire

### Régénérer un webhook compromis

Si votre URL de webhook a fuité :

1. Retournez dans Discord → Modifier le salon → Intégrations → Webhooks
2. Cliquez sur votre webhook
3. Cliquez sur **Supprimer le Webhook**
4. Créez-en un nouveau
5. Mettez à jour votre configuration et redémarrez le conteneur

## 🐛 Dépannage

### Les notifications n'arrivent pas

1. **Vérifiez l'URL du webhook**
   ```bash
   # Regardez les logs
   docker-compose logs -f
   
   # Vous devriez voir "Notification envoyée" ou une erreur
   ```

2. **Testez le webhook manuellement** (voir section Test ci-dessus)

3. **Vérifiez que Discord n'est pas en maintenance**

4. **Vérifiez les permissions du webhook dans Discord**

### Erreur 404 - Webhook not found

- L'URL du webhook est incorrecte
- Le webhook a été supprimé sur Discord
- Vérifiez qu'il n'y a pas d'espaces ou de caractères invisibles dans l'URL

### Erreur 429 - Rate limit

Discord limite à ~30 messages par minute par webhook. Si vous avez beaucoup de machines qui démarrent en même temps, attendez quelques secondes entre les notifications.

Solution dans le code :
```python
import time

def send_notification(self, title, message, priority="normal"):
    # ... votre code ...
    response = requests.post(self.notification_url, json=payload)
    response.raise_for_status()
    
    # Pause de 1 seconde entre les notifications
    time.sleep(1)
```

### Les embeds ne s'affichent pas correctement

- Vérifiez que vous envoyez bien un tableau `"embeds": [...]` et non un objet
- Vérifiez le format JSON (utilisez un validateur JSON en ligne)
- Les couleurs doivent être des entiers décimaux, pas des hex strings

## 📚 Ressources

- [Documentation officielle Discord Webhooks](https://discord.com/developers/docs/resources/webhook)
- [Discord Embed Visualizer](https://leovoel.github.io/embed-visualizer/) - Pour tester vos embeds
- [Générateur de couleurs Discord](https://www.spycolor.com/) - Convertir hex en décimal

---

Besoin d'aide ? Vérifiez les logs avec `docker-compose logs -f` ! 🚀
