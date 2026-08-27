#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 07 : Génération de l'API JSON (v1)
===============================================================================
Rôle :
1. Parcourt les payloads, PKG et profils de configuration.
2. Génère les fichiers JSON d'indexation dans `api/v1/`.
3. Fournit une API statique complète pour l'UI web et le loader.
===============================================================================
"""

import os
import json
import time
from utils import get_base_dir, load_settings, logging

def build_api_json():
    base_dir = get_base_dir()
    settings = load_settings()
    site_url = settings.get("repository_identity", {}).get("social_links", {}).get("website", "https://github.com/nexgen999")
    
    api_dir = os.path.join(base_dir, "api", "v1")
    os.makedirs(api_dir, exist_ok=True)

    # 1. Traitement des Payloads
    payloads_dir = os.path.join(base_dir, "payloads")
    payloads_data = []

    if os.path.exists(payloads_dir):
        for root, _, files in os.walk(payloads_dir):
            for file in files:
                if file.endswith((".elf", ".bin")):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
                    mtime = os.path.getmtime(full_path)
                    
                    payloads_data.append({
                        "filename": file,
                        "path": rel_path,
                        "download_url": f"{site_url}/{rel_path}",
                        "size_bytes": os.path.getsize(full_path),
                        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))
                    })

    with open(os.path.join(api_dir, "payloads.json"), "w", encoding="utf-8") as f:
        json.dump({"updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "count": len(payloads_data), "items": payloads_data}, f, indent=2, ensure_ascii=False)

    # 2. Traitement des PKG
    pkg_dir = os.path.join(base_dir, "pkg")
    pkg_data = []

    if os.path.exists(pkg_dir):
        for root, _, files in os.walk(pkg_dir):
            for file in files:
                if file.endswith(".pkg"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
                    mtime = os.path.getmtime(full_path)
                    
                    pkg_data.append({
                        "filename": file,
                        "path": rel_path,
                        "download_url": f"{site_url}/{rel_path}",
                        "size_bytes": os.path.getsize(full_path),
                        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))
                    })

    with open(os.path.join(api_dir, "pkg.json"), "w", encoding="utf-8") as f:
        json.dump({"updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "count": len(pkg_data), "items": pkg_data}, f, indent=2, ensure_ascii=False)

    logging.info(f"[Module 07] API JSON v1 générée : {len(payloads_data)} payloads, {len(pkg_data)} PKG.")

def main():
    logging.info("=== Lancement du Module 07 : Génération API JSON ===")
    build_api_json()
    logging.info("=== Module 07 Terminé avec succès ===")

if __name__ == "__main__":
    main()