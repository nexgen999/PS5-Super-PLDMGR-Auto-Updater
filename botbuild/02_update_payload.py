import os
import sys
import json
import logging
import requests

# Ajout du dossier botbuild au chemin Python pour permettre les imports entre modules
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import importlib
module_01 = importlib.import_module("01_update_payload_rules")
build_payload_rules_map = module_01.build_payload_rules_map

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SETTINGS_PATH = os.path.join(CURRENT_DIR, "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def download_file(url, destination_path):
    """Telecharge un fichier avec un timeout pour eviter les blocages dans GitHub Actions."""
    headers = {"User-Agent": "PS5-Super-PLDMGR-Auto-Updater"}
    try:
        response = requests.get(url, headers=headers, timeout=(10, 60), stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            with open(destination_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info(f"Fichier telecharge : {destination_path}")
            return True
        else:
            logging.warning(f"Echec du telechargement ({response.status_code}) : {url}")
    except Exception as e:
        logging.error(f"Erreur lors du telechargement de {url} : {e}")
    return False

def process_payload_updates():
    logging.info("=== Lancement du Module 02 : Mise a jour des Payloads ===")
    
    # 1. Recuperation des regles de depot construites par le module 01
    rules_map = build_payload_rules_map()
    if not rules_map:
        logging.warning("Aucune regle de payload trouvee dans le module 01.")
        return

    payloads_dir = "payloads"
    os.makedirs(payloads_dir, exist_ok=True)
    
    downloaded_count = 0

    # 2. Iteration sur chaque regle et telechargement des fichiers .elf / .bin
    for repo_name, rule in rules_map.items():
        download_url = rule.get("download_url")
        file_name = rule.get("file_name")
        category = rule.get("category", "uncategorized")

        if download_url and file_name:
            target_dir = os.path.join(payloads_dir, category)
            target_file_path = os.path.join(target_dir, file_name)

            if download_file(download_url, target_file_path):
                downloaded_count += 1

    logging.info(f"=== Module 02 Termine avec succes : {downloaded_count} payload(s) traite(s) ===")

if __name__ == "__main__":
    process_payload_updates()
