#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 09 : Notification Discord Webhook
===============================================================================
Rôle :
1. Vérifie si une URL de webhook est configurée dans les paramètres.
2. Lit les statistiques générées par l'API JSON.
3. Envoie un message formaté (Embed) sur Discord.
===============================================================================
"""

import os
import json
import urllib.request
import urllib.error
from utils import get_base_dir, load_settings, logging

def send_discord_notification():
    base_dir = get_base_dir()
    settings = load_settings()
    
    webhook_url = settings.get("web_and_ui", {}).get("discord_webhook_url", "")
    if not webhook_url or webhook_url.strip() == "":
        logging.info("[Module 09] Aucun Webhook Discord configuré, étape ignorée.")
        return

    site_title = settings.get("web_and_ui", {}).get("site_title", "PS5 Super PLDMGR Store")
    site_url = settings.get("repository_identity", {}).get("social_links", {}).get("website", "https://github.com/nexgen999")
    
    # Lecture des statistiques depuis l'API JSON générée au module 07
    payloads_count = 0
    pkg_count = 0
    
    try:
        with open(os.path.join(base_dir, "api", "v1", "payloads.json"), "r", encoding="utf-8") as f:
            payloads_count = json.load(f).get("count", 0)
        with open(os.path.join(base_dir, "api", "v1", "pkg.json"), "r", encoding="utf-8") as f:
            pkg_count = json.load(f).get("count", 0)
    except FileNotFoundError:
        pass

    # Construction du message Embed
    embed = {
        "title": "✅ Mise à jour automatique terminée",
        "description": f"Les dépôts de **{site_title}** viennent d'être synchronisés.",
        "url": site_url,
        "color": 3066993, # Vert
        "fields": [
            {"name": "🧱 Payloads disponibles", "value": str(payloads_count), "inline": True},
            {"name": "📦 PKG disponibles", "value": str(pkg_count), "inline": True},
            {"name": "Détails", "value": f"[Voir le Changelog]({site_url}/whatsnew.md)", "inline": False}
        ],
        "footer": {"text": "Bot Build Pipeline"}
    }

    data = json.dumps({"embeds": [embed]}).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})

    try:
        urllib.request.urlopen(req)
        logging.info("[Module 09] Notification Discord envoyée avec succès.")
    except urllib.error.URLError as e:
        logging.error(f"[Module 09] Échec de l'envoi au Webhook Discord : {e}")

def main():
    logging.info("=== Lancement du Module 09 : Discord Webhook ===")
    send_discord_notification()
    logging.info("=== Module 09 Terminé avec succès ===")

if __name__ == "__main__":
    main()