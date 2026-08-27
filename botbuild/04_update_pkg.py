import os
import sys
import json
import logging
import requests

# Gestion du sys.path pour les imports internes
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import importlib
module_03 = importlib.import_module("03_update_pkg_rules")
build_pkg_rules_map = module_03.build_pkg_rules_map

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SETTINGS_PATH = os.path.join(CURRENT_DIR, "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def download_file(url, destination_path):
    """Télécharge un fichier PKG avec timeout."""
    headers = {"User-Agent": "PS5-Super-PLDMGR-Auto-Updater"}
    try:
        response = requests.get(url, headers=headers, timeout=(10, 60), stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info(f"Fichier PKG téléchargé : {destination_path}")
            return True
        else:
            logging.warning(f"Échec du téléchargement ({response.status_code}) : {url}")
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement de {url} : {e}")
    return False

def process_pkg_updates():
    logging.info("=== Lancement du Module 04 : Mise à jour des PKG ===")
    
    rules_map = build_pkg_rules_map()
    if not rules_map:
        logging.warning("Aucune règle PKG trouvée dans le module 03.")
        return

    pkg_dir = "pkg"
    os.makedirs(pkg_dir, exist_ok=True)
    
    downloaded_count = 0

    for repo_name, rule in rules_map.items():
        download_url = rule.get("download_url")
        file_name = rule.get("file_name")
        category = rule.get("category", "uncategorized")

        if download_url and file_name:
            target_dir = os.path.join(pkg_dir, category)
            target_file_path = os.path.join(target_dir, file_name)

            if download_file(download_url, target_file_path):
                downloaded_count += 1

    logging.info(f"=== Module 04 Terminé avec succès : {downloaded_count} PKG traité(s) ===")

if __name__ == "__main__":
    process_pkg_updates()
