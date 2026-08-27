#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Pipeline Principal : Master Orchestrator (15 Modules)
===============================================================================
Description :
Exécute dans l'ordre séquentiel l'ensemble des modules du botbuild pour la 
synchronisation, la génération des API, la création des archives et la publication.
===============================================================================
"""

import sys
import time
import importlib
from utils import logging

# Liste des 15 modules correspondant à tes fichiers réels
MODULES = [
    ("Module 01", "01_update_payload_rules", "Analyse des règles Payloads"),
    ("Module 02", "02_update_payload", "Téléchargement des Payloads"),
    ("Module 03", "03_update_pkg_rules", "Analyse des règles PKG"),
    ("Module 04", "04_update_pkg", "Téléchargement des PKG"),
    ("Module 05", "05_update_rss", "Génération du flux RSS"),
    ("Module 06", "06_clean_repository", "Nettoyage et rotation de sauvegarde"),
    ("Module 07", "07_build_api_json", "Génération des API JSON"),
    ("Module 08", "08_generate_whatsnew", "Génération du changelog whatsnew.md"),
    ("Module 09", "09_discord_webhook", "Notification Discord Webhook"),
    ("Module 10", "10_create_zip_archives", "Archives ZIP & Assemblage Store Clean"),
    ("Module 11", "11_build_index_html", "Génération de index.html"),
    ("Module 12", "12_validate_json", "Validation des fichiers JSON"),
    ("Module 13", "13_update_readme", "Mise à jour du README.md"),
    ("Module 14", "14_git_commit_push", "Git Commit & Push"),
    ("Module 15", "15_generate_opml", "Génération de l'export OPML")
]

def run_module(module_tag, module_name, description):
    """Importe et exécute la fonction main() d'un module donné."""
    logging.info(f"---> [{module_tag}] {description} ({module_name}.py)...")
    start_time = time.time()
    
    try:
        # Import dynamique du module
        mod = importlib.import_module(module_name)
        
        # Vérification de la présence de la fonction main()
        if hasattr(mod, "main"):
            mod.main()
        else:
            logging.warning(f"  [!] Aucune fonction main() trouvée dans {module_name}.py")
            
        elapsed = time.time() - start_time
        logging.info(f"  [OK] {module_tag} terminé en {elapsed:.2f}s\n")
        return True

    except Exception as e:
        elapsed = time.time() - start_time
        logging.error(f"  [X] ÉCHEC du {module_tag} ({module_name}.py) après {elapsed:.2f}s")
        logging.error(f"      Erreur : {e}", exc_info=True)
        return False

def main():
    start_pipeline = time.time()
    logging.info("=========================================================================")
    logging.info("         DÉMARRAGE DU PIPELINE BOTBUILD - STORE PS5 (15 MODULES)          ")
    logging.info("=========================================================================\n")

    failed_modules = []

    for tag, name, desc in MODULES:
        success = run_module(tag, name, desc)
        if not success:
            failed_modules.append((tag, name))
            # Optionnel : Interrompre le pipeline en cas d'erreur sur un module critique
            # sys.exit(1)

    total_time = time.time() - start_pipeline
    logging.info("=========================================================================")
    
    if not failed_modules:
        logging.info(f"  [SUCCESS] PIPELINE TERMINÉ AVEC SUCCÈS EN {total_time:.2f}s")
    else:
        logging.warning(f"  [WARNING] PIPELINE TERMINÉ EN {total_time:.2f}s AVEC DES ERREURS :")
        for tag, name in failed_modules:
            logging.warning(f"    - {tag} ({name}.py)")

    logging.info("=========================================================================")

if __name__ == "__main__":
    main()