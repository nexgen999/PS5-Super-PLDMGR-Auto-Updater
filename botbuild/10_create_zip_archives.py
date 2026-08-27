#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 10 : Compression ZIP & Assembly du Store Clean
===============================================================================
Rôle :
1. Génère 'payloads_latest.zip' contenant la dernière version de chaque payload
   référencé dans api/v1/payloads.json.
2. Génère 'pkg_latest.zip' contenant l'ensemble des fichiers PKG disponibles.
3. Prépare le dossier 'dist/' (Store Clean) prêt à être déployé ou poussé sur Git.
===============================================================================
"""

import os
import json
import shutil
import zipfile
from utils import get_base_dir, logging

def build_payloads_zip(base_dir, dist_dir):
    """Crée une seule archive ZIP avec uniquement la dernière version de chaque payload."""
    api_payloads_path = os.path.join(base_dir, "api", "v1", "payloads.json")
    zip_path = os.path.join(dist_dir, "payloads_latest.zip")

    if not os.path.exists(api_payloads_path):
        logging.warning("[Module 10] api/v1/payloads.json introuvable, annulation du ZIP payloads.")
        return

    with open(api_payloads_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        items = data.get("items", [])

    added_files = set()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in items:
            # Récupère le chemin du fichier relatif ou absolu enregistré dans l'API
            file_path = item.get("file_path") or item.get("local_path")
            if not file_path:
                continue

            full_path = os.path.join(base_dir, file_path) if not os.path.isabs(file_path) else file_path

            if os.path.exists(full_path) and full_path not in added_files:
                filename = os.path.basename(full_path)
                zipf.write(full_path, arcname=os.path.join("payloads", filename))
                added_files.add(full_path)

    logging.info(f"[Module 10] Archive payloads_latest.zip créée avec {len(added_files)} fichier(s).")

def build_pkg_zip(base_dir, dist_dir):
    """Crée une seule archive ZIP contenant tous les PKG."""
    pkg_dir = os.path.join(base_dir, "pkg")
    zip_path = os.path.join(dist_dir, "pkg_latest.zip")

    if not os.path.exists(pkg_dir):
        logging.warning("[Module 10] Dossier pkg introuvable, annulation du ZIP PKG.")
        return

    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(pkg_dir):
            for file in files:
                if file.endswith(".pkg"):
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, pkg_dir)
                    zipf.write(full_path, arcname=os.path.join("pkg", arcname))
                    count += 1

    logging.info(f"[Module 10] Archive pkg_latest.zip créée avec {count} fichier(s).")

def assemble_clean_store(base_dir, dist_dir):
    """Assemble le Store Clean dans dist/ avec tous les fichiers prêts pour Git/déploiement."""
    # Dossiers et fichiers essentiels du store à inclure dans le build clean
    items_to_copy = [
        "api",
        "payloads",
        "pkg",
        "index.html",
        "whatsnew.md",
        "README.md",
        "PS5_Repository_Feeds.opml"
    ]

    for item in items_to_copy:
        src = os.path.join(base_dir, item)
        dst = os.path.join(dist_dir, item)

        if not os.path.exists(src):
            continue

        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    logging.info("[Module 10] Store Clean assemblé dans le dossier dist/.")

def main():
    logging.info("=== Lancement du Module 10 : Archives ZIP & Build Store Clean ===")
    base_dir = get_base_dir()
    dist_dir = os.path.join(base_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)

    build_payloads_zip(base_dir, dist_dir)
    build_pkg_zip(base_dir, dist_dir)
    assemble_clean_store(base_dir, dist_dir)

    logging.info("=== Module 10 Terminé avec succès ===")

if __name__ == "__main__":
    main()