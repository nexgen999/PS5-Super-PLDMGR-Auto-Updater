#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 04 : Téléchargement et Synchronisation des Paquets PKG
===============================================================================
Rôle :
1. Parcourt les releases GitHub de chaque dépôt d'applications PKG validé au Module 03.
2. Télécharge les fichiers `.pkg` correspondant aux critères dans le dossier `pkg/`.
3. Vérifie les limites de taille de fichier définies dans `settings.json`.
4. Sécurité Anti-404 : Conserve les paquets locaux si le dépôt d'origine est supprimé.
===============================================================================
"""

import os
import requests
from utils import get_base_dir, load_settings, logging
from 03_update_pkg_rules import build_pkg_rules_map

def download_pkg_file(url: str, dest_path: str, max_size_mb: int = 2048, timeout: int = 30) -> bool:
    """
    Télécharge un fichier PKG en vérifiant son en-tête Content-Length pour s'assurer
    qu'il ne dépasse pas la limite maximale autorisée.
    """
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        if response.status_code == 200:
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > max_size_mb:
                    logging.warning(f"Fichier PKG trop volumineux ({size_mb:.1f} Mo > {max_size_mb} Mo max) : {url}")
                    return False

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=16384):
                    f.write(chunk)
            return True
        else:
            logging.warning(f"Échec du téléchargement du PKG ({response.status_code}) : {url}")
            return False
    except Exception as e:
        logging.error(f"Erreur réseau lors du téléchargement du PKG {url} : {e}")
        return False

def fetch_and_update_pkgs():
    """Télécharge et synchronise la totalité des applications PKG répertoriées."""
    base_dir = get_base_dir()
    settings = load_settings()
    net_cfg = settings.get("network_and_scraping", {})
    global_cfg = settings.get("global_rules_and_filtering", {})
    retention_cfg = settings.get("retention_and_storage", {})
    
    max_pkg_size = global_cfg.get("max_file_size_mb_pkg", 2048)
    rules = build_pkg_rules_map()
    pkg_dir = os.path.join(base_dir, "pkg")

    for repo_url, rule in rules.items():
        logging.info(f"[Module 04] Traitement du dépôt PKG : {repo_url}")
        
        parts = repo_url.replace("https://github.com/", "").split("/")
        if len(parts) < 2:
            continue
        owner, repo_name = parts[0], parts[1]

        api_url = f"https://api.github.com/repos/{owner}/{repo_name}/releases/latest"
        
        try:
            res = requests.get(api_url, timeout=net_cfg.get("request_timeout_seconds", 30))
            
            # Gestion Sécurité Dépôt Introuvable / 404
            if res.status_code == 404:
                if retention_cfg.get("preserve_deleted_repos", True):
                    logging.warning(f"⚠️ Dépôt PKG 404 introuvable ({repo_url}). Conservation des paquets locaux.")
                continue
            
            if res.status_code != 200:
                continue

            release_data = res.json()
            assets = release_data.get("assets", [])

            for asset in assets:
                filename = asset["name"]
                download_url = asset["browser_download_url"]

                # Ignorer si l'extension n'est pas .pkg ou si un mot-clé exclu est détecté
                if not filename.lower().endswith(".pkg"):
                    continue

                if any(kw.lower() in filename.lower() for kw in rule["keyword_ignore"]):
                    continue

                # Détermination du nom final (renommage sur-mesure ou nom d'origine)
                final_filename = rule["custom_filename"] if (rule["force_rename"] and rule["custom_filename"]) else filename
                dest_file = os.path.join(pkg_dir, repo_name, final_filename)

                if download_pkg_file(download_url, dest_file, max_size_mb=max_pkg_size):
                    logging.info(f"Fichier PKG mis à jour avec succès : {final_filename}")

        except Exception as e:
            logging.error(f"Erreur lors de la synchronisation PKG de {repo_url} : {e}")

def main():
    logging.info("=== Lancement du Module 04 : Synchronisation des Paquets PKG ===")
    fetch_and_update_pkgs()
    logging.info("=== Module 04 Terminé avec succès ===")

if __name__ == "__main__":
    main()