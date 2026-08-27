import json
import os
from datetime import datetime

def generate_whatsnew():
    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
    
    content = f"# 🆕 Quoi de neuf sur PS5 Super PLDMGR Hub ?\n\n"
    content += f"*Dernière mise à jour automatique : {now_str}*\n\n"

    # 1. DERNIÈRES MISES À JOUR (Top 10 récents)
    content += "## 🚀 Dernières Mises à Jour\n\n"
    content += "| Type | Nom | Version / Fichier | Date |\n"
    content += "| :--- | :--- | :--- | :--- |\n"
    
    all_items = []
    if os.path.exists("payloads.json"):
        with open("payloads.json", "r", encoding="utf-8") as f:
            for p in json.load(f).get("payloads", []):
                p["item_type"] = "Payload"
                all_items.append(p)

    if os.path.exists("pkg.json"):
        with open("pkg.json", "r", encoding="utf-8") as f:
            for k in json.load(f).get("pkg", []):
                k["item_type"] = "PKG"
                all_items.append(k)

    # Tri par date
    all_items.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    for item in all_items[:10]:
        content += f"| {item.get('item_type')} | **{item.get('title', 'N/A')}** | `{item.get('file_name', '')}` | {item.get('updated_at', 'N/A')} |\n"

    # 2. CONTENU INTÉGRAL PAYLOADS AIO
    content += "\n---\n\n## 📦 Contenu Intégral du Pack Payloads AIO\n\n"
    content += "| Catégorie | Fichier | Description |\n"
    content += "| :--- | :--- | :--- |\n"
    if os.path.exists("payloads.json"):
        with open("payloads.json", "r", encoding="utf-8") as f:
            for p in json.load(f).get("payloads", []):
                content += f"| {p.get('category', 'Uncategorized')} | `{p.get('file_name')}` | {p.get('description', '')} |\n"

    # 3. CONTENU INTÉGRAL PKG AIO
    content += "\n---\n\n## 🎮 Contenu Intégral du Pack PKG AIO\n\n"
    content += "| Application | Fichier PKG | Version |\n"
    content += "| :--- | :--- | :--- |\n"
    if os.path.exists("pkg.json"):
        with open("pkg.json", "r", encoding="utf-8") as f:
            for k in json.load(f).get("pkg", []):
                content += f"| **{k.get('title')}** | `{k.get('file_name')}` | {k.get('version', 'v1.0')} |\n"

    with open("whatsnew.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    generate_whatsnew()
