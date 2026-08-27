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
import shutil
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def build_zip_archives():
    """
    Cree les archives AIO dans dist/ et conserve un backup dans backup/payloads/ et backup/pkg/
    """
    dist_dir = "dist"
    backup_payloads_dir = "backup/payloads"
    backup_pkg_dir = "backup/pkg"

    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(backup_payloads_dir, exist_ok=True)
    os.makedirs(backup_pkg_dir, exist_ok=True)

    # 1. Archive AIO Payloads
    payloads_source = "payloads"
    payloads_zip_dist = os.path.join(dist_dir, "payloads_aio.zip")
    payloads_zip_backup = os.path.join(backup_payloads_dir, "payloads_aio.zip")

    if os.path.exists(payloads_source):
        with zipfile.ZipFile(payloads_zip_dist, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(payloads_source):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, payloads_source)
                    zipf.write(file_path, arcname)
        logging.info(f"Archive AIO Payloads creee : {payloads_zip_dist}")
        
        # Copie dans backup/payloads/
        shutil.copy(payloads_zip_dist, payloads_zip_backup)
        logging.info(f"Backup Payloads copie dans : {payloads_zip_backup}")

    # 2. Archive AIO PKG
    pkg_source = "pkg"
    pkg_zip_dist = os.path.join(dist_dir, "pkg_aio.zip")
    pkg_zip_backup = os.path.join(backup_pkg_dir, "pkg_aio.zip")

    if os.path.exists(pkg_source):
        with zipfile.ZipFile(pkg_zip_dist, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(pkg_source):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, pkg_source)
                    zipf.write(file_path, arcname)
        logging.info(f"Archive AIO PKG creee : {pkg_zip_dist}")
        
        # Copie dans backup/pkg/
        shutil.copy(pkg_zip_dist, pkg_zip_backup)
        logging.info(f"Backup PKG copie dans : {pkg_zip_backup}")

if __name__ == "__main__":
    logging.info("Execution du module 10_create_zip_archives...")
    build_zip_archives()

    logging.info("=== Module 10 Terminé avec succès ===")

if __name__ == "__main__":
    main()
