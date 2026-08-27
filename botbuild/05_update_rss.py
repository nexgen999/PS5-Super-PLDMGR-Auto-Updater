#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 05 : Génération du Flux RSS Synthétique
===============================================================================
Rôle :
1. Scanne l'ensemble des fichiers Payloads et PKG disponibles sur le dépôt.
2. Extrait les dates de modification, versions et catégories.
3. Génère un fichier RSS 2.0 (rss/payloads_rss.xml) valide.
===============================================================================
"""

import os
import time
from xml.sax.saxutils import escape
from utils import get_base_dir, load_settings, logging

def generate_rss_feed():
    base_dir = get_base_dir()
    settings = load_settings()
    repo_cfg = settings.get("repository_identity", {})
    
    site_url = repo_cfg.get("social_links", {}).get("website", "https://github.com/nexgen999")
    rss_path = os.path.join(base_dir, "rss", "payloads_rss.xml")
    
    os.makedirs(os.path.dirname(rss_path), exist_ok=True)
    
    items_xml = []
    
    # Parcours des Payloads et PKG pour construire les entrées RSS
    targets = [
        ("Payload", os.path.join(base_dir, "payloads")),
        ("PKG", os.path.join(base_dir, "pkg"))
    ]
    
    for item_type, target_dir in targets:
        if not os.path.exists(target_dir):
            continue
            
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".elf", ".bin", ".pkg")):
                    full_path = os.path.join(root, file)
                    mtime = os.path.getmtime(full_path)
                    pub_date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(mtime))
                    rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
                    
                    item_title = f"[{item_type}] {file}"
                    item_link = f"{site_url}/{rel_path}"
                    item_desc = f"Nouveau binaire {item_type} disponible : {file} (Mise à jour automatique)."
                    
                    items_xml.append(f"""    <item>
      <title>{escape(item_title)}</title>
      <link>{escape(item_link)}</link>
      <description>{escape(item_desc)}</description>
      <pubDate>{pub_date}</pubDate>
      <guid>{escape(item_link)}</guid>
    </item>""")

    # Trio d'en-tête, corps et fermeture du document XML RSS
    rss_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>{escape(settings.get("web_and_ui", {}).get("site_title", "PS5 Super PLDMGR Store"))}</title>
    <link>{escape(site_url)}</link>
    <description>Flux d'actualités et de mises à jour automatiques des Payloads et PKG PS5</description>
    <language>fr-FR</language>
    <lastBuildDate>{time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())}</lastBuildDate>
{"".join(items_xml)}
  </channel>
</rss>"""

    with open(rss_path, "w", encoding="utf-8") as f:
        f.write(rss_content)
        
    logging.info(f"[Module 05] Flux RSS généré avec succès : {rss_path} ({len(items_xml)} éléments)")

def main():
    logging.info("=== Lancement du Module 05 : Génération Flux RSS ===")
    generate_rss_feed()
    logging.info("=== Module 05 Terminé avec succès ===")

if __name__ == "__main__":
    main()