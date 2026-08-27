import os
import sys
import json
import shutil
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

SETTINGS_PATH = os.path.join(ROOT_DIR, "settings.json")

def load_settings():
    defaults = {
        "payloads_dir": "payloads",
        "backup_payloads_dir": "backup/payloads",
        "backup_pkg_dir": "backup/pkg",
        "payloads_zip_name": "payloads_aio.zip",
        "pkg_zip_name": "pkg_aio.zip",
        "template_zip_name": "PS5_Super_PLDMGR_Store_Template.zip"
    }
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
                logging.info("[Module 10] Configuration settings.json chargée.")
        except Exception as e:
            logging.warning(f"[Module 10] Erreur de lecture de settings.json : {e}")
    return defaults

def build_zip_archives():
    cfg = load_settings()
    
    payloads_dir = os.path.join(ROOT_DIR, cfg.get("payloads_dir", "payloads"))
    backup_payloads = os.path.join(ROOT_DIR, cfg.get("backup_payloads_dir", "backup/payloads"))
    dist_dir = os.path.join(ROOT_DIR, "dist")
    
    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(backup_payloads, exist_ok=True)

    # 1. Archive Payloads AIO (Seulement les fichiers actifs + Backup du reste)
    payloads_zip_name = cfg.get("payloads_zip_name", "payloads_aio.zip")
    if not payloads_zip_name.endswith(".zip"):
        payloads_zip_name += ".zip"
    payloads_zip_path = os.path.join(dist_dir, payloads_zip_name)

    active_files = set()
    payloads_json_path = os.path.join(ROOT_DIR, "payloads.json")
    if os.path.exists(payloads_json_path):
        with open(payloads_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("payloads", []):
                file_name = item.get("file_name")
                if file_name:
                    active_files.add(file_name)

    with zipfile.ZipFile(payloads_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(payloads_dir):
            for root, _, files in os.walk(payloads_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, payloads_dir)
                    
                    if file in active_files or not active_files:
                        zipf.write(file_path, rel_path)
                    else:
                        # Ancienne version -> Déplacement dans backup/payloads/
                        target_backup = os.path.join(backup_payloads, rel_path)
                        os.makedirs(os.path.dirname(target_backup), exist_ok=True)
                        shutil.move(file_path, target_backup)
                        logging.info(f"[Module 10] Déplacé dans backup : {file}")

    # 2. Archive PKG AIO
    pkg_zip_name = cfg.get("pkg_zip_name", "pkg_aio.zip")
    if not pkg_zip_name.endswith(".zip"):
        pkg_zip_name += ".zip"
    pkg_zip_path = os.path.join(dist_dir, pkg_zip_name)
    pkg_dir = os.path.join(ROOT_DIR, "pkg")

    with zipfile.ZipFile(pkg_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(pkg_dir):
            for root, _, files in os.walk(pkg_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, pkg_dir)
                    zipf.write(file_path, rel_path)

    # 3. Archive Template Store (Uniquement le moteur du dépôt)
    template_zip_name = cfg.get("template_zip_name", "PS5_Super_PLDMGR_Store_Template.zip")
    if not template_zip_name.endswith(".zip"):
        template_zip_name += ".zip"
    template_zip_path = os.path.join(dist_dir, template_zip_name)

    engine_items = ["botbuild", ".github", "feed", "PKGfeed", "requirements.txt", "README.md", "settings.json", ".gitignore"]
    with zipfile.ZipFile(template_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in engine_items:
            full_item_path = os.path.join(ROOT_DIR, item)
            if os.path.isdir(full_item_path):
                for root, _, files in os.walk(full_item_path):
                    for file in files:
                        fp = os.path.join(root, file)
                        rel_fp = os.path.relpath(fp, ROOT_DIR)
                        zipf.write(fp, rel_fp)
            elif os.path.isfile(full_item_path):
                zipf.write(full_item_path, item)

    logging.info(f"[Module 10] Archives crées avec succès dans {dist_dir}")

if __name__ == "__main__":
    build_zip_archives()
