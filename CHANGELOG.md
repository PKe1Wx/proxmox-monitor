# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.0] - 2025-01-30

### Ajouté
- 🎉 Version initiale du projet
- ✨ Détection automatique des nouvelles VM et LXC
- 🚀 Notifications au démarrage des machines
- 📊 Rapport quotidien configurable
- 🌐 Récupération automatique des IP (QEMU Guest Agent pour VM, natif pour LXC)
- 🔔 Support notifications Discord avec embeds colorés
- 🔐 Support Token API Proxmox (authentification sécurisée)
- 💾 Persistance des états des machines
- 🐳 Conteneurisation Docker
- 🍓 Optimisation pour Raspberry Pi
- 📝 Documentation complète (README, guides, exemples)
- 🧪 Script de test pour webhook Discord
- ⚙️ Script d'installation interactive

### Fonctionnalités
- Surveillance multi-nœuds (clusters Proxmox)
- Support authentification par mot de passe ou token API
- Intervalle de vérification configurable
- Heure du rapport quotidien personnalisable
- Logs persistants
- Désactivation automatique de la vérification SSL (certificats auto-signés)

### Documentation
- README principal avec installation rapide
- Guide de configuration Proxmox (PROXMOX_SETUP.md)
- Guide de configuration Discord (DISCORD_SETUP.md)
- Guide de démarrage rapide (QUICK_START.md)
- Exemples d'utilisation avancée (ADVANCED.md)

## [Unreleased]

### À venir
- Support Telegram
- Support Slack
- Interface web de visualisation
- Alertes sur l'utilisation des ressources (CPU/RAM)
- Intégration Home Assistant native
- Support snapshots automatiques
- Notifications par email
- Dashboard Grafana

---

## Format des versions

- **MAJOR** : Changements incompatibles avec les versions précédentes
- **MINOR** : Nouvelles fonctionnalités rétrocompatibles
- **PATCH** : Corrections de bugs rétrocompatibles

## Types de changements

- **Ajouté** : Nouvelles fonctionnalités
- **Modifié** : Changements dans des fonctionnalités existantes
- **Déprécié** : Fonctionnalités qui seront supprimées
- **Supprimé** : Fonctionnalités supprimées
- **Corrigé** : Corrections de bugs
- **Sécurité** : Corrections de vulnérabilités
