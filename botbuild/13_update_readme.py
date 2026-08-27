#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json
from utils import get_base_dir, load_settings, logging

def update_readme():
    base_dir = get_base_dir()
    settings = load_settings()
    title = settings.get("web_and_ui", {}).get("site_title", "PS5 Repo")
    readme_path = os.path.join(base_dir, "README.md")
    
    content = f"# {title}\n\nDépôt autonome mis à jour automatiquement pour PS5 (payloads ELF/BIN et PKG).\n\n"
    content += "## Accès Rapides\n- [Quoi de neuf ?](whatsnew.md)\n- [API Payloads](api/v1/payloads.json)\n- [API PKG](api/v1/pkg.json)\n"
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    logging.info("[Module 13] README.md mis à jour.")

if __name__ == "__main__":
    update_readme()