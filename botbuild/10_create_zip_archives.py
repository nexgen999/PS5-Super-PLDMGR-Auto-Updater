import os
import json
import shutil
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def build_zip_archives():
    dist_dir = "dist"
    backup_payloads = "backup/payloads"
    backup_pkg = "backup/pkg"

    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(backup_payloads, exist_ok=True)
    os.makedirs(backup_pkg, exist_ok=True)

    # -------------------------------------------------------------
    # 1. PAYLOADS AIO (Uniquement les dernières versions actives de payloads.json)
    # -------------------------------------------------------------
    payloads_zip_path = os.path.join(dist_dir, "payloads_aio.zip")
    active_files = set()

    if os.path.exists("payloads.json"):
        with open("payloads.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # Récupération des chemins exacts des fichiers actifs
            for item in data.get("payloads", []):
                if "path" in item:
                    active_files.add(os.path.normpath(item["path"]))

    with zipfile.ZipFile(payloads_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists("payloads"):
            for root, _, files in os.walk("payloads"):
                for file in files:
                    file_path = os.path.normpath(os.path.join(root, file))
                    # Si le fichier fait partie des versions actives
                    if file_path in active_files or not active_files:
                        arcname = os.path.relpath(file_path, "payloads")
                        zipf.write(file_path, arcname)
                    else:
                        # 6. Déplacement des anciennes versions vers backup/payloads/
                        backup_target = os.path.join(backup_payloads, os.path.relpath(file_path, "payloads"))
                        os.makedirs(os.path.dirname(backup_target), exist_ok=True)
                        shutil.move(file_path, backup_target)
                        logging.info(f"Ancienne version déplacée dans backup : {file_path}")

    # -------------------------------------------------------------
    # 2. PKG AIO (Inclusion des PKG pour la release)
    # -------------------------------------------------------------
    pkg_zip_path = os.path.join(dist_dir, "pkg_aio.zip")
    with zipfile.ZipFile(pkg_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists("pkg"):
            for root, _, files in os.walk("pkg"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, "pkg")
                    zipf.write(file_path, arcname)

    # -------------------------------------------------------------
    # 3. STORE TEMPLATE (Moteur complet du dépôt)
    # -------------------------------------------------------------
    template_name = "PS5_Super_PLDMGR_Store_Template"
    template_zip_path = os.path.join(dist_dir, f"{template_name}.zip")

    # Éléments constituant le moteur du store
    engine_elements = [
        "botbuild",
        ".github",
        "feed",
        "PKGfeed",
        "requirements.txt",
        "README.md",
        "LICENSE",
        ".gitignore"
    ]

    with zipfile.ZipFile(template_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in engine_elements:
            if os.path.isdir(item):
                for root, _, files in os.walk(item):
                    for file in files:
                        fp = os.path.join(root, file)
                        zipf.write(fp, fp)
            elif os.path.isfile(item):
                zipf.write(item, item)

    logging.info("Toutes les archives (Payloads AIO, PKG AIO, Store Template) ont été générées.")

if __name__ == "__main__":
    build_zip_archives()
