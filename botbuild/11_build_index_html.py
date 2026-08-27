#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from utils import get_base_dir, load_settings, logging

def build_index_html():
    base_dir = get_base_dir()
    settings = load_settings()
    title = settings.get("web_and_ui", {}).get("site_title", "PS5 Store")
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>body{{font-family:sans-serif;padding:20px;background:#121212;color:#fff;}}a{{color:#4da6ff;}}</style>
</head>
<body>
    <h1>{title}</h1>
    <p>API Statique & Loader PS5 opérationnels.</p>
    <ul>
        <li><a href="api/v1/payloads.json">API Payloads</a></li>
        <li><a href="api/v1/pkg.json">API PKG</a></li>
        <li><a href="whatsnew.md">Changelog</a></li>
    </ul>
</body>
</html>"""
    with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    logging.info("[Module 11] index.html généré.")

if __name__ == "__main__":
    build_index_html()