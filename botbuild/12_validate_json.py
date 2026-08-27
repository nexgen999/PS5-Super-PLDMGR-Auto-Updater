#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json
from utils import get_base_dir, logging

def validate_all_json():
    base_dir = get_base_dir()
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json") and "node_modules" not in root:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        json.load(f)
                except Exception as e:
                    logging.error(f"[Module 12] JSON Invalide détecté ({file}) : {e}")
    logging.info("[Module 12] Validation JSON terminée.")

if __name__ == "__main__":
    validate_all_json()