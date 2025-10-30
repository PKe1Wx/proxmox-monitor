#!/bin/bash

echo "========================================="
echo "Test du webhook Discord"
echo "========================================="
echo ""

WEBHOOK_URL="https://discord.com/api/webhooks/1433028525279150203/HohwbkhS3BQ_z5CQtRtX5UlqzblkXBHaq8530Ao_bIpdNy8a4dMLhhnUybID7wUAgzrr"

echo "Envoi d'un message de test sur Discord..."
echo ""

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "embeds": [{
      "title": "🧪 Test Proxmox Monitor",
      "description": "Votre webhook Discord fonctionne parfaitement !\n\n✅ Configuration réussie\n📱 Vous êtes prêt à recevoir les notifications",
      "color": 3447003,
      "fields": [
        {
          "name": "🖥️ Test",
          "value": "Notification envoyée avec succès",
          "inline": false
        }
      ],
      "footer": {
        "text": "Proxmox Monitor"
      },
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'"
    }],
    "username": "Proxmox Monitor"
  }'

echo ""
echo ""

if [ $? -eq 0 ]; then
    echo "✅ Message envoyé avec succès !"
    echo "Vérifiez votre canal Discord."
else
    echo "❌ Erreur lors de l'envoi du message."
    echo "Vérifiez votre connexion internet et l'URL du webhook."
fi

echo ""
