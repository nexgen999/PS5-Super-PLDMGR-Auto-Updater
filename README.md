# 🎮 PS5 Payload Manager & Mini-Store

![Logo ou Bannière](assets/banner.png)

Bienvenue sur mon écosystème automatisé pour la scène jailbreak PS5 ! Ce dépôt fait office de **back-end et de serveur de distribution** pour mon application PS5.

Toutes les X heures, un robot vérifie les dépôts officiels des développeurs, télécharge les derniers payloads, calcule leur empreinte de sécurité (SHA-256) et génère les index JSON nécessaires au fonctionnement du store sur la console.

---

## 📱 Flux RSS & Alertes (Notifications Mobile / PC)
Vous pouvez suivre l'actualité du store directement depuis votre lecteur RSS favoris :
* **Radar Global (Fichier OPML à importer) :** `rss/store-global.opml`
* **Flux de mises à jour (Notifications en temps réel) :** `rss/feed.xml`

---

## 📦 Liste des Applications & Payloads disponibles

| Application | Auteur | Catégorie | Version (Dépôt) | Empreinte SHA-256 | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **nanoDNS** | Drakmor | Ps5 Dns | [0.3](https://github.com/nexgen999/PS5-Super-PLDMGR-Auto-Updater/tree/main/payloads/ps5_dns/nanoDNS/0.3) | `09b7c87903...` | Un serveur DNS ultra-léger et rapide idéal pour rediriger les requêtes de la console vers votre hôte local d'exploits. |
| **Chukei DNS** | Al-Azif | Ps5 Dns | [0.9.0](https://github.com/nexgen999/PS5-Super-PLDMGR-Auto-Updater/tree/main/payloads/ps5_dns/Chukei_DNS/0.9.0) | `0cf13e1ed8...` | Serveur DNS de redirection d'envergure conçu spécifiquement pour bloquer les mises à jour de Sony et rediriger le guide de l'utilisateur. |
| **etaHEN** | LightningMods | Ps5 HEN Loader | [2.5B](https://github.com/nexgen999/PS5-Super-PLDMGR-Auto-Updater/tree/main/payloads/ps5_hen_loader/etaHEN/2.5B) | `4845cac450...` | Le Homebrew Enabler (HEN) de référence pour la PS5 avec serveurs de triche, plugins et gestionnaire de mémoire intégrés. |
| **PS5 Unified Autoloader** | itsPLK | Ps5 HEN Loader | [v0.1.2-8e96846](https://github.com/nexgen999/PS5-Super-PLDMGR-Auto-Updater/tree/main/payloads/ps5_hen_loader/PS5_Unified_Autoloader/v0.1.2-8e96846) | `14312044a4...` | Chargeur universel de payloads permettant de lancer automatiquement vos outils favoris au démarrage de l'exploit. |
| **PS5 Payload Manager** | itsPLK | Ps5 HEN Loader | [v0.3.1](https://github.com/nexgen999/PS5-Super-PLDMGR-Auto-Updater/tree/main/payloads/ps5_hen_loader/PS5_Payload_Manager/v0.3.1) | `518740adba...` | Interface d'administration et de gestion réseau pour envoyer, activer et ordonner vos fichiers ELF/BIN sur la console. |
| **ELF Arsenal** | SonicIso | Ps5 HEN Loader | [v1.6.21](https://github.com/nexgen999/PS5-Super-PLDMGR-Auto-Updater/tree/main/payloads/ps5_hen_loader/ELF_Arsenal/v1.6.21) | `N/A (Archi...` | Boîte à outils regroupant une collection complète de payloads utilitaires pour les consoles jailbreakées. |
| **Kura** | NookieAI | Ps5 HEN Loader | [v1.0.0-beta.22](https://github.com/nexgen999/PS5-Super-PLDMGR-Auto-Updater/tree/main/payloads/ps5_hen_loader/Kura/v1.0.0-beta.22) | `5e4489709c...` | Un loader de payloads moderne et épuré conçu pour optimiser l'injection de code sur PS5. |

---

## 🤝 Crédits & Remerciements
Ce store ne serait rien sans le travail incroyable des développeurs de la scène PS5. Retrouvez ci-dessous les liens vers leurs projets originaux :

- **Al-Azif** : [Chukei DNS](https://github.com/Al-Azif/chukei-dns)
- **Drakmor** : [nanoDNS](https://github.com/drakmor/nanoDNS)
- **LightningMods** : [etaHEN](https://github.com/etaHEN/etaHEN)
- **NookieAI** : [Kura](https://github.com/NookieAI/kura)
- **SonicIso** : [ELF Arsenal](https://git.etawen.dev/soniciso/elf-arsenal)
- **itsPLK** : [PS5 Payload Manager](https://github.com/itsPLK/ps5-payload-manager)
- **itsPLK** : [PS5 Unified Autoloader](https://github.com/itsPLK/ps5-unified-autoloader)

---
*Dépôt 100% autonome géré par GitHub Actions.*
