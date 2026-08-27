import os
import sys
import json
import logging
import requests

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import importlib
module_03 = importlib.import_module("03_update_pkg_rules")
build_pkg_rules_map = module_03.build_pkg_rules_map

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def download_file(url, destination_path):
    headers = {"User-Agent": "PS5-Super-PLDMGR-Auto-Updater"}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        
    try:
        response = requests.get(url, headers=headers, timeout=(10, 60), stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info(f"[Module 04] PKG téléchargé : {destination_path}")
            return True
        else:
            logging.warning(f"[Module 04] Échec du téléchargement ({response.status_code}) : {url}")
    except Exception as e:
        logging.error(f"[Module 04] Erreur sur {url} : {e}")
    return False

def process_pkg_updates():
    logging.info("=== Lancement du Module 04 : Mise à jour des PKG ===")
    
    # Récupération des règles issues de 03_update_pkg_rules.py
    rules_map = build_pkg_rules_map()
    if not rules_map:
        logging.warning("[Module 04] Aucune règle PKG trouvée.")
        return

    pkg_dir = "pkg"
    os.makedirs(pkg_dir, exist_ok=True)
    downloaded_count = 0

    # Si rules_map est une liste de règles au lieu d'un dictionnaire
    items = rules_map.values() if isinstance(rules_map, dict) else rules_map

    for rule in items:
        download_url = rule.get("download_url") or rule.get("url")
        file_name = rule.get("file_name") or rule.get("name")
        category = rule.get("category", "main")

        if download_url and file_name:
            target_path = os.path.join(pkg_dir, category, file_name)
            if download_file(download_url, target_path):
                downloaded_count += 1

    logging.info(f"=== Module 04 Terminé : {downloaded_count} PKG traité(s) ===")

if __name__ == "__main__":
    process_pkg_updates()
