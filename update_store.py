import xml.etree.ElementTree as ET
import os
import re
import urllib.request
import zipfile
import subprocess
import json

# ==============================================================================
# CONFIGURATION ET CONSTANTES
# ==============================================================================
FEED_URL = "https://raw.githubusercontent.com/LightningMods/Store-Meta/refs/heads/main/db.xml"
LOCAL_XML = "db.xml"
PAYLOADS_ROOT = "Payloads"

# Listes des dépôts nécessitant une extraction d'archives ZIP
ZIP_EXTRACTION_REPOS = [
    "poords4", 
    "fan_target", 
    "shadowmountplus", 
    "instalador-host-psm-poop2jb"
]

# Listes des dépôts à filtrage strict (uniquement .elf et .bin)
STRICT_BIN_ELF_REPOS = [
    "ps5-payload-dev/websrv", 
    "phantomptr/ps5upload", 
    "boazvdwansem/ps5-debugger", 
    "smoxa/ps5-new-overlay"
]

# Extensions de fichiers indésirables à nettoyer automatiquement
DISCARD_EXTENSIONS = ['.dmg', '.exe', '.appimage', '.msi', '.txt', '.md', '.json', '.yml', '.yaml']

# Instances alternatives basées sur Forgejo / Gitea
FORGEJO_HOSTS = ["brewser.com", "pkg-zone.com", "gitea", "forgejo"]

# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================
def clean_tag(tag):
    """
    Supprime le namespace XML ({http...}) pour faciliter le ciblage des balises.
    """
    if '}' in tag:
        return tag.split('}')[-1]
    return tag


def sanitize_filename(name):
    """
    Nettoie une chaîne de caractères pour l'utiliser comme nom de dossier/fichier.
    """
    cleaned = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    return re.sub(r'_+', '_', cleaned).strip('_')


def fetch_db():
    """
    Télécharge la base de données XML si elle n'existe pas localement.
    """
    print("----------------------------------------------------------------------")
    if not os.path.exists(LOCAL_XML):
        print(f"[*] Téléchargement du fichier de base de données depuis : {FEED_URL}")
        try:
            urllib.request.urlretrieve(FEED_URL, LOCAL_XML)
            print("[+] Base de données XML téléchargée avec succès.")
        except Exception as e:
            print(f"[!] Erreur critique lors du téléchargement de db.xml : {e}")
            exit(1)
    else:
        print(f"[*] Fichier local '{LOCAL_XML}' trouvé et pris en compte.")
    print("----------------------------------------------------------------------")


# ==============================================================================
# TRAITEMENT DES ARCHIVES ET NETTOYAGE
# ==============================================================================
def process_zip_extractions(target_dir, repo_lower):
    """
    Inspecte le dossier cible à la recherche d'archives ZIP et extrait les .elf.
    """
    should_extract = any(repo_key in repo_lower for repo_key in ZIP_EXTRACTION_REPOS)
    
    if not should_extract:
        return

    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        if item.lower().endswith('.zip'):
            print(f"    [-->] Extraction d'archive détectée : {item}")
            try:
                with zipfile.ZipFile(item_path, 'r') as zf:
                    for member in zf.namelist():
                        if member.lower().endswith('.elf'):
                            zf.extract(member, target_dir)
                            extracted_path = os.path.join(target_dir, member)
                            dest_path = os.path.join(target_dir, os.path.basename(member))
                            
                            # Déplacement à la racine du dossier cible si sous-dossier
                            if extracted_path != dest_path:
                                if os.path.exists(dest_path):
                                    os.remove(dest_path)
                                os.rename(extracted_path, dest_path)
                            print(f"        [+] Extrait avec succès : {os.path.basename(member)}")
            except Exception as zerr:
                print(f"    [!] Erreur lors de l'extraction ZIP ({item}) : {zerr}")
            finally:
                if os.path.exists(item_path):
                    os.remove(item_path)


