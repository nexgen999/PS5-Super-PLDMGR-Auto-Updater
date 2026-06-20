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

        if "ps4" in title.lower() or "ps4" in description.lower():
            print(f" 🚫 Ignoré (Critère d'exclusion PS4 trouvé dans {title})")
            continue

        print(f" 🔍 Analyse de {title} ({xml_url})...")

        version = "v1.0.0"
        downloaded = False
        
        # 0. TRAITEMENT DES SOURCES FIXES
        clean_xml_url = xml_url.split('?')[0].lower()
        if clean_xml_url.endswith('.elf') or clean_xml_url.endswith('.bin') or clean_xml_url.endswith('.pkg'):
            try:
                version = "Source-Fixe"
                version_clean = "Source-Fixe"
                target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                os.makedirs(target_dir, exist_ok=True)
                
                f_name = xml_url.split('?')[0].split('/')[-1]
                print(f"   🎯 Source fixe détectée (Téléchargement Raw direct) : {f_name}")
                
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(xml_url, os.path.join(target_dir, f_name))
                downloaded = True
            except Exception as e:
                print(f"   ⚠️ Échec du téléchargement de la source fixe : {e}")

        # 1. TRAITEMENT RELEASES GITHUB
        if not downloaded and "github.com" in xml_url:
            repo_match = re.search(r'github\.com/([^/]+/[^/]+)', xml_url)
            if repo_match:
                repo = repo_match.group(1)
                try:
                    res_tag = subprocess.check_output(f"gh release list --repo {repo} --limit 1 --json tagName --jq '.[0].tagName'", shell=True).decode().strip()
                    if res_tag: 
                        version = res_tag
                    else:
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
                    
                    files_downloaded = os.listdir(target_dir)
                    repo_lower = repo.lower()
                    
                    if "ps5-payload-dev/websrv" in repo_lower or "phantomptr/ps5upload" in repo_lower:
                        print("   ⚠️ Dépôt lourd détecté : Application de la règle d'exception (.elf uniquement)")
                        for f in files_downloaded:
                            f_lower = f.lower()
                            if not f_lower.endswith('.elf'):
                                try:
                                    os.remove(os.path.join(target_dir, f))
                                except:
                                    pass
                    else:
                        for f in files_downloaded:
                            if "ps4" in f.lower():
                                os.remove(os.path.join(target_dir, f))

                    if os.listdir(target_dir):
                        downloaded = True
                except Exception as e:
                    print(f"   ⚠️ Erreur gh release: {e}")

        # 2. TRAITEMENT RELEASES FORGEJO
        if not downloaded and "git.etawen.dev" in xml_url:
            try:
                api_repo_match = re.search(r'git\.etawen\.dev/([^/]+/[^/]+)', xml_url)
                if api_repo_match:
                    repo_path = api_repo_match.group(1)
                    api_url = f"https://git.etawen.dev/api/v1/repos/{repo_path}/releases"
                    
                    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response:
                        releases_data = json.loads(response.read().decode('utf-8'))
                        
                        if releases_data:
                            latest_release = releases_data[0]
                            version = latest_release.get('tag_name', 'v1.0.0')
                            
                            version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version)
                            target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
                            os.makedirs(target_dir, exist_ok=True)
                            
                            assets = latest_release.get('assets', [])
                            valid_file_url = None
                            f_name = None
                            
                            for asset in assets:
                                asset_url = asset.get('browser_download_url', '')
                                asset_name = asset.get('name', '')
                                clean_name = asset_name.lower()
                                
                                if "ps4" in clean_name:
                                    continue
                                    
                                if clean_name.endswith('.elf') or clean_name.endswith('.bin') or clean_name.endswith('.pkg'):
                                    valid_file_url = asset_url
                                    f_name = asset_name
                                    break
                                    
                            if not valid_file_url:
                                for asset in assets:
                                    asset_url = asset.get('browser_download_url', '')
                                    asset_name = asset.get('name', '')
                                    clean_name = asset_name.lower()
                                    
                                    if "ps4" in clean_name:
                                        continue
                                        
                                    if clean_name.endswith('.zip'):
                                        valid_file_url = asset_url
                                        f_name = asset_name
                                        break
                            
                            if valid_file_url and f_name:
                                print(f"   🎯 Asset Forgejo détecté : {f_name}")
                                urllib.request.urlretrieve(valid_file_url, os.path.join(target_dir, f_name))
                                downloaded = True
            except Exception as e:
                print(f"   ℹ️ Erreur API Forgejo ({e})")

        # ANALYSE, RENOMMAGE AUTOMATIQUE ET CALCUL CHECKSUM
        version_clean = re.sub(r'[^a-zA-Z0-9._-]', '', version) if version != "Source-Fixe" else "Source-Fixe"
        target_dir = os.path.join(PAYLOADS_ROOT, cat_tech_name, title.replace(" ", "_"), version_clean)
        
        files_in_dir = os.listdir(target_dir) if os.path.exists(target_dir) else []
        main_file = None
        sha256_hash = ""

        # Formatage propre du tag de version pour le nom de fichier (ex: "0.14" -> "_v0.14", "v1.2" -> "_v1.2")
        v_suffix = version_clean
        if v_suffix != "Source-Fixe":
            if not v_suffix.lower().startswith('v'):
                v_suffix = f"v{v_suffix}"
            v_suffix = f"_{v_suffix}"
        else:
            v_suffix = ""

        for f_name in files_in_dir:
            f_name_lower = f_name.lower()
            if f_name_lower.endswith('.elf') or f_name_lower.endswith('.bin'):
                # Extraction du nom d'origine et de l'extension
                base_name, ext = os.path.splitext(f_name)
                
                # On évite de rajouter la version en boucle si elle est déjà présente dans le fichier d'origine
                if v_suffix and v_suffix in base_name:
                    new_f_name = f_name
                else:
                    new_f_name = f"{base_name}{v_suffix}{ext}"
                
                # Renommage physique du fichier sur le stockage
                old_path = os.path.join(target_dir, f_name)
                new_path = os.path.join(target_dir, new_f_name)
                if old_path != new_path:
                    try:
                        os.rename(old_path, new_path)
                        print(f"   🏷️  Fichier renommé : {f_name} -> {new_f_name}")
                    except Exception as rn_err:
                        print(f"   ⚠️ Erreur renommage : {rn_err}")
                        new_f_name = f_name
                
                main_file = new_f_name
                break

        if main_file:
            full_path = os.path.join(target_dir, main_file)
            hasher = hashlib.sha256()
            with open(full_path, 'rb') as fb:
                for chunk in iter(lambda: fb.read(4096), b""): 
                    hasher.update(chunk)
            sha256_hash = hasher.hexdigest()

            credits_list.add(f"- **{author}** : [{title}]({xml_url})")
            
            repo_name = os.environ.get('GITHUB_REPOSITORY', 'PS5-Super-PLDMGR-Auto-Updater').split('/')[-1]
            file_url = f"https://nexgen999.github.io/{repo_name}/{target_dir.replace(os.sep, '/')}/{main_file}"

            item_data = {
                "name": title,
                "filename": main_file,
                "url": file_url,
                "description": description if description else f"Payload {title} pour PS5",
                "version": version,
                "checksum": sha256_hash
            }
            category_payloads_list.append(item_data)
            all_payloads_flat_list.append(item_data)
            
            repo_folder_url = f"https://github.com/nexgen999/{repo_name}/tree/main/{target_dir.replace(os.sep, '/')}"
            readme_rows.append(f"| **{title}** | {author} | {cat_display_name} | [{version}]({repo_folder_url}) | `{sha256_hash[:10]}...` | {description} |")
        else:
            print(f"   🚫 Ignoré du JSON final car aucun binaire (.elf / .bin) détecté pour {title}")

    # Sauvegarde JSON Catégorie
    with open(os.path.join(JSON_DIR, f"{cat_tech_name}.json"), 'w', encoding='utf-8') as out_cat:
        json.dump(category_payloads_list, out_cat, indent=2, ensure_ascii=False)

