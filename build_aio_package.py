import os
import sys
import zipfile
import datetime

PAYLOADS_ROOT = "payloads"
RELEASE_NOTES_FILE = "release_notes.md"

def build_aio():
    if not os.path.exists(PAYLOADS_ROOT):
        print(f"Erreur: Le dossier {PAYLOADS_ROOT} n'existe pas.")
        sys.exit(1)

    # Horodatage : JJ.MM.AAAA_HH.MM
    now = datetime.datetime.now()
    tag_timestamp = now.strftime("%d.%m.%Y_%H.%M")

    zip_timestamp_name = f"ps5_super_pldmgr_auto_updated_offline.aio_v{tag_timestamp}.zip"
    zip_latest_name = "ps5_super_pldmgr_auto_updated_offline.aio_latest.zip"

    elf_files_found = []

    print(f"=== Création des packages AIO ({tag_timestamp}) ===")

    # Collecte de tous les fichiers .elf
    for root, _, files in os.walk(PAYLOADS_ROOT):
        for file in files:
            if file.lower().endswith('.elf'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PAYLOADS_ROOT)
                elf_files_found.append((full_path, rel_path, file))

    if not elf_files_found:
        print("⚠️ Aucun fichier .elf trouvé dans payloads/.")
        sys.exit(0)

    # Création des deux archives ZIP (horodatée + latest)
    for zip_name in [zip_timestamp_name, zip_latest_name]:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for full_p, rel_p, filename in elf_files_found:
                # Place les fichiers à la racine de l'archive
                zf.write(full_p, arcname=filename)
        print(f"📦 Archive créée : {zip_name}")

    # Génération des release notes
    with open(RELEASE_NOTES_FILE, "w", encoding="utf-8") as rn:
        rn.write(f"## 🚀 Release AIO Auto-Updated ({tag_timestamp})\n\n")
        rn.write("Cette archive contient l'intégralité des payloads ELF compilés et mis à jour automatiquement.\n\n")
        rn.write("### 📦 Payloads inclus dans ce package :\n")
        for _, _, filename in sorted(elf_files_found, key=lambda x: x[2].lower()):
            rn.write(f"- `{filename}`\n")

    # Exporter le tag pour GitHub Actions via l'environnement
    github_env = os.environ.get('GITHUB_ENV')
    if github_env:
        with open(github_env, 'a', encoding='utf-8') as f:
            f.write(f"AIO_TAG={tag_timestamp}\n")
            f.write(f"ZIP_TIMESTAMP_NAME={zip_timestamp_name}\n")

    print("=== Packaging AIO terminé avec succès ===")

if __name__ == "__main__":
    build_aio()