def clean_unwanted_files(target_dir, repo_lower):
    """
    Nettoie les fichiers binaires non PS5 ou inutiles téléchargés dans les releases.
    """
    if not os.path.exists(target_dir):
        return

    files_downloaded = os.listdir(target_dir)
    is_strict = any(strict_repo in repo_lower for strict_repo in STRICT_BIN_ELF_REPOS)

    for file in files_downloaded:
        file_path = os.path.join(target_dir, file)
        if os.path.isdir(file_path):
            continue

        f_lower = file.lower()

        if is_strict:
            # Mode strict : conserve uniquement .elf et .bin
            if not (f_lower.endswith('.elf') or f_lower.endswith('.bin')):
                try:
                    os.remove(file_path)
                    print(f"    [-] Nettoyage (mode strict) : {file}")
                except Exception as e:
                    print(f"    [!] Impossible de supprimer {file} : {e}")
        else:
            # Mode standard : conserve les payloads et supprime les exécutables PC/Mac/docs
            if f_lower.endswith('.elf') or f_lower.endswith('.bin'):
                continue
            
            if any(f_lower.endswith(ext) for ext in DISCARD_EXTENSIONS):
                try:
                    os.remove(file_path)
                    print(f"    [-] Nettoyage binaire PC/Mac : {file}")
                except Exception as e:
                    print(f"    [!] Impossible de supprimer {file} : {e}")