# Sauvegarde JSON Global complet
with open(os.path.join(JSON_DIR, "payloads.json"), 'w', encoding='utf-8') as out_glob:
    json.dump(all_payloads_flat_list, out_glob, indent=2, ensure_ascii=False)

# GENERATION RSS & README
print("\n📡 Génération des flux RSS et OPML...")
with open(os.path.join(RSS_DIR, "store-global.opml"), "w", encoding="utf-8") as opml_out:
    opml_out.write('<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0">\n  <head>\n    <title>PS5 Store Global Radar</title>\n  </head>\n  <body>\n')
    for row in sorted(list(credits_list)):
        match = re.search(r'\*\*([^*]+)\*\*\s*:\s*\[([^\]]+)\]\(([^)]+)\)', row)
        if match:
            author_name, title_name, raw_url = match.group(1), match.group(2), match.group(3)
            opml_out.write(f'    <outline text="{title_name}" title="{title_name}" type="rss" xmlUrl="{raw_url}" author="{author_name}"/>\n')
    opml_out.write('  </body>\n</opml>')

with open(os.path.join(RSS_DIR, "feed.xml"), "w", encoding="utf-8") as feed_out:
    repo_name = os.environ.get('GITHUB_REPOSITORY', 'PS5-Super-PLDMGR-Auto-Updater').split('/')[-1]
    feed_out.write('<?xml version="1.0" encoding="UTF-8" ?>\n<rss version="2.0">\n  <channel>\n    <title>PS5 Mini-Store Mises à jour</title>\n')
    feed_out.write(f'    <link>https://nexgen999.github.io/{repo_name}/</link>\n    <description>Suivi automatique des payloads</description>\n')
    for item in all_payloads_flat_list:
        feed_out.write('    <item>\n')
        feed_out.write(f'      <title>{item["name"]} ({item["version"]})</title>\n')
        feed_out.write(f'      <link>{item["url"]}</link>\n')
        feed_out.write(f'      <description>{item["description"]} - Checksum: {item["checksum"]}</description>\n')
        feed_out.write('    </item>\n')
    feed_out.write('  </channel>\n</rss>')

