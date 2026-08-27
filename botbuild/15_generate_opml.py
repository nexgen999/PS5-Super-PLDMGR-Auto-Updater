#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json
from utils import get_base_dir, load_settings, logging

def generate_opml():
    base_dir = get_base_dir()
    rules_path = os.path.join(base_dir, "config", "rules_payloads.json")
    opml_path = os.path.join(base_dir, "PS5_Repository_Feeds.opml")
    
    feeds = []
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            feeds = data.get("repositories", [])

    opml_content = ['<?xml version="1.0" encoding="UTF-8"?>', '<opml version="2.0">', '  <head><title>PS5 Repository Feeds</title></head>', '  <body>']
    for repo in feeds:
        name = repo.get("repo", "Unknown")
        xml_url = f"https://github.com/{name}/releases.atom"
        opml_content.append(f'    <outline text="{name}" title="{name}" type="rss" xmlUrl="{xml_url}" />')
    opml_content.extend(['  </body>', '</opml>'])

    with open(opml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(opml_content))
    logging.info("[Module 15] Fichier PS5_Repository_Feeds.opml généré.")

if __name__ == "__main__":
    generate_opml()