# ==============================================================================
# LOGIQUE PRINCIPALE DU PARSER
# ==============================================================================
def parse_and_download():
    """
    Parcourt l'arbre XML et déclenche le protocole de téléchargement adapté.
    """
    try:
        tree = ET.parse(LOCAL_XML)
        root = tree.getroot()
    except Exception as parse_err:
        print(f"[!] Erreur de lecture du fichier XML : {parse_err}")
        return

    items = [elem for elem in root.iter() if clean_tag(elem.tag) == "item"]
    print(f"[*] Traitement de {len(items)} éléments dans la base de données...")

    for index, item in enumerate(items, start=1):
        title = ""
        category_name = ""
        version = "v1.0"
        xml_url = ""

        # Lecture des sous-éléments de chaque <item>
        for child in item:
            tag = clean_tag(child.tag)
            text = child.text.strip() if child.text else ""

            if tag == "title":
                title = text
            elif tag == "category":
                category_name = text
            elif tag == "version":
                if text:
                    version = text
            elif tag == "enclosure":
                xml_url = child.attrib.get('url', '')

        # Filtrage : On n'embarque que les catégories liées aux Payloads
        if "payload" not in category_name.lower():
            continue

        cat_tech_name = category_name.replace(" ", "_")
        downloaded = False

        print(f"\n======================================================================")
        print(f"[{index}/{len(items)}] TRAITEMENT : {title}")
        print(f"    -> Catégorie : {category_name}")
        print(f"    -> Version XML : {version}")
        print(f"    -> URL source  : {xml_url}")
        print(f"======================================================================")

        # ----------------------------------------------------------------------
        # STRATÉGIE 1 : Lien Direct pointant sur un fichier .elf
        # ----------------------------------------------------------------------
        if xml_url.lower().endswith('.elf'):
            version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
            target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
            os.makedirs(target_dir, exist_ok=True)
            
            filename = os.path.basename(xml_url)
            file_path = os.path.join(target_dir, filename)

            try:
                print(f"   [+] Exécution Stratégie 1 (Lien direct .elf)...")
                urllib.request.urlretrieve(xml_url, file_path)
                print(f"   [✓] Fichier téléchargé : {filename}")
                downloaded = True
            except Exception as e:
                print(f"   [!] Erreur Téléchargement Direct : {e}")

        # ----------------------------------------------------------------------
        # STRATÉGIE 2 : Plateformes Forgejo / Gitea (Brewser, Pkg-Zone, etc.)
        # ----------------------------------------------------------------------
        if not downloaded and any(host in xml_url.lower() for host in FORGEJO_HOSTS):
            try:
                match = re.search(r'https?://([^/]+)/([^/]+/[^/]+)', xml_url)
                if match:
                    domain = match.group(1)
                    repo = match.group(2).rstrip('/')
                    
                    print(f"   [+] Exécution Stratégie 2 (Forgejo/Gitea sur {domain})...")
                    api_url = f"https://{domain}/api/v1/repos/{repo}/releases/latest"
                    
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as resp:
                        rel_data = json.loads(resp.read().decode('utf-8'))
                        version = rel_data.get('tag_name', version)
                        version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                        
                        target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                        os.makedirs(target_dir, exist_ok=True)

                        for asset in rel_data.get('assets', []):
                            asset_name = asset.get('name', '')
                            download_url = asset.get('browser_download_url', '')
                            
                            if asset_name.lower().endswith(('.elf', '.bin', '.zip')):
                                print(f"       [-->] Téléchargement asset : {asset_name}")
                                dest_file = os.path.join(target_dir, asset_name)
                                urllib.request.urlretrieve(download_url, dest_file)
                                
                                # Traitement des zips téléchargés via Forgejo
                                if asset_name.lower().endswith('.zip'):
                                    try:
                                        with zipfile.ZipFile(dest_file, 'r') as zf:
                                            zf.extractall(target_dir)
                                        os.remove(dest_file)
                                    except Exception as ze:
                                        print(f"       [!] Erreur extraction ZIP Forgejo : {ze}")
                                downloaded = True
            except Exception as fe:
                print(f"   [!] Erreur durant le processus Forgejo/Gitea : {fe}")

        # ----------------------------------------------------------------------
        # STRATÉGIE 3 : Dépôts GitHub (Releases GitHub / GitHub CLI / API)
        # ----------------------------------------------------------------------
        repo_lower = ""
        if not downloaded and "github.com" in xml_url:
            repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
            if repo_match:
                repo = repo_match.group(1)
                repo_lower = repo.lower()
                
                # Récupération de la dernière version via GH CLI
                try:
                    res_tag = subprocess.check_output(
                        f"gh release list --repo {repo} --limit 1 --json tagName --jq '.[0].tagName'", 
                        shell=True
                    ).decode().strip()
                    if res_tag: 
                        version = res_tag
                    else:
                        res_tag = subprocess.check_output(
                            f"gh repo view {repo} --json latestRelease --jq '.latestRelease.tagName'", 
                            shell=True
                        ).decode().strip()
                        if res_tag: 
                            version = res_tag
                except Exception:
                    pass
                
                version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                os.makedirs(target_dir, exist_ok=True)

                try:
                    print(f"   [+] Exécution Stratégie 3 (GitHub Release v{version})...")
                    
                    # Cas d'exception API directe pour smoxa/ps5-new-overlay
                    if "smoxa/ps5-new-overlay" in repo_lower:
                        try:
                            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req) as resp:
                                rel_data = json.loads(resp.read().decode('utf-8'))
                                version = rel_data.get('tag_name', version)
                                version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                                
                                target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                                os.makedirs(target_dir, exist_ok=True)

                                for asset in rel_data.get('assets', []):
                                    asset_name = asset.get('name', '')
                                    download_url = asset.get('browser_download_url', '')
                                    if asset_name.lower().endswith('.elf'):
                                        print(f"       [-->] Récupération API GitHub : {asset_name}")
                                        urllib.request.urlretrieve(download_url, os.path.join(target_dir, asset_name))
                                        downloaded = True
                        except Exception as overlay_err:
                            print(f"       [!] Échec récupération via API Overlay : {overlay_err}")
                    else:
                        # Téléchargement standard via GitHub CLI (Shadowmount, etc.)
                        subprocess.call(
                            f"gh release download '{version}' --repo '{repo}' --dir '{target_dir}' --clobber 2>/devnull", 
                            shell=True
                        )

                    # Post-traitements (Extractions ZIP spécifiques & Nettoyage de dossier)
                    process_zip_extractions(target_dir, repo_lower)
                    clean_unwanted_files(target_dir, repo_lower)

                    if os.path.exists(target_dir) and os.listdir(target_dir):
                        downloaded = True
                except Exception as e:
                    print(f"   [!] Erreur lors de l'exécution GH Release : {e}")

        # ----------------------------------------------------------------------
        # STRATÉGIE 4 : Mode Dégradé / Repli Direct sur l'URL de l'enclosure
        # ----------------------------------------------------------------------
        if not downloaded and xml_url:
            version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
            target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
            os.makedirs(target_dir, exist_ok=True)
            
            try:
                print(f"   [+] Exécution Stratégie 4 (Repli URL directe)...")
                archive_name = os.path.basename(xml_url) or "payload.bin"
                archive_path = os.path.join(target_dir, archive_name)
                
                urllib.request.urlretrieve(xml_url, archive_path)
                
                if archive_name.lower().endswith('.zip'):
                    with zipfile.ZipFile(archive_path, 'r') as zf:
                        zf.extractall(target_dir)
                    os.remove(archive_path)
                print(f"   [✓] Fichier de repli récupéré : {archive_name}")
            except Exception as e:
                print(f"   [!] Échec global du téléchargement : {e}")


# ==============================================================================
# POINT D'ENTRÉE DU SCRIPT
# ==============================================================================
if __name__ == "__main__":
    fetch_db()
    parse_and_download()
    print("\n======================================================================")
    print("      ✅ TRAITEMENT COMPLET TERMINÉ ET LOGS GÉNÉRÉS SUR LA CONSOLE")
    print("======================================================================\n")
