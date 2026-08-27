import os
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

    # 1. Archive AIO Payloads (créée uniquement si le dossier payloads existe)
    if os.path.exists("payloads") and os.listdir("payloads"):
        zip_payloads = shutil.make_archive(f"{dist_dir}/payloads_aio", 'zip', "payloads")
        if os.path.exists(zip_payloads):
            shutil.copy(zip_payloads, f"{backup_payloads}/payloads_aio.zip")
            logging.info("Archive payloads_aio.zip créée et sauvegardée.")

    # 2. Archive AIO PKG (créée uniquement si le dossier pkg existe et n'est pas vide)
    if os.path.exists("pkg") and os.listdir("pkg"):
        zip_pkg = shutil.make_archive(f"{dist_dir}/pkg_aio", 'zip', "pkg")
        if os.path.exists(zip_pkg):
            shutil.copy(zip_pkg, f"{backup_pkg}/pkg_aio.zip")
            logging.info("Archive pkg_aio.zip créée et sauvegardée.")
    else:
        logging.warning("Le dossier pkg est vide ou inexistant, création d'une archive pkg_aio.zip vide par sécurité.")
        # Crée un zip vide pour éviter que le job GitHub Release ne plante s'il attend ce fichier
        with zipfile.ZipFile(f"{dist_dir}/pkg_aio.zip", 'w') as zipf:
            pass
        shutil.copy(f"{dist_dir}/pkg_aio.zip", f"{backup_pkg}/pkg_aio.zip")

    # 3. Archive Template Store Global
    template_name = "PS5_Super_PLDMGR_Store_Template"
    template_zip_path = f"{dist_dir}/{template_name}.zip"
    
    with zipfile.ZipFile(template_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder in ["payloads", "pkg"]:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files:
                        fp = os.path.join(root, file)
                        zipf.write(fp, os.path.relpath(fp, "."))
        for json_file in ["payloads.json", "pkg.json"]:
            if os.path.exists(json_file):
                zipf.write(json_file, json_file)

    if os.path.exists(template_zip_path):
        shutil.copy(template_zip_path, f"{backup_payloads}/{template_name}.zip")
        logging.info(f"Archive {template_name}.zip créée et sauvegardée.")

if __name__ == "__main__":
    build_zip_archives()
