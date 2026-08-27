import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_script(script_name):
    script_path = os.path.join("botbuild", script_name)
    logging.info(f"--- Execution de {script_path} ---")
    
    if not os.path.exists(script_path):
        logging.warning(f"Fichier introuvable : {script_path}, passage au module suivant.")
        return

    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        logging.error(f"Erreur lors de l'execution de {script_name}")
        raise RuntimeError(f"Echec du script {script_name}")

if __name__ == "__main__":
    logging.info("Lancement du pipeline complet PS5 Super PLDMGR Auto Updater (15 modules)...")
    
    # 1. Traitement des Payloads (.elf / .bin)
    run_script("01_update_payload_rules.py")
    run_script("02_update_payload.py")
    
    # 2. Traitement des PKG
    run_script("03_update_pkg_rules.py")
    run_script("04_update_pkg.py")
    
    # 3. Flux RSS & OPML
    run_script("05_update_rss.py")
    run_script("15_generate_opml.py")
    
    # 4. Nettoyage initial et structuration de l'API JSON
    run_script("06_clean_repository.py")
    run_script("07_build_api_json.py")
    
    # 5. Interface, Changements & Validation
    run_script("08_generate_whatsnew.py")
    run_script("11_build_index_html.py")
    run_script("12_validate_json.py")
    run_script("13_update_readme.py")
    
    # 6. Archivage, Backup local & Notifications
    run_script("10_create_zip_archives.py")
    run_script("09_discord_webhook.py")
    
    # 7. Validation Git (Commit & Push des changements sur GitHub)
    run_script("14_git_commit_push.py")
    
    logging.info("Les 15 modules ont ete executes avec succes !")
