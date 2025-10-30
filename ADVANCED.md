# Exemples et configurations avancées

## 🎨 Personnalisation des notifications

### Modifier les messages de notification

Éditez le fichier `proxmox_monitor.py` pour personnaliser les messages :

```python
# Ligne ~216 - Notification nouvelle machine
message = (
    f"🆕 Nouvelle machine détectée!\n\n"
    f"Nom: {machine['name']}\n"
    f"Type: {machine['type']}\n"
    f"VMID: {machine['vmid']}\n"
    f"Nœud: {machine['node']}\n"
    f"État: {machine['status']}\n"
    f"IP: {machine['ip']}"
)
```

### Ajouter des emojis personnalisés

```python
# Selon le type de machine
if machine['type'] == 'VM':
    icon = "🖥️"
elif machine['type'] == 'LXC':
    icon = "📦"

message = f"{icon} {machine['name']} - {machine['ip']}"
```

## 🔔 Intégrations avec d'autres services

### Home Assistant

Créez un webhook dans Home Assistant :

```yaml
# configuration.yaml
automation:
  - alias: "Proxmox Machine Created"
    trigger:
      platform: webhook
      webhook_id: proxmox_alert
      allowed_methods:
        - POST
    action:
      - service: notify.mobile_app_votre_telephone
        data:
          title: "{{ trigger.json.title }}"
          message: "{{ trigger.json.message }}"
          data:
            priority: high
            tag: proxmox
            
      - service: persistent_notification.create
        data:
          title: "{{ trigger.json.title }}"
          message: "{{ trigger.json.message }}"
```

Configuration du monitoring :
```env
NOTIFICATION_TYPE=webhook
NOTIFICATION_URL=http://homeassistant.local:8123/api/webhook/proxmox_alert
```

### Discord

Créez un webhook Discord et utilisez cette configuration :

```python
# Modification du send_notification pour Discord
def send_notification_discord(self, title, message, priority="normal"):
    """Envoie une notification sur Discord"""
    color_map = {"low": 0x00ff00, "normal": 0x0099ff, "high": 0xff0000}
    
    embed = {
        "title": title,
        "description": message,
        "color": color_map.get(priority, 0x0099ff),
        "timestamp": datetime.now().isoformat()
    }
    
    payload = {"embeds": [embed]}
    response = requests.post(self.notification_url, json=payload)
```

### Telegram

Pour utiliser Telegram :

```python
def send_notification_telegram(self, title, message, priority="normal"):
    """Envoie une notification sur Telegram"""
    text = f"*{title}*\n\n{message}"
    params = {
        "chat_id": self.telegram_chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
    response = requests.post(url, params=params)
```

Configuration :
```env
NOTIFICATION_TYPE=telegram
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=your_chat_id
```

## 📊 Filtrage et alertes personnalisées

### Surveiller uniquement certaines machines

Modifiez la méthode `check_for_changes` :

```python
def check_for_changes(self):
    # ...
    current_machines = self.get_all_machines()
    
    # Filtrer par nom (regex)
    import re
    pattern = re.compile(r'^(prod|staging)-.*')
    current_machines = [m for m in current_machines if pattern.match(m['name'])]
    
    # Ou filtrer par type
    current_machines = [m for m in current_machines if m['type'] == 'LXC']
    
    # Ou filtrer par nœud
    current_machines = [m for m in current_machines if m['node'] == 'pve']
```

### Alertes sur l'utilisation des ressources

Ajoutez cette méthode pour surveiller l'utilisation :

```python
def check_resource_usage(self, node, vmid, vm_type):
    """Vérifie l'utilisation des ressources"""
    try:
        status_url = f"{self.proxmox_host}/api2/json/nodes/{node}/{vm_type}/{vmid}/status/current"
        response = self.session.get(status_url)
        
        if response.status_code == 200:
            data = response.json()['data']
            
            # Exemple : Alerter si CPU > 80%
            if data.get('cpu', 0) > 0.8:
                return f"⚠️ CPU élevé : {data['cpu']*100:.1f}%"
            
            # Exemple : Alerter si RAM > 90%
            if data.get('mem', 0) / data.get('maxmem', 1) > 0.9:
                mem_percent = (data['mem'] / data['maxmem']) * 100
                return f"⚠️ RAM élevée : {mem_percent:.1f}%"
        
        return None
    except:
        return None
```

### Alertes sur les backups

```python
def check_backups(self):
    """Vérifie l'état des derniers backups"""
    try:
        backup_url = f"{self.proxmox_host}/api2/json/cluster/backup"
        response = self.session.get(backup_url)
        
        if response.status_code == 200:
            backups = response.json()['data']
            
            # Vérifier les backups de moins de 24h
            from datetime import timedelta
            yesterday = datetime.now() - timedelta(days=1)
            
            for backup in backups:
                if backup.get('enabled', 0):
                    # Logique de vérification
                    pass
    except Exception as e:
        logging.error(f"Erreur vérification backups: {e}")
```

## 🔄 Automatisations avancées

### Démarrage automatique en cas d'arrêt inattendu

