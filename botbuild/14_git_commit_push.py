#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
from utils import get_base_dir, logging

def git_commit_push():
    base_dir = get_base_dir()
    try:
        # 1. Verification du statut
        status = subprocess.run(
            ["git", "status", "--porcelain"], 
            cwd=base_dir, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        if not status.stdout.strip():
            logging.info("[Module 14] Aucun changement a commiter.")
            return

        # 2. Ajout selectif des fichiers legers de metadata et du depot
        # Le fichier .gitignore se charge de bloquer dist/, pkg/ et les .zip
        files_to_add = [
            "payloads.json",
            "pkg.json",
            "README.md",
            "whatsnew.md",
            "PS5_Repository_Feeds.opml",
            "rss/",
            "feed/",
            "PKGfeed/",
            "payloads/"
        ]

        for file_item in files_to_add:
            subprocess.run(["git", "add", file_item], cwd=base_dir, stderr=subprocess.DEVNULL)

        # 3. Commit
        commit_res = subprocess.run(
            ["git", "commit", "-m", "auto: synchro automatique du depot"], 
            cwd=base_dir, 
            capture_output=True, 
            text=True
        )

        if "nothing to commit" in commit_res.stdout:
            logging.info("[Module 14] Rien a commiter.")
            return

        # 4. Push vers le depot distant
        subprocess.run(["git", "push"], cwd=base_dir, check=True)
        logging.info("[Module 14] Git commit et push executes avec succes.")

    except Exception as e:
        logging.warning(f"[Module 14] Git push ignore ou non configure localement : {e}")

if __name__ == "__main__":
    git_commit_push()
