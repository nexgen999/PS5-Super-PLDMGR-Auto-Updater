#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 08 : Génération du Changelog whatsnew.md
===============================================================================
Rôle :
1. Récupère les fichiers les plus récents ajoutés ou mis à jour.
2. Synthétise les informations sous forme d'un document Markdown clair.
3. Enregistre le résultat dans `whatsnew.md` à la racine du dépôt.
===============================================================================
"""

import os
import time
from utils import get_base_dir, load_settings, logging

def generate_whatsnew():
    base_dir = get_base_dir()
    settings = load_settings()
    site_title = settings.get("web_and_ui", {}).get("site_title", "PS5 Super PLDMGR Store")
    whatsnew_path = os.path.join(base_dir, "whatsnew.md")

    files_list = []
    
    # Parcours des répertoires payloads et pkg
    for folder_name in ["payloads", "pkg"]:
        target_dir = os.path.join(base_dir, folder_name)
        if not os.path.exists(target_dir):
            continue

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith((".elf", ".bin", ".pkg")):
                    full_path = os.path.join(root, file)
                    mtime = os.path.getmtime(full_path)
                    files_list.append((file, folder_name, mtime, os.path.getsize(full_path)))

    # Tri par date de modification (du plus récent au plus ancien)
    files_list.sort(key=lambda x: x[2], reverse=True)

    # Récupération des 15 derniers éléments
    recent_items = files_list[:15]

    md_lines = [
        f"# 🆕 Quoi de neuf sur {site_title} ?",
        f"\n*Dernière mise à jour automatique : {time.strftime('%d/%m/%Y à %H:%M:%S', time.localtime())}*\n",
        "| Type | Fichier | Taille | Mis à jour le |",
        "| :--- | :--- | :--- | :--- |"
    ]

    for filename, ftype, mtime, size in recent_items:
        date_str = time.strftime("%d/%m/%Y %H:%M", time.localtime(mtime))
        size_mb = f"{size / (1024 * 1024):.2f} Mo"
        type_badge = "🧱 Payload" if ftype == "payloads" else "📦 PKG"
        md_lines.append(f"| {type_badge} | `{filename}` | {size_mb} | {date_str} |")

    with open(whatsnew_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    logging.info(f"[Module 08] Fichier whatsnew.md généré ({len(recent_items)} entrées récents).")

def main():
    logging.info("=== Lancement du Module 08 : Génération whatsnew.md ===")
    generate_whatsnew()
    logging.info("=== Module 08 Terminé avec succès ===")

if __name__ == "__main__":
    main()