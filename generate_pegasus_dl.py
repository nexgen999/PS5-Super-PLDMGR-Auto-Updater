import json
import time
from playwright.sync_api import sync_playwright

SITE_URL = "https://pippo26442999.github.io/.exFAT/"
# Si le site demande un mot de passe d'accès au catalogue, mets-le ici (ex: "1234")
PASSWORD = "pippo" 

def scrape_and_generate():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"Chargement de {SITE_URL}...")
        page.goto(SITE_URL, wait_until="networkidle")

        # Si le site possède un champ mot de passe au lancement
        password_input = page.query_selector("input[type='password']")
        if password_input and PASSWORD:
            print("Saisie du mot de passe...")
            password_input.fill(PASSWORD)
            page.keyboard.press("Enter")
            page.wait_for_timeout(3000)

        # Attente du chargement complet de la grille/catalogue déchiffré
        print("Attente du déchiffrement des données par le navigateur...")
        page.wait_for_selector(".grid, .game-card, table, #catalog", timeout=30000)

        # Attendre un délai supplémentaire pour s'assurer que le catalogue complet est chargé
        time.sleep(5)

        # Exécution du script d'extraction dans le contexte du navigateur
        print("Extraction du catalogue Pegasus...")
        pegasus_data = page.evaluate("""
            () => {
                // Si la fonction interne du site existe, on l'appelle directement
                if (typeof window.generatePegasusJson === 'function') {
                    return window.generatePegasusJson();
                }

                // Sinon, extraction manuelle des éléments déchiffrés
                let packages = [];
                let items = window.games || window.catalogData || [];
                
                if (Array.isArray(items) && items.length > 0) {
                    items.forEach(game => {
                        let links = [];
                        let rawLinks = game.downloadLinks || game.links || game.urls || [];
                        
                        if (Array.isArray(rawLinks)) {
                            rawLinks.forEach((l, idx) => {
                                links.append({
                                    name: l.name || l.host || `Mirror ${idx+1}`,
                                    url: l.url || l
                                });
                            });
                        }
                        
                        if (links.length > 0) {
                            packages.push({
                                titleId: String(game.titleId || game.id || "UNKNOWN"),
                                title: String(game.title || game.name || "Untitled"),
                                version: String(game.version || "1.00"),
                                downloadLinks: links
                            });
                        }
                    });
                }

                return {
                    name: "exFAT Pegasus Catalog",
                    packages: packages
                };
            }
        """)

        browser.close()

        if pegasus_data and len(pegasus_data.get("packages", [])) > 0:
            with open("exfat-pegasus.json", "w", encoding="utf-8") as f:
                json.dump(pegasus_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Succès : {len(pegasus_data['packages'])} jeux enregistrés dans exfat-pegasus.json")
        else:
            print("❌ Échec : Aucune donnée récupérée.")

if __name__ == "__main__":
    scrape_and_generate()
