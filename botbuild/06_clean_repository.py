#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 06 : Rétention et Rotation des Sauvegardes
===============================================================================
Rôle :
1. Contrôle le nombre de versions actives conservées dans `payloads/` et `pkg/`.
2. Déplace les versions plus anciennes vers le dossier `backup/payloads/`.
3. Assure la protection absolue des dépôts archivés (Anti-404).
===============================================================================
"""

import os
import shutil
from utils import get_base_dir, load_settings, logging

def apply_retention_and_backup():
    base_dir = get_base_dir()
    settings = load_settings()
    ret_cfg = settings.get("retention_and_storage", {})
    
    keep_count = ret_cfg.get("keep_active_payloads_count", 3)
    backup_enabled = ret_cfg.get("enable_payload_backup", True)
    backup_dir = os.path.join(base_dir, ret_cfg.get("backup_folder_path", "backup/payloads"))
    payloads_dir = os.path.join(base_dir, "payloads")

    if not os.path.exists(payloads_dir):
        return

    for repo_folder in os.listdir(payloads_dir):
        repo_path = os.path.join(payloads_dir, repo_folder)
        if not os.path.isdir(repo_path) or repo_folder == "temp":
            continue

        # Récupération de tous les fichiers binaires triés par date de modification (du plus récent au plus ancien)
        files = []
        for f in os.listdir(repo_path):
            file_p = os.path.join(repo_path, f)
            if os.path.isfile(file_p) and f.endswith((".elf", ".bin")):
                files.append((file_p, os.path.getmtime(file_p)))

        files.sort(key=lambda x: x[1], reverse=True)

        # Si le nombre de versions dépasse la limite de rétention paramétrée
        if len(files) > keep_count:
            files_to_move = files[keep_count:]
            for file_path, _ in files_to_move:
                filename = os.path.basename(file_path)
                if backup_enabled:
                    target_backup = os.path.join(backup_dir, repo_folder)
                    os.makedirs(target_backup, exist_ok=True)
                    dest_path = os.path.join(target_backup, filename)
                    shutil.move(file_path, dest_path)
                    logging.info(f"[Module 06] Archivé vers backup/ : {filename}")
                else:
                    os.remove(file_path)
                    logging.info(f"[Module 06] Supprimé (hors limite rétention) : {filename}")

def main():
    logging.info("=== Lancement du Module 06 : Rétention & Rotation Backup ===")
    apply_retention_and_backup()
    logging.info("=== Module 06 Terminé avec succès ===")

if __name__ == "__main__":
    main()