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

    now = datetime.datetime.now()
    tag_timestamp = now.strftime("%d.%m.%Y_%H.%M")

    zip_timestamp_name = f"ps5_super_pldmgr_auto_updated_offline.aio_v{tag_timestamp}.zip"
    zip_latest_name = "ps5_super_pldmgr_auto_updated_offline.aio_latest.zip"

    print(f"=== Création des packages AIO avec DERNIÈRES VERSIONS UNIQUEMENT ({tag_timestamp}) ===")

    latest_elf_files = {}

    # Parcourt les sous-dossiers : payloads/categorie/nom_payload/version/fichier.elf
    for root, _, files in os.walk(PAYLOADS_ROOT):
        for file in files:
            if file.lower().endswith('.elf'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PAYLOADS_ROOT)
                parts = rel_path.split(os.sep)

                if len(parts) >= 3:
                    payload_key = f"{parts[0]}/{parts[1]}/{file}"
                    latest_elf_files[payload_key] = (full_path, file)
                else:
                    latest_elf_files[rel_path] = (full_path, file)

    elf_to_pack = list(latest_elf_files.values())

    if not elf_to_pack:
        print("⚠️ Aucun fichier .elf trouvé dans payloads/.")
        sys.exit(0)

    for zip_name in [zip_timestamp_name, zip_latest_name]:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for full_p, filename in elf_to_pack:
                zf.write(full_p, arcname=filename)
        print(f"📦 Archive créée : {zip_name} ({len(elf_to_pack)} ELF uniques)")

    with open(RELEASE_NOTES_FILE, "w", encoding="utf-8") as rn:
        rn.write(f"## 🚀 Release AIO Auto-Updated ({tag_timestamp})\n\n")
        rn.write("Cette archive contient uniquement la **dernière version** de chaque payload ELF disponible.\n\n")
        rn.write("### 📦 Payloads inclus dans ce package :\n")
        for _, filename in sorted(elf_to_pack, key=lambda x: x[1].lower()):
            rn.write(f"- `{filename}`\n")

    github_env = os.environ.get('GITHUB_ENV')
    if github_env:
        with open(github_env, 'a', encoding='utf-8') as f:
            f.write(f"AIO_TAG={tag_timestamp}\n")
            f.write(f"ZIP_TIMESTAMP_NAME={zip_timestamp_name}\n")

    print("=== Packaging AIO terminé ===")

if __name__ == "__main__":
    build_aio()
