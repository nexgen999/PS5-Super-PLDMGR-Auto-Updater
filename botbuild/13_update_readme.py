import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

REPO_NAME = "nexgen999/PS5-Super-PLDMGR-Auto-Updater"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO_NAME}/main"
PAGES_BASE_URL = "https://nexgen999.github.io/PS5-Super-PLDMGR-Auto-Updater"

def generate_readme():
    """Genere un README.md structure avec les URLs du nouveau depot et du Store."""
    readme_path = "README.md"
    
    payloads_count = 0
    if os.path.exists("api/v1/payloads.json"):
        try:
            with open("api/v1/payloads.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                payloads_count = len(data) if isinstance(data, list) else len(data.get("payloads", []))
        except Exception:
            pass

    content = f"""# 🚀 PS5 Super PLDMGR Auto Updater

Automated payload and PKG repository manager for PS5 homebrew execution & host loading. Updated automatically every 6 hours.

---

## 🏬 Store PLDMGR & Links

To use this repository with **PLDMGR / Host Loaders**, configure your endpoint to:

- **Payloads Store JSON:**  
  `{RAW_BASE_URL}/payloads.json`  
  *(OR via API: `{RAW_BASE_URL}/api/v1/payloads.json`)*

- **PKG Store JSON:**  
  `{RAW_BASE_URL}/pkg.json`  
  *(OR via API: `{RAW_BASE_URL}/api/v1/pkg.json`)*

- **Global OPML Feed:**  
  `{RAW_BASE_URL}/rss/store-global.opml`

- **Web Dashboard / GUI:**  
  [{PAGES_BASE_URL}]({PAGES_BASE_URL})

---

## 📦 Direct Downloads & Backups

- 📥 **Payloads All-In-One ZIP:** [`backup/payloads/payloads_aio.zip`]({RAW_BASE_URL}/backup/payloads/payloads_aio.zip)
- 📥 **PKG All-In-One ZIP:** [`backup/pkg/pkg_aio.zip`]({RAW_BASE_URL}/backup/pkg/pkg_aio.zip)
- 🏷️ **Latest Releases:** [GitHub Releases](https://github.com/{REPO_NAME}/releases/tag/latest)

---

## 📊 Status & Overview

- **Total Monitored Payloads:** `{payloads_count}`
- **Automated Update Interval:** Every 6 hours via GitHub Actions
- **Deployed Site:** GitHub Pages (`/dist`)

---
*Maintained automatically by PS5 Super PLDMGR Auto Updater Bot.*
"""

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    
    logging.info(f"README.md mis a jour avec succes pour {REPO_NAME}.")

if __name__ == "__main__":
    logging.info("Execution du module 13_update_readme...")
    generate_readme()
