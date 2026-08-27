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

    # 1. Archive AIO Payloads
    if os.path.exists("payloads"):
        shutil.make_archive(f"{dist_dir}/payloads_aio", 'zip', "payloads")
        shutil.copy(f"{dist_dir}/payloads_aio.zip", f"{backup_payloads}/payloads_aio.zip")

    # 2. Archive AIO PKG
    if os.path.exists("pkg"):
        shutil.make_archive(f"{dist_dir}/pkg_aio.zip", 'zip', "pkg")
        shutil.copy(f"{dist_dir}/pkg_aio.zip", f"{backup_pkg}/pkg_aio.zip")

    # 3. Archive Template Store Global (payloads + json + config)
    template_name = "PS5_Super_PLDMGR_Store_Template"
    with zipfile.ZipFile(f"{dist_dir}/{template_name}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder in ["payloads", "pkg"]:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        fp = os.path.join(root, file)
                        zipf.write(fp, os.path.relpath(fp, "."))
        for json_file in ["payloads.json", "pkg.json"]:
            if os.path.exists(json_file):
                zipf.write(json_file, json_file)

    shutil.copy(f"{dist_dir}/{template_name}.zip", f"{backup_payloads}/{template_name}.zip")
    logging.info("Les 3 archives ZIP ont ete creees et sauvegardees.")

if __name__ == "__main__":
    build_zip_archives()
