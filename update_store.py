import os
import sys
import json
import re
import hashlib
import subprocess
import urllib.request
import html

FEED_DIR = "feed"
JSON_DIR = "json"
RSS_DIR = "rss"
PAYLOADS_ROOT = "payloads"

os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(RSS_DIR, exist_ok=True)
os.makedirs(PAYLOADS_ROOT, exist_ok=True)

all_payloads_flat_list = []
readme_rows = []
credits_list = set()

print("=== Début de la synchronisation ===")

if not os.path.exists(FEED_DIR):
    print(f"Erreur: Le dossier {FEED_DIR} n'existe pas.")
    sys.exit(1)

opml_files = [f for f in os.listdir(FEED_DIR) if f.endswith('.opml')]

for opml_file in opml_files:
    cat_tech_name = opml_file.replace('.opml', '')
    cat_display_name = cat_tech_name.replace('_', ' ').title()
    if "Hen" in cat_display_name: cat_display_name = cat_display_name.replace("Hen", "HEN")
    
    print(f"\n📁 Catégorie : {cat_display_name} ({cat_tech_name})")
    category_payloads_list = []

    with open(os.path.join(FEED_DIR, opml_file), 'r', encoding='utf-8') as f:
        content = f.read()

    outlines = re.findall(r'<outline\s+([^>]+)/>', content)
    
    for outline in outlines:
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', outline))
        title = attrs.get('title', 'Inconnu')
        xml_url = attrs.get('xmlUrl', '').strip('/')
        author = attrs.get('author', 'Inconnu')
        description = attrs.get('description', '')

        if not xml_url:
            continue

        print(f" 🔍 Analyse de {title} ({xml_url})...")
        credits_list.add(f"- **{author}** : [{title}]({xml_url})")

        version = "v1.0.0"
        downloaded = False
        
        # 1. TRAITEMENT RELEASES GITHUB
        if "github.com" in xml_url:
            repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
            if repo_match:
                repo = repo_match.group(1)
                try:
                    res_tag = subprocess.check_output(f"gh repo view {repo} --json latestRelease --jq '.latestRelease.tagName'", shell=True).decode().strip()
                    if res_tag: version = res_tag
                except:
                    pass
                
                version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                os.makedirs(target_dir, exist_ok=True)

                try:
                    print(f"   -> Téléchargement GitHub ({version})...")
                    subprocess.call(f"gh release download '{version}' --repo '{repo}' --dir '{target_dir}' --clobber 2>/dev/null", shell=True)
                    if os.listdir(target_dir):
                        downloaded = True
                except Exception as e:
                    print(f"   ⚠️ Erreur gh release: {e}")

