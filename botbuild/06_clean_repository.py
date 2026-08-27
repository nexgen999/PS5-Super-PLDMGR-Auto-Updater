import os
import shutil
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clean_local_temp_files():
    """Nettoie les dossiers temporaires et de cache locaux."""
    temp_dirs = ["tmp", "temp", "cache", "__pycache__"]
    for d in temp_dirs:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
            logging.info(f"Dossier temporaire supprime : {d}")

def clean_github_releases(repo_slug="nexgen999/PS5-Super-PLDMGR-Auto-Updater", max_keep=3):
    """
    Conserve uniquement les `max_keep` dernieres releases sur GitHub et supprime les plus anciennes.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logging.warning("GITHUB_TOKEN non defini, nettoyage des releases distantes ignore.")
        return

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{repo_slug}/releases"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Echec de recuperation des releases: {response.status_code}")
            return

        releases = response.json()
        # Conserver la release fixe 'latest' et purger le surplus d'anciennes releases horodatees
        releases_to_clean = [r for r in releases if r.get("tag_name") != "latest"]

        if len(releases_to_clean) > max_keep:
            for old_release in releases_to_clean[max_keep:]:
                rel_id = old_release["id"]
                tag_name = old_release["tag_name"]
                del_url = f"https://api.github.com/repos/{repo_slug}/releases/{rel_id}"
                del_resp = requests.delete(del_url, headers=headers)
                if del_resp.status_code in [204, 200]:
                    logging.info(f"Ancienne release supprimee sur GitHub : {tag_name} (ID: {rel_id})")
                else:
                    logging.warning(f"Impossible de supprimer la release {tag_name}: {del_resp.status_code}")
    except Exception as e:
        logging.error(f"Erreur lors du nettoyage des releases GitHub: {e}")

if __name__ == "__main__":
    logging.info("Execution du module 06_clean_repository...")
    clean_local_temp_files()
    clean_github_releases()
