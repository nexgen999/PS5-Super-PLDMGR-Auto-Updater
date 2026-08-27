#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Module Utilitaires Centralisés - PS5 Super PLDMGR Auto-Updater
===============================================================================
Ce fichier contient les fonctions partagées par l'ensemble des modules (01 à 15).
Il permet de charger le fichier de configuration `settings.json`, les fichiers de
règles, et d'assurer un logging homogène.
"""

import os
import json
import logging

# Configuration de base du système de logs
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

def get_base_dir() -> str:
    """Retourne le chemin absolu de la racine du dépôt GitHub."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def load_settings() -> dict:
    """
    Charge le fichier central `botbuild/settings.json`.
    Si le fichier est introuvable, retourne un dictionnaire vide.
    """
    settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
    if not os.path.exists(settings_path):
        logging.error(f"Fichier de configuration introuvable : {settings_path}")
        return {}
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_json_file(filepath: str) -> dict:
    """Charge un fichier JSON quelconque en toute sécurité."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erreur lors de la lecture de {filepath} : {e}")
        return {}

def save_json_file(filepath: str, data: dict) -> bool:
    """Sauvegarde des données au format JSON structuré avec indentation."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde de {filepath} : {e}")
        return False