# 2. TRAITEMENT RELEASES FORGEJO (SCAN INTÉGRAL, SÉLECTION STRICTE ET EXCLUSION PS4)
        if not downloaded and "git.etawen.dev" in xml_url:
            try:
                rss_url = f"{xml_url}/releases.atom"
                req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
                raw_atom = urllib.request.urlopen(req).read().decode('utf-8')
                
                tag_match = re.search(r'<title>[^<]*?(v?\d+\.\d+\.\d+[^<]*?)</title>', raw_atom)
                if tag_match:
                    version = tag_match.group(1).strip()
                
                version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                os.makedirs(target_dir, exist_ok=True)

                # Décodage complet des entités HTML
                decoded_atom = html.unescape(raw_atom)
                
                # On extrait TOUS les liens possibles présents dans le flux
                all_found_links = re.findall(r'href=[\'"]?([^\'" >]+)', decoded_atom)
                
                valid_file_url = None
                
                # Étape 1 : On cherche en priorité absolue un binaire pur (.elf, .bin, .pkg) sans "ps4"
                for link in all_found_links:
                    link_lower = link.lower()
                    # Exclusion stricte de la mention PS4 et des archives de code source
                    if "ps4" in link_lower or "archive" in link_lower or link_lower.endswith('.zip') or link_lower.endswith('.tar.gz'):
                        continue
                    if link_lower.endswith('.elf') or link_lower.endswith('.bin') or link_lower.endswith('.pkg'):
                        valid_file_url = link
                        break
                
                # Étape 2 : Si vraiment aucun binaire pur n'est trouvé, on cherche une archive (.zip), toujours sans "ps4"
                if not valid_file_url:
                    for link in all_found_links:
                        link_lower = link.lower()
                        if "ps4" in link_lower or "archive" in link_lower:
                            continue
                        if link_lower.endswith('.zip'):
                            valid_file_url = link
                            break

                if valid_file_url:
                    # Reconstruction de l'URL absolue si Forgejo renvoie un chemin relatif
                    if valid_file_url.startswith('/'):
                        base_url = re.match(r'(https?://[^/]+)', xml_url).group(1)
                        valid_file_url = base_url + valid_file_url
                    
                    f_name = valid_file_url.split('/')[-1]
                    if "?" in f_name: f_name = f_name.split('?')[0]
                    
                    print(f"   🎯 Cible idéale trouvée : {f_name}")
                    print(f"   -> Téléchargement en cours...")
                    urllib.request.urlretrieve(valid_file_url, os.path.join(target_dir, f_name))
                    downloaded = True
                else:
                    print("   ⚠️ Aucun fichier correspondant aux critères PS5 (.elf/.bin) n'a été localisé dans le flux.")
            except Exception as e:
                print(f"   ℹ️ Échec de l'analyse du flux Forgejo ({e}), bascule sur l'API des Tags...")

            # Secours via l'API des Tags (uniquement si rien n'a été pris sur le flux)
            if not downloaded:
                try:
                    api_repo_match = re.search(r'git\.etawen\.dev/([^/]+/[^/]+)', xml_url)
                    if api_repo_match:
                        repo_path = api_repo_match.group(1)
                        api_url = f"https://git.etawen.dev/api/v1/repos/{repo_path}/tags"
                        
                        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req) as response:
                            tags_data = json.loads(response.read().decode('utf-8'))
                            if tags_data:
                                version = tags_data[0].get('name', 'v1.0.0')
                                zip_url = tags_data[0].get('zipball_url', '')
                                if zip_url and "ps4" not in zip_url.lower():
                                    version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                                    target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                                    os.makedirs(target_dir, exist_ok=True)
                                    f_name = f"{title.replace(' ', '_')}_{version_clean}.zip"
                                    print(f"   -> [Secours Tag] Archive récupérée : {f_name}")
                                    urllib.request.urlretrieve(zip_url, os.path.join(target_dir, f_name))
                                    downloaded = True
                except Exception as api_err:
                    print(f"   ⚠️ Échec complet Forgejo pour {title}: {api_err}")

        # ANALYSE ET CALCUL SHA-256
        version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
        target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
        
        files_in_dir = os.listdir(target_dir) if os.path.exists(target_dir) else []
        main_file = None
        sha256_hash = ""

        for f_name in files_in_dir:
            if f_name.endswith('.elf') or f_name.endswith('.bin'):
                main_file = f_name
                full_path = os.path.join(target_dir, f_name)
                hasher = hashlib.sha256()
                with open(full_path, 'rb') as fb:
                    for chunk in iter(lambda: fb.read(4096), b""): 
                        hasher.update(chunk)
                sha256_hash = hasher.hexdigest()
                break

        if not main_file:
            for f_name in files_in_dir:
                if f_name.endswith('.zip') or f_name.endswith('.pkg') or f_name.endswith('.tar.gz'):
                    main_file = f_name
                    sha256_hash = "N/A (Archive)"
                    break

        if main_file:
            repo_name = os.environ.get('GITHUB_REPOSITORY', 'PS5-Super-PLDMGR-Auto-Updater').split('/')[-1]
            file_url = f"https://nexgen999.github.io/{repo_name}/{target_dir.replace(os.sep, '/')}/{main_file}"

            item_data = {
                "title": title,
                "author": author,
                "version": version,
                "url": file_url,
                "sha256": sha256_hash,
                "description": description
            }
            category_payloads_list.append(item_data)
            all_payloads_flat_list.append(item_data)
            
            repo_folder_url = f"https://github.com/nexgen999/{repo_name}/tree/main/{target_dir.replace(os.sep, '/')}"
            readme_rows.append(f"| **{title}** | {author} | {cat_display_name} | [{version}]({repo_folder_url}) | `{sha256_hash[:10]}...` | {description} |")

    # Sauvegarde JSON Catégorie
    cat_final_json = {
        "name": f"{cat_tech_name} (PLDMGR Updater)",
        "payloads": category_payloads_list
    }
    with open(os.path.join(JSON_DIR, f"{cat_tech_name}.json"), 'w', encoding='utf-8') as out_cat:
        json.dump(cat_final_json, out_cat, indent=2, ensure_ascii=False)

# Sauvegarde JSON Global
repo_name = os.environ.get('GITHUB_REPOSITORY', 'PS5-Super-PLDMGR-Auto-Updater').split('/')[-1]
global_flat_json = {
    "name": "PS5 Super PLDMGR Updater",
    "payloads": all_payloads_flat_list
}
with open(os.path.join(JSON_DIR, "payloads.json"), 'w', encoding='utf-8') as out_glob:
    json.dump(global_flat_json, out_glob, indent=2, ensure_ascii=False)

