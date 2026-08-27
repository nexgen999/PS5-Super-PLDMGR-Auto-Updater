#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 02 : Téléchargement et Synchronisation des Payloads
===============================================================================
Rôle :
1. Interroge les releases GitHub de chaque dépôt issu du Module 01.
2. Filtre les assets selon les règles (extensions, mots-clés, archives).
3. Télécharge et extrait si nécessaire (.zip / .rar) dans le dossier `payloads/`.
4. Sécurité Anti-404 : Conservé si le dépôt source a été supprimé ou renommé.
===============================================================================
"""

import os
import zipfile
import requests
from utils import get_base_dir, load_settings, logging
import importlib
module_01 = importlib.import_module("botbuild.01_update_payload_rules")
build_payload_rules_map = module_01.build_payload_rules_map

def download_file(url: str, dest_path: str, timeout: int = 30) -> bool:
    """Télécharge un fichier distant vers le chemin local spécifié."""
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            logging.warning(f"Échec du téléchargement ({response.status_code}) : {url}")
            return False
    except Exception as e:
        logging.error(f"Erreur réseau lors du téléchargement de {url} : {e}")
        return False

def process_archive(archive_path: str, extract_dir: str, target_exts: list) -> list:
    """Extraie les fichiers cibles (.elf / .bin) depuis une archive ZIP."""
    extracted_files = []
    try:
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if any(member.endswith(ext) for ext in target_exts):
                        zip_ref.extract(member, extract_dir)
                        extracted_files.append(os.path.join(extract_dir, member))
    except Exception as e:
        logging.error(f"Erreur d'extraction sur l'archive {archive_path} : {e}")
    return extracted_files

def fetch_and_update_payloads():
    """Parcourt les dépôts et met à jour le dossier payloads/."""
    base_dir = get_base_dir()
    settings = load_settings()
    net_cfg = settings.get("network_and_scraping", {})
    retention_cfg = settings.get("retention_and_storage", {})
    
    rules = build_payload_rules_map()
    payloads_dir = os.path.join(base_dir, "payloads")

    for repo_url, rule in rules.items():
        logging.info(f"[Module 02] Traitement du dépôt : {repo_url}")
        
        # Extraction du proprietaire et nom du repo pour l'API GitHub
        parts = repo_url.replace("https://github.com/", "").split("/")
        if len(parts) < 2:
            continue
        owner, repo_name = parts[0], parts[1]

        api_url = f"https://api.github.com/repos/{owner}/{repo_name}/releases/latest"
        
        try:
            res = requests.get(api_url, timeout=net_cfg.get("request_timeout_seconds", 30))
            
            # Gestion Dépôt Introuvable / Supprimé (404)
            if res.status_code == 404:
                if retention_cfg.get("preserve_deleted_repos", True):
                    logging.warning(f"⚠️ Dépôt 404 introuvable ({repo_url}). Conservation des fichiers locaux (Mode Archive).")
                continue
            
            if res.status_code != 200:
                continue

            release_data = res.json()
            assets = release_data.get("assets", [])

            for asset in assets:
                filename = asset["name"]
                download_url = asset["browser_download_url"]

                # Application des filtres d'exclusion par mots-clés
                if any(kw.lower() in filename.lower() for kw in rule["keyword_ignore"]):
                    continue

                # Téléchargement vers un dossier de destination
                dest_file = os.path.join(payloads_dir, repo_name, filename)
                
                # Cas 1 : Archive ZIP à extraire
                if rule["archive_extract"] and filename.endswith(".zip"):
                    temp_zip = os.path.join(payloads_dir, "temp", filename)
                    if download_file(download_url, temp_zip):
                        extracted = process_archive(temp_zip, os.path.join(payloads_dir, repo_name), rule["archive_target_extension"])
                        logging.info(f"Fichiers extraits : {extracted}")
                        if os.path.exists(temp_zip):
                            os.remove(temp_zip)

                # Cas 2 : Fichier binaire direct (.elf / .bin)
                elif any(filename.endswith(ext) for ext in [".elf", ".bin"]):
                    if download_file(download_url, dest_file):
                        logging.info(f"Payload mis à jour : {filename}")

        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation de {repo_url} : {e}")

def main():
    logging.info("=== Lancement du Module 02 : Téléchargement des Payloads ===")
    fetch_and_update_payloads()
    logging.info("=== Module 02 Terminé avec succès ===")

if __name__ == "__main__":
    main()
