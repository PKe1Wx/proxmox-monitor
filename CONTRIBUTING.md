# Contribution au projet Proxmox Monitor

Merci de votre intérêt pour contribuer à Proxmox Monitor ! 🎉

## 🤝 Comment contribuer

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](https://github.com/VOTRE-USERNAME/proxmox-monitor/issues)
2. Ouvrez une nouvelle issue avec le template "Bug Report"
3. Décrivez clairement le problème avec :
   - Version de Proxmox Monitor
   - Version de Proxmox VE
   - Configuration (masquez les infos sensibles)
   - Logs pertinents
   - Étapes pour reproduire

### Proposer une fonctionnalité

1. Ouvrez une issue avec le template "Feature Request"
2. Décrivez la fonctionnalité souhaitée
3. Expliquez pourquoi elle serait utile
4. Proposez une implémentation si possible

### Soumettre une Pull Request

1. **Fork** le projet
2. **Créez une branche** pour votre fonctionnalité :
   ```bash
   git checkout -b feature/ma-super-fonctionnalite
   ```
3. **Commitez** vos changements :
   ```bash
   git commit -am 'Ajout d'une fonctionnalité géniale'
   ```
4. **Push** vers la branche :
   ```bash
   git push origin feature/ma-super-fonctionnalite
   ```
5. **Ouvrez une Pull Request**

## 📝 Guidelines de code

### Style Python

- Suivez [PEP 8](https://peps.python.org/pep-0008/)
- Utilisez des noms de variables explicites
- Commentez le code complexe
- Maximum 100 caractères par ligne

### Commits

Format des messages de commit :

```
type(scope): description courte

Description plus détaillée si nécessaire

Fixes #123
```

**Types** :
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage, pas de changement de code
- `refactor`: Refactorisation du code
- `test`: Ajout de tests
- `chore`: Maintenance

**Exemples** :
```
feat(notifications): ajout support Telegram
fix(proxmox): correction détection IP pour LXC
docs(readme): mise à jour instructions installation
```

## 🧪 Tests

Avant de soumettre une PR :

1. **Testez localement** :
   ```bash
   docker-compose build
   docker-compose up -d
   docker-compose logs -f
   ```

2. **Vérifiez que ça fonctionne** :
   - Création de VM/LXC
   - Démarrage/arrêt
   - Rapport quotidien
   - Notifications Discord

3. **Testez les cas limites** :
   - Proxmox inaccessible
   - Webhook Discord invalide
   - Configuration incorrecte

## 📚 Documentation

- Mettez à jour le **README.md** si nécessaire
- Ajoutez des commentaires dans le code
- Documentez les nouvelles variables d'environnement
- Mettez à jour le **CHANGELOG.md**

## ✅ Checklist avant PR

- [ ] Le code suit les guidelines
- [ ] Testé localement
- [ ] Documentation mise à jour
- [ ] CHANGELOG.md mis à jour
- [ ] Pas de données sensibles (tokens, mots de passe)
- [ ] Commits clairs et descriptifs

## 🎯 Domaines où contribuer

### Facile (débutants)
- 📝 Amélioration de la documentation
- 🌍 Traductions
- 🐛 Correction de typos
- ✨ Amélioration des messages de notification

### Moyen
- 🔔 Nouveaux types de notifications (Telegram, Slack, Email)
- 🎨 Personnalisation des messages Discord
- 📊 Nouvelles métriques à surveiller
- 🔧 Nouvelles options de configuration

### Avancé
- 🖥️ Interface web de visualisation
- 📈 Dashboard Grafana
- 🏠 Intégration Home Assistant
- 🔐 Améliorations de sécurité
- ⚡ Optimisations de performances

## 💬 Questions ?

- Ouvrez une [Discussion](https://github.com/VOTRE-USERNAME/proxmox-monitor/discussions)
- Rejoignez le Discord du projet (si disponible)
- Contactez les mainteneurs

## 📜 Code de conduite

Soyez respectueux et constructif. Nous voulons une communauté accueillante pour tous.

## 🙏 Merci !

Chaque contribution, petite ou grande, est appréciée ! Merci de rendre ce projet meilleur. ❤️
