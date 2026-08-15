# 🛠️ OPML Feed Manager - PS5 Store Auto-Updater

**OPML Feed Manager** est une interface graphique (GUI) développée en Python avec **CustomTkinter**. Elle permet de créer, modifier et gérer facilement la liste des dépôts GitHub (feeds OPML) utilisés pour mettre à jour automatiquement les payloads et applications de votre store PS5.

---

## 📌 Fonctionnalités

* 📁 **Scan automatique** : Détection instantanée de tous les fichiers `.opml` présents dans le dossier `feed/`.
* ➕ **Création & Édition** : Ajout facile de nouvelles catégories ou modifications de flux existants.
* ✏️ **Édition directe** : Chargement et mise à jour d'un dépôt existant sans suppression nécessaire.
* 🎯 **Format conforme** : Génération XML structurée au format OPML 2.0 avec tous les attributs requis (`text`, `title`, `type="rss"`, `xmlUrl`, `author`, `description`).
* 🧹 **Nettoyage automatique** : Suppression des balises superflues (`htmlUrl`) et mise en forme propre du code XML.

---

## ⚙️ Prérequis & Installation

### 1. Prérequis
Assurez-vous d'avoir installé **Python 3.8** ou une version ultérieure sur votre PC.

### 2. Installation de la dépendance
L'application utilise la bibliothèque **CustomTkinter** pour l'interface graphique. Ouvrez un terminal (Invite de commandes, PowerShell ou WSL) à la racine du projet et exécutez :

```bash
pip install customtkinter

🚀 Lancement de l'application
Vous pouvez lancer l'utilitaire via le terminal avec la commande suivante : python opml_manager.py

Astuce : Si vous utilisez Visual Studio Code ou PyCharm, ouvrez simplement opml_manager.py et appuyez sur la touche F5 pour exécuter le script.

📖 Tutoriel d'utilisation
1. Sélectionner ou créer une catégorie .opml
Ouvrir une catégorie : Dans le panneau de gauche (Catégories OPML), cliquez sur un fichier .opml existant (ex: ps5_kstuff.opml).

Créer une catégorie : Cliquez sur le bouton vert + Nouveau fichier .opml, saisissez le nom du fichier (ex: ps5_utilities.opml) et validez.

2. Ajouter un nouveau dépôt
Remplissez le formulaire de saisie en haut à droite :

Nom / Titre : Le nom du projet (ex: kstuff_EchoStretch).

Auteur : Le créateur du dépôt (ex: EchoStretch).

URL Dépôt / Feed : L'adresse GitHub du projet (ex: https://github.com/EchoStretch/kstuff).

Description : Une brève explication du payload (ex: Fnd Kstuff payload for PS5.).

Cliquez ensuite sur ➕ Ajouter au fichier.

3. Modifier ou supprimer un dépôt
Modifier : Cliquez sur le bouton ✏️ à côté d'un dépôt dans la liste. Les informations se chargent dans le formulaire. Appliquez vos modifications puis cliquez sur 🔄 Mettre à jour.

Supprimer : Cliquez sur le bouton rouge 🗑️ pour retirer un dépôt de la liste.

4. Sauvegarder et publier les changements
Cliquez sur le bouton bleu 💾 Enregistrer au bon format OPML en bas à droite.

Ouvrez votre terminal ou GitHub Desktop.

Effectuez votre commit et poussez les modifications sur le dépôt :

Bash
git add feed/
git commit -m "Mise à jour des catégories OPML"
git push