# GENERATION DES FICHIERS DANS RSS/ (Flux & OPML Global)
print("\n📡 Génération des flux RSS et OPML...")
# 1. OPML Global Réseau
with open(os.path.join(RSS_DIR, "store-global.opml"), "w", encoding="utf-8") as opml_out:
    opml_out.write('<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0">\n  <head>\n    <title>PS5 Store Global Radar</title>\n  </head>\n  <body>\n')
    for row in sorted(list(credits_list)):
        # Extrait le titre et l'url brute pour reconstruire proprement l'OPML
        match = re.search(r'\*\*([^*]+)\*\*\s*:\s*\[([^\]]+)\]\(([^)]+)\)', row)
        if match:
            author_name, title_name, raw_url = match.group(1), match.group(2), match.group(3)
            opml_out.write(f'    <outline text="{title_name}" title="{title_name}" type="rss" xmlUrl="{raw_url}" author="{author_name}"/>\n')
    opml_out.write('  </body>\n</opml>')

# 2. Flux XML d'actualités basique
with open(os.path.join(RSS_DIR, "feed.xml"), "w", encoding="utf-8") as feed_out:
    feed_out.write('<?xml version="1.0" encoding="UTF-8" ?>\n<rss version="2.0">\n  <channel>\n    <title>PS5 Mini-Store Mises à jour</title>\n')
    feed_out.write(f'    <link>https://nexgen999.github.io/{repo_name}/</link>\n    <description>Suivi automatique des payloads</description>\n')
    for item in all_payloads_flat_list:
        feed_out.write('    <item>\n')
        feed_out.write(f'      <title>{item["title"]} ({item["version"]})</title>\n')
        feed_out.write(f'      <link>{item["url"]}</link>\n')
        feed_out.write(f'      <description>{item["description"]} - SHA256: {item["sha256"]}</description>\n')
        feed_out.write('    </item>\n')
    feed_out.write('  </channel>\n</rss>')

# REGENERATION STRUCTURELLE ET COMPLÈTE DU README (Avec tes instructions pour payloads.json)
with open("README.md", "w", encoding="utf-8") as r_file:
    r_file.write("# 🎮 PS5 Payload Manager & Mini-Store\n\n")
    r_file.write("![Logo ou Bannière](assets/banner.png)\n\n")
    r_file.write("Bienvenue sur mon écosystème automatisé pour la scène jailbreak PS5 ! Ce dépôt fait office de **back-end et de serveur de distribution** pour mon application PS5.\n\n")
    r_file.write("Toutes les X heures, un robot vérifie les dépôts officiels des développeurs, télécharge les derniers payloads, calcule leur empreinte de sécurité (SHA-256) et génère les index JSON nécessaires au fonctionnement du store sur la console.\n\n")
    r_file.write("> 💡 **Configuration du Store sur l'application PS5 :** Pour connecter votre console, vous devez ajouter le fichier central **`payloads.json`** disponible à l'adresse de téléchargement direct suivante :\n")
    r_file.write(f"> `https://nexgen999.github.io/{repo_name}/json/payloads.json`\n\n")
    r_file.write("---\n\n")
    r_file.write("## 📱 Flux RSS & Alertes (Notifications Mobile / PC)\n")
    r_file.write("Vous pouvez suivre l'actualité du store directement depuis votre lecteur RSS favoris :\n")
    r_file.write("* **Radar Global (Fichier OPML à importer) :** `rss/store-global.opml`\n")
    r_file.write("* **Flux de mises à jour (Notifications en temps réel) :** `rss/feed.xml`\n\n")
    r_file.write("---\n\n")
    r_file.write("## 📦 Liste des Applications & Payloads disponibles\n\n")
    r_file.write("| Application | Auteur | Catégorie | Version (Dépôt) | Empreinte SHA-256 | Description |\n")
    r_file.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    r_file.write("\n".join(readme_rows) + "\n\n")
    r_file.write("---\n\n")
    r_file.write("## 🤝 Crédits & Remerciements\n")
    r_file.write("Ce store ne serait rien sans le travail incroyable des développeurs de la scène PS5. Retrouvez ci-dessous les liens vers leurs projets originaux :\n\n")
    r_file.write("\n".join(sorted(list(credits_list))) + "\n\n")
    r_file.write("---\n")
    r_file.write("*Dépôt 100% autonome géré par GitHub Actions.*\n")

print("=== Synchronisation terminée ===")
