#!/usr/bin/env python3
"""
Script de monitoring Proxmox
- Détecte les nouvelles VM/LXC créées
- Vérifie leur état au démarrage
- Envoie un rapport quotidien
"""

import requests
import json
import time
import schedule
from datetime import datetime
from pathlib import Path
import logging
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/data/proxmox_monitor.log'),
        logging.StreamHandler()
    ]
)

class ProxmoxMonitor:
    def __init__(self):
        # Configuration depuis variables d'environnement
        self.proxmox_host = os.getenv('PROXMOX_HOST', 'https://proxmox.local:8006')
        self.proxmox_user = os.getenv('PROXMOX_USER', 'root@pam')
        self.proxmox_password = os.getenv('PROXMOX_PASSWORD', '')
        self.proxmox_token_id = os.getenv('PROXMOX_TOKEN_ID', '')
        self.proxmox_token_secret = os.getenv('PROXMOX_TOKEN_SECRET', '')
        
        # Configuration des notifications
        self.notification_type = os.getenv('NOTIFICATION_TYPE', 'gotify')  # gotify, ntfy, webhook
        self.notification_url = os.getenv('NOTIFICATION_URL', '')
        self.notification_token = os.getenv('NOTIFICATION_TOKEN', '')
        
        # Heure du rapport quotidien (format HH:MM)
        self.daily_report_time = os.getenv('DAILY_REPORT_TIME', '09:00')
        
        # Fichier pour stocker l'état des machines
        self.state_file = '/data/machines_state.json'
        self.machines_state = self.load_state()
        
        # Session requests
        self.session = requests.Session()
        self.session.verify = False  # Désactiver la vérification SSL
        requests.packages.urllib3.disable_warnings()
        
        self.ticket = None
        self.csrf_token = None
    
    def load_state(self):
        """Charge l'état sauvegardé des machines"""
        if Path(self.state_file).exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_state(self):
        """Sauvegarde l'état des machines"""
        with open(self.state_file, 'w') as f:
            json.dump(self.machines_state, f, indent=2)
    
    def authenticate(self):
        """Authentification auprès de Proxmox"""
        # Priorité au token API si disponible
        if self.proxmox_token_id and self.proxmox_token_secret:
            self.session.headers.update({
                'Authorization': f'PVEAPIToken={self.proxmox_token_id}={self.proxmox_token_secret}'
            })
            logging.info("Authentification par token API")
            return True
        
        # Sinon, authentification par mot de passe
        try:
            auth_url = f"{self.proxmox_host}/api2/json/access/ticket"
            data = {
                'username': self.proxmox_user,
                'password': self.proxmox_password
            }
            response = self.session.post(auth_url, data=data)
            response.raise_for_status()
            
            result = response.json()['data']
            self.ticket = result['ticket']
            self.csrf_token = result['CSRFPreventionToken']
            
            self.session.headers.update({
                'Cookie': f'PVEAuthCookie={self.ticket}',
                'CSRFPreventionToken': self.csrf_token
            })
            
            logging.info("Authentification réussie")
            return True
            
        except Exception as e:
            logging.error(f"Erreur d'authentification: {e}")
            return False
    
    def get_all_machines(self):
        """Récupère toutes les VM et LXC de tous les nœuds"""
        all_machines = []
        
        try:
            # Récupérer la liste des nœuds
            nodes_url = f"{self.proxmox_host}/api2/json/nodes"
            response = self.session.get(nodes_url)
            response.raise_for_status()
            nodes = response.json()['data']
            
            for node in nodes:
                node_name = node['node']
                
                # Récupérer les VM (QEMU)
                vms_url = f"{self.proxmox_host}/api2/json/nodes/{node_name}/qemu"
                response = self.session.get(vms_url)
                if response.status_code == 200:
                    vms = response.json()['data']
                    for vm in vms:
                        machine_info = {
                            'id': f"vm-{node_name}-{vm['vmid']}",
                            'vmid': vm['vmid'],
                            'name': vm['name'],
                            'type': 'VM',
                            'node': node_name,
                            'status': vm['status'],
                            'ip': self.get_machine_ip(node_name, vm['vmid'], 'qemu')
                        }
                        all_machines.append(machine_info)
                
                # Récupérer les LXC
                lxcs_url = f"{self.proxmox_host}/api2/json/nodes/{node_name}/lxc"
                response = self.session.get(lxcs_url)
                if response.status_code == 200:
                    lxcs = response.json()['data']
                    for lxc in lxcs:
                        machine_info = {
                            'id': f"lxc-{node_name}-{lxc['vmid']}",
                            'vmid': lxc['vmid'],
                            'name': lxc['name'],
                            'type': 'LXC',
                            'node': node_name,
                            'status': lxc['status'],
                            'ip': self.get_machine_ip(node_name, lxc['vmid'], 'lxc')
                        }
                        all_machines.append(machine_info)
            
            return all_machines
            
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des machines: {e}")
            return []
    
    def update_machine_notes(self, node, vmid, vm_type, machine_info):
        """Met à jour les notes de la machine avec son IP et d'autres infos"""
        try:
            # Construire le texte pour les notes
            notes = f"""Monitoring automatique Proxmox
            
Nom: {machine_info['name']}
Type: {machine_info['type']}
État: {machine_info['status']}
IP: {machine_info['ip']}
Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
Généré automatiquement par Proxmox Monitor
"""
            
            # URL de configuration selon le type
            config_url = f"{self.proxmox_host}/api2/json/nodes/{node}/{vm_type}/{vmid}/config"
            
            # Mettre à jour la description
            data = {'description': notes}
            response = self.session.put(config_url, data=data)
            
            if response.status_code == 200:
                logging.debug(f"Notes mises à jour pour {machine_info['name']} (VMID: {vmid})")
                return True
            else:
                logging.debug(f"Impossible de mettre à jour les notes pour {vmid}: {response.status_code}")
                return False
                
        except Exception as e:
            logging.debug(f"Erreur lors de la mise à jour des notes pour {vmid}: {e}")
            return False
    
    def get_machine_ip(self, node, vmid, vm_type):
        """Récupère l'adresse IP d'une machine"""
        try:
            # Pour les VM, essayer d'abord l'agent QEMU
            if vm_type == 'qemu':
                agent_url = f"{self.proxmox_host}/api2/json/nodes/{node}/qemu/{vmid}/agent/network-get-interfaces"
                response = self.session.get(agent_url)
                
                if response.status_code == 200:
                    data = response.json()['data']['result']
                    for interface in data:
                        if 'ip-addresses' in interface:
                            for ip_info in interface['ip-addresses']:
                                # Ignorer loopback et IPv6 link-local
                                if ip_info['ip-address-type'] == 'ipv4' and not ip_info['ip-address'].startswith('127.'):
                                    return ip_info['ip-address']
                
                # Si l'agent ne fonctionne pas, essayer de récupérer l'IP via la config réseau
                config_url = f"{self.proxmox_host}/api2/json/nodes/{node}/qemu/{vmid}/config"
                response = self.session.get(config_url)
                
                if response.status_code == 200:
                    config = response.json()['data']
                    # Chercher une IP configurée statiquement
                    for key, value in config.items():
                        if key.startswith('ipconfig') and 'ip=' in str(value):
                            # Extraire l'IP de la config
                            import re
                            match = re.search(r'ip=(\d+\.\d+\.\d+\.\d+)', str(value))
                            if match:
                                return match.group(1)
            
            # Pour les LXC, utiliser l'interface réseau
            elif vm_type == 'lxc':
                config_url = f"{self.proxmox_host}/api2/json/nodes/{node}/lxc/{vmid}/interfaces"
                response = self.session.get(config_url)
                
                if response.status_code == 200:
                    interfaces = response.json()['data']
                    for interface in interfaces:
                        if interface.get('inet') and not interface['inet'].startswith('127.'):
                            return interface['inet'].split('/')[0]
                
                # Alternative : lire depuis la config
                config_url = f"{self.proxmox_host}/api2/json/nodes/{node}/lxc/{vmid}/config"
                response = self.session.get(config_url)
                
                if response.status_code == 200:
                    config = response.json()['data']
                    # Chercher net0, net1, etc.
                    for key, value in config.items():
                        if key.startswith('net') and 'ip=' in str(value):
                            import re
                            match = re.search(r'ip=(\d+\.\d+\.\d+\.\d+)', str(value))
                            if match:
                                return match.group(1)
            
            return "Non configuré"
            
        except Exception as e:
            logging.debug(f"Impossible de récupérer l'IP pour {vm_type} {vmid}: {e}")
            return "Voir DHCP"
    
    def send_notification(self, title, message, priority="normal"):
        """Envoie une notification"""
        try:
            if self.notification_type == 'gotify':
                url = f"{self.notification_url}/message"
                priority_map = {"low": 2, "normal": 5, "high": 8}
                data = {
                    "title": title,
                    "message": message,
                    "priority": priority_map.get(priority, 5)
                }
                params = {"token": self.notification_token}
                response = requests.post(url, json=data, params=params)
                response.raise_for_status()
                
            elif self.notification_type == 'ntfy':
                headers = {
                    "Title": title,
                    "Priority": priority,
                    "Tags": "computer"
                }
                if self.notification_token:
                    headers["Authorization"] = f"Bearer {self.notification_token}"
                response = requests.post(self.notification_url, data=message.encode('utf-8'), headers=headers)
                response.raise_for_status()
                
            elif self.notification_type == 'discord':
                # Support Discord webhook
                color_map = {"low": 3066993, "normal": 3447003, "high": 15158332}  # vert, bleu, rouge
                
                embed = {
                    "title": title,
                    "description": message,
                    "color": color_map.get(priority, 3447003),
                    "timestamp": datetime.now().isoformat(),
                    "footer": {
                        "text": "Proxmox Monitor"
                    }
                }
                
                payload = {
                    "embeds": [embed],
                    "username": "Proxmox Monitor"
                }
                
                response = requests.post(self.notification_url, json=payload)
                response.raise_for_status()
                
            elif self.notification_type == 'webhook':
                data = {
                    "title": title,
                    "message": message,
                    "priority": priority,
                    "timestamp": datetime.now().isoformat()
                }
                response = requests.post(self.notification_url, json=data)
                response.raise_for_status()
            
            logging.info(f"Notification envoyée: {title}")
            
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de la notification: {e}")
    
    def check_for_changes(self):
        """Vérifie les changements (nouvelles machines, changements d'état)"""
        if not self.authenticate():
            return
        
        current_machines = self.get_all_machines()
        update_notes = os.getenv('UPDATE_NOTES', 'true').lower() == 'true'
        
        for machine in current_machines:
            machine_id = machine['id']
            
            # Mettre à jour les notes avec l'IP si activé
            if update_notes and machine['ip'] not in ['Non configuré', 'Voir DHCP']:
                self.update_machine_notes(machine['node'], machine['vmid'], 
                                         'qemu' if machine['type'] == 'VM' else 'lxc',
                                         machine)
            
            # Nouvelle machine détectée
            if machine_id not in self.machines_state:
                message = (
                    f"🆕 Nouvelle machine détectée!\n\n"
                    f"Nom: {machine['name']}\n"
                    f"Type: {machine['type']}\n"
                    f"VMID: {machine['vmid']}\n"
                    f"Nœud: {machine['node']}\n"
                    f"État: {machine['status']}\n"
                    f"IP: {machine['ip']}"
                )
                self.send_notification(f"Nouvelle machine: {machine['name']}", message, "high")
                logging.info(f"Nouvelle machine détectée: {machine['name']}")
            
            # Changement d'état (arrêt -> démarrage)
            elif self.machines_state[machine_id]['status'] == 'stopped' and machine['status'] == 'running':
                message = (
                    f"✅ Machine démarrée!\n\n"
                    f"Nom: {machine['name']}\n"
                    f"Type: {machine['type']}\n"
                    f"État: {machine['status']}\n"
                    f"IP: {machine['ip']}"
                )
                self.send_notification(f"Machine démarrée: {machine['name']}", message, "normal")
                logging.info(f"Machine démarrée: {machine['name']}")
            
            # Mise à jour de l'état
            self.machines_state[machine_id] = {
                'name': machine['name'],
                'type': machine['type'],
                'status': machine['status'],
                'ip': machine['ip'],
                'node': machine['node'],
                'vmid': machine['vmid'],
                'last_seen': datetime.now().isoformat()
            }
        
        self.save_state()
    
    def send_daily_report(self):
        """Envoie le rapport quotidien"""
        if not self.authenticate():
            return
        
        machines = self.get_all_machines()
        
        if not machines:
            message = "Aucune machine trouvée sur Proxmox."
            self.send_notification("Rapport quotidien Proxmox", message, "low")
            return
        
        # Trier par type puis par nom
        machines.sort(key=lambda x: (x['type'], x['name']))
        
        # Construire le rapport
        report = "📊 Rapport quotidien Proxmox\n\n"
        
        vms = [m for m in machines if m['type'] == 'VM']
        lxcs = [m for m in machines if m['type'] == 'LXC']
        
        if vms:
            report += "🖥️ Machines Virtuelles:\n"
            for vm in vms:
                status_icon = "✅" if vm['status'] == 'running' else "⭕"
                report += f"{status_icon} {vm['name']} - {vm['ip']} ({vm['status']})\n"
            report += "\n"
        
        if lxcs:
            report += "📦 Conteneurs LXC:\n"
            for lxc in lxcs:
                status_icon = "✅" if lxc['status'] == 'running' else "⭕"
                report += f"{status_icon} {lxc['name']} - {lxc['ip']} ({lxc['status']})\n"
        
        # Statistiques
        running = len([m for m in machines if m['status'] == 'running'])
        stopped = len([m for m in machines if m['status'] == 'stopped'])
        report += f"\n📈 Total: {len(machines)} machines ({running} up, {stopped} down)"
        
        self.send_notification("Rapport quotidien Proxmox", report, "low")
        logging.info("Rapport quotidien envoyé")
    
    def run(self):
        """Lance le monitoring en continu"""
        logging.info("Démarrage du monitoring Proxmox")
        
        # Programmer le rapport quotidien
        schedule.every().day.at(self.daily_report_time).do(self.send_daily_report)
        
        # Envoyer un rapport au démarrage
        self.send_daily_report()
        
        # Boucle principale
        check_interval = int(os.getenv('CHECK_INTERVAL', '60'))  # secondes
        
        while True:
            try:
                self.check_for_changes()
                schedule.run_pending()
                time.sleep(check_interval)
            except KeyboardInterrupt:
                logging.info("Arrêt du monitoring")
                break
            except Exception as e:
                logging.error(f"Erreur dans la boucle principale: {e}")
                time.sleep(check_interval)

if __name__ == "__main__":
    monitor = ProxmoxMonitor()
    monitor.run()