with open("README.md", "w", encoding="utf-8") as r_file:
    repo_name = os.environ.get('GITHUB_REPOSITORY', 'PS5-Super-PLDMGR-Auto-Updater').split('/')[-1]
    r_file.write("# 🎮 PS5 Payload Manager & Mini-Store\n\n")
    r_file.write("Bienvenue sur mon écosystème automatisé pour la scène jailbreak PS5 !\n\n")
    r_file.write("> 💡 **Configuration du Store sur l'application PS5 :** Pour connecter votre console, ajoutez le fichier central **`payloads.json`** :\n")
    r_file.write(f"> `https://nexgen999.github.io/{repo_name}/json/payloads.json`\n\n")
    r_file.write("---\n\n")
    r_file.write("## 📱 Flux RSS & Alertes\n")
    r_file.write("* **Radar Global (OPML) :** `rss/store-global.opml`\n")
    r_file.write("* **Flux de mises à jour (XML) :** `rss/feed.xml`\n\n")
    r_file.write("---\n\n")
    r_file.write("## 📦 Liste des Applications & Payloads disponibles\n\n")
    r_file.write("| Application | Auteur | Catégorie | Version (Dépôt) | Empreinte SHA-256 | Description |\n")
    r_file.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    r_file.write("\n".join(readme_rows) + "\n\n")
    r_file.write("---\n\n")
    r_file.write("## 🤝 Crédits & Remerciements\n")
    r_file.write("\n".join(sorted(list(credits_list))) + "\n\n")
    r_file.write("---\n")
    r_file.write("*Dépôt 100% autonome géré par GitHub Actions.*\n")

print("=== Synchronisation terminée ===")
