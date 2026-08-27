#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
from utils import get_base_dir, logging

def git_commit_push():
    base_dir = get_base_dir()
    try:
        subprocess.run(["git", "add", "."], cwd=base_dir, check=True)
        subprocess.run(["git", "commit", "-m", "auto: synchro du dépôt"], cwd=base_dir)
        subprocess.run(["git", "push"], cwd=base_dir)
        logging.info("[Module 14] Git commit et push exécutés avec succès.")
    except Exception as e:
        logging.warning(f"[Module 14] Git push ignoré ou non configuré localement : {e}")

if __name__ == "__main__":
    git_commit_push()