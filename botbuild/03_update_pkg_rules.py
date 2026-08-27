#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module 03 : Traitement et Validation des Règles PKG
===============================================================================
Rôle :
1. Analyse la liste des dépôts GitHub fournis dans le dossier `PKGfeed/` (.opml / .xml).
2. Charge le fichier `botbuild/rules_pkg.json`.
3. Construit un dictionnaire de règles validées pour chaque dépôt d'applications PKG
   (exclusions d'extensions, filtrage de mots-clés, renommage forcé).
===============================================================================
"""

import os
import xml.etree.ElementTree as ET
from utils import get_base_dir, load_settings, load_json_file, logging

def parse_pkg_opml_feeds(pkg_feed_dir: str) -> list:
    """
    Analyse tous les fichiers .opml / .xml présents dans le dossier `PKGfeed/`
    et extrait les URLs des dépôts GitHub d'applications PKG.
    """
    repos = []
    if not os.path.exists(pkg_feed_dir):
        logging.warning(f"Le dossier des flux PKG est introuvable : {pkg_feed_dir}")
        return repos

    for file in os.listdir(pkg_feed_dir):
        if file.endswith(".opml") or file.endswith(".xml"):
            filepath = os.path.join(pkg_feed_dir, file)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()
                for outline in root.findall(".//outline"):
                    xml_url = outline.get("xmlUrl", "")
                    html_url = outline.get("htmlUrl", "")
                    target = xml_url or html_url
                    if "github.com" in target:
                        repos.append({
                            "title": outline.get("text") or outline.get("title") or "Unknown PKG Repo",
                            "url": target.strip()
                        })
            except Exception as e:
                logging.error(f"Erreur de lecture du fichier OPML PKG {file} : {e}")
    return repos

def build_pkg_rules_map() -> dict:
    """
    Associe chaque dépôt PKG aux règles définies dans `rules_pkg.json`.
    Si un dépôt n'a pas de règle propre, applique les règles globales de `settings.json`.
    """
    base_dir = get_base_dir()
    settings = load_settings()
    global_rules = settings.get("global_rules_and_filtering", {})

    rules_file = os.path.join(base_dir, "botbuild", "rules_pkg.json")
    custom_rules_data = load_json_file(rules_file).get("rules", [])
    
    # Dictionnaire indexé par URL normalisée du dépôt
    custom_rules_map = {r["repo"].lower().rstrip("/"): r for r in custom_rules_data if "repo" in r}

    feed_repos = parse_pkg_opml_feeds(os.path.join(base_dir, "PKGfeed"))
    logging.info(f"[Module 03] {len(feed_repos)} dépôts PKG identifiés dans PKGfeed/")

    validated_rules = {}
    for repo_info in feed_repos:
        repo_url = repo_info["url"].lower().rstrip("/")
        
        # Règle sur-mesure ou repli sur les paramètres globaux
        rule = custom_rules_map.get(repo_url, {})

        validated_rules[repo_url] = {
            "title": repo_info["title"],
            "extension_ignore": rule.get("extension_ignore", [".zip", ".json", ".txt"]),
            "keyword_ignore": rule.get("keyword_ignore", global_rules.get("global_keyword_ignore", [])),
            "force_rename": rule.get("force_rename", False),
            "custom_filename": rule.get("custom_filename", ""),
            "special_rules": rule.get("special_rules", None)
        }

    return validated_rules

def main():
    logging.info("=== Lancement du Module 03 : Validation des Règles PKG ===")
    rules_map = build_pkg_rules_map()
    logging.info(f"[Module 03] {len(rules_map)} règles de dépôts PKG prêtes pour la synchronisation.")
    logging.info("=== Module 03 Terminé avec succès ===")

if __name__ == "__main__":
    main()