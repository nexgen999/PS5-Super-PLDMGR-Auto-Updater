#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 01 : Traitement et Validation des Règles de Payloads
===============================================================================
Rôle :
1. Analyse la liste des dépôts GitHub fournis dans le dossier `feed/` (fichiers OPML).
2. Charge le fichier `botbuild/rules_payloads.json`.
3. Génère une carte de règles normalisée associant chaque dépôt GitHub aux filtres
   d'extension, mots-clés d'exclusion, règles d'extraction d'archives ZIP/RAR et renommage.
===============================================================================
"""

import os
import xml.etree.ElementTree as ET
from utils import get_base_dir, load_settings, load_json_file, logging

def parse_opml_feeds(feed_dir: str) -> list:
    """
    Analyse tous les fichiers .opml présents dans le dossier `feed/`
    et extrait les URLs des dépôts GitHub.
    """
    repos = []
    if not os.path.exists(feed_dir):
        logging.warning(f"Le dossier des flux est introuvable : {feed_dir}")
        return repos

    for file in os.listdir(feed_dir):
        if file.endswith(".opml") or file.endswith(".xml"):
            filepath = os.path.join(feed_dir, file)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                for outline in root.findall(".//outline"):
                    xml_url = outline.get("xmlUrl", "")
                    html_url = outline.get("htmlUrl", "")
                    target = xml_url or html_url
                    if "github.com" in target:
                        repos.append({
                            "title": outline.get("text") or outline.get("title") or "Unknown",
                            "url": target.strip()
                        })
            except Exception as e:
                logging.error(f"Erreur de lecture du fichier OPML {file} : {e}")
    return repos

def build_payload_rules_map() -> dict:
    """
    Associe chaque dépôt aux règles déclarées dans `rules_payloads.json`.
    Si un dépôt n'a pas de règle spécifique, applique les règles par défaut issues de `settings.json`.
    """
    base_dir = get_base_dir()
    settings = load_settings()
    global_rules = settings.get("global_rules_and_filtering", {})

    rules_file = os.path.join(base_dir, "botbuild", "rules_payloads.json")
    custom_rules_data = load_json_file(rules_file).get("rules", [])
    
    # Dictionnaire indexé par l'URL du dépôt
    custom_rules_map = {r["repo"].lower().rstrip("/"): r for r in custom_rules_data if "repo" in r}

    feed_repos = parse_opml_feeds(os.path.join(base_dir, "feed"))
    logging.info(f"[Module 01] {len(feed_repos)} dépôts identifiés dans feed/")

    validated_rules = {}
    for repo_info in feed_repos:
        repo_url = repo_info["url"].lower().rstrip("/")
        
        # Règle personnalisée si elle existe, sinon configuration par défaut
        rule = custom_rules_map.get(repo_url, {})

        validated_rules[repo_url] = {
            "title": repo_info["title"],
            "extension_ignore": rule.get("extension_ignore", []),
            "keyword_ignore": rule.get("keyword_ignore", global_rules.get("global_keyword_ignore", [])),
            "archive_extract": rule.get("archive_extract", False),
            "archive_target_extension": rule.get("archive_target_extension", [".elf", ".bin"]),
            "force_rename": rule.get("force_rename", False),
            "custom_filename": rule.get("custom_filename", ""),
            "multiple_files": rule.get("multiple_files", False),
            "special_rules": rule.get("special_rules", None)
        }

    return validated_rules

def main():
    logging.info("=== Lancement du Module 01 : Validation des Règles Payloads ===")
    rules_map = build_payload_rules_map()
    logging.info(f"[Module 01] {len(rules_map)} règles de dépôts prêtes pour le téléchargement.")
    logging.info("=== Module 01 Terminé avec succès ===")

if __name__ == "__main__":
    main()