```python
def auto_start_machines(self, machines_to_monitor):
    """Démarre automatiquement certaines machines si arrêtées"""
    for machine in machines_to_monitor:
        if machine['status'] == 'stopped' and machine['name'] in ['critical-vm', 'prod-server']:
            self.start_machine(machine['node'], machine['vmid'], machine['type'])
            self.send_notification(
                "Auto-démarrage",
                f"Machine {machine['name']} redémarrée automatiquement",
                "high"
            )

def start_machine(self, node, vmid, vm_type):
    """Démarre une machine"""
    try:
        start_url = f"{self.proxmox_host}/api2/json/nodes/{node}/{vm_type}/{vmid}/status/start"
        response = self.session.post(start_url)
        response.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Erreur démarrage machine {vmid}: {e}")
        return False
```

### Snapshots automatiques avant démarrage

```python
def create_snapshot_before_start(self, node, vmid, vm_type):
    """Crée un snapshot avant de démarrer"""
    try:
        snapshot_name = f"auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        snapshot_url = f"{self.proxmox_host}/api2/json/nodes/{node}/{vm_type}/{vmid}/snapshot"
        
        data = {
            'snapname': snapshot_name,
            'description': 'Snapshot automatique avant démarrage'
        }
        
        response = self.session.post(snapshot_url, data=data)
        response.raise_for_status()
        
        logging.info(f"Snapshot créé: {snapshot_name}")
        return True
    except Exception as e:
        logging.error(f"Erreur création snapshot: {e}")
        return False
```

## 📈 Statistiques et rapports

### Rapport hebdomadaire détaillé

```python
def send_weekly_report(self):
    """Envoie un rapport hebdomadaire détaillé"""
    if not self.authenticate():
        return
    
    machines = self.get_all_machines()
    
    # Statistiques
    total_vms = len([m for m in machines if m['type'] == 'VM'])
    total_lxc = len([m for m in machines if m['type'] == 'LXC'])
    running = len([m for m in machines if m['status'] == 'running'])
    stopped = len([m for m in machines if m['status'] == 'stopped'])
    
    # Uptime moyen (à implémenter)
    # Nouvelles machines cette semaine (à implémenter)
    
    report = f"""
📊 Rapport Hebdomadaire Proxmox

🖥️ Machines Virtuelles: {total_vms}
📦 Conteneurs LXC: {total_lxc}
✅ En fonctionnement: {running}
⭕ Arrêtées: {stopped}

📈 Total: {len(machines)} machines
    """
    
    self.send_notification("Rapport Hebdomadaire", report, "low")

# Dans la méthode run(), ajouter :
schedule.every().monday.at("09:00").do(self.send_weekly_report)
```

### Export des données

```python
def export_to_csv(self):
    """Exporte l'état des machines en CSV"""
    import csv
    
    machines = self.get_all_machines()
    
    with open('/data/machines_export.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'type', 'status', 'ip', 'node', 'vmid'])
        writer.writeheader()
        writer.writerows(machines)
    
    logging.info("Export CSV créé")
```

## 🐳 Configurations Docker avancées

### Utilisation du réseau host (pour meilleure découverte)

```yaml
# docker-compose.yml
services:
  proxmox-monitor:
    network_mode: "host"
    environment:
      PROXMOX_HOST: "https://127.0.0.1:8006"  # Si Proxmox sur la même machine
```

### Multi-instances (plusieurs serveurs Proxmox)

Créez plusieurs services dans `docker-compose.yml` :

```yaml
version: '3.8'

services:
  proxmox-monitor-pve1:
    build: .
    container_name: proxmox-monitor-pve1
    env_file: .env.pve1
    volumes:
      - ./data/pve1:/data
  
  proxmox-monitor-pve2:
    build: .
    container_name: proxmox-monitor-pve2
    env_file: .env.pve2
    volumes:
      - ./data/pve2:/data
```

### Healthcheck Docker

```yaml
services:
  proxmox-monitor:
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 🔍 Debugging et logs avancés

### Mode debug

Ajoutez dans `.env` :
```env
LOG_LEVEL=DEBUG
```

Et dans le code :
```python
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level))
```

### Logs structurés (JSON)

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        }
        return json.dumps(log_obj)

handler = logging.FileHandler('/data/proxmox_monitor.json')
handler.setFormatter(JsonFormatter())
logging.getLogger().addHandler(handler)
```

## 🚀 Performance et optimisation

### Cache des résultats API

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedProxmoxMonitor(ProxmoxMonitor):
    def __init__(self):
        super().__init__()
        self.cache = {}
        self.cache_duration = 30  # secondes
    
    def get_all_machines_cached(self):
        now = datetime.now()
        if 'machines' in self.cache:
            cached_time, machines = self.cache['machines']
            if (now - cached_time).seconds < self.cache_duration:
                return machines
        
        machines = self.get_all_machines()
        self.cache['machines'] = (now, machines)
        return machines
```

### Traitement asynchrone

```python
import asyncio
import aiohttp

async def get_machine_ip_async(self, node, vmid, vm_type):
    """Version asynchrone de get_machine_ip"""
    # Implémentation avec aiohttp
    pass
```

## 📱 Interface Web légère (Bonus)

Créez un fichier `web_dashboard.py` pour voir l'état en temps réel :

```python
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/api/machines')
def get_machines():
    with open('/data/machines_state.json', 'r') as f:
        machines = json.load(f)
    return jsonify(machines)

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Ajoutez Flask dans `requirements.txt` et exposez le port dans Docker.

---

Ces exemples vous donnent une base pour étendre le monitoring selon vos besoins spécifiques !
