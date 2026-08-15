import os
import json
import datetime

JSON_DIR = "json"
PAYLOADS_JSON = os.path.join(JSON_DIR, "payloads.json")
OUTPUT_HTML = "index.html"

# Configuration profil & réseaux
USERNAME = "nexgen999"
AVATAR_URL = f"https://github.com/{USERNAME}.png"
REPO_NAME = os.environ.get('GITHUB_REPOSITORY', 'PS5-Super-PLDMGR-Auto-Updater').split('/')[-1]
LATEST_ZIP_URL = f"https://github.com/{USERNAME}/{REPO_NAME}/releases/latest/download/ps5_super_pldmgr_auto_updated_offline.aio_latest.zip"
JSON_URL = f"https://{USERNAME}.github.io/{REPO_NAME}/json/payloads.json"

def generate_html():
    now_str = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
    
    payloads_data = []
    if os.path.exists(PAYLOADS_JSON):
        try:
            with open(PAYLOADS_JSON, 'r', encoding='utf-8') as f:
                payloads_data = json.load(f).get("payloads", [])
        except Exception as e:
            print(f"Erreur de lecture du JSON : {e}")

    # Génération des lignes de la table de payloads
    payload_rows_html = ""
    for item in payloads_data:
        payload_rows_html += f"""
        <tr>
            <td><strong>{item.get('name', 'Inconnu')}</strong></td>
            <td><span class="badge badge-cat">{item.get('category', 'Général')}</span></td>
            <td><span class="badge badge-ver">{item.get('version', 'v1.0')}</span></td>
            <td><code>{item.get('checksum', '')[:10]}...</code></td>
            <td><a href="{item.get('url', '#')}" class="btn-download-sm" target="_blank">ELF</a></td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PS5 Payload Manager & Store</title>
    <style>
        :root {{
            --bg-main: #15202b;
            --bg-card: #1e2732;
            --bg-hover: #273340;
            --border-color: #38444d;
            --text-main: #f7f9fa;
            --text-muted: #8899a6;
            --accent-blue: #1da1f2;
            --accent-blue-hover: #1a91da;
            --accent-green: #00ba7c;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: var(--bg-main); color: var(--text-main); display: flex; min-height: 100vh; }}

        /* Sidebar */
        .sidebar {{ width: 280px; background-color: var(--bg-main); border-right: 1px solid var(--border-color); padding: 20px; display: flex; flex-direction: column; position: fixed; height: 100vh; overflow-y: auto; }}
        .profile-card {{ text-align: center; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); margin-bottom: 20px; }}
        .profile-img {{ width: 90px; height: 90px; border-radius: 50%; border: 3px solid var(--accent-blue); margin-bottom: 10px; }}
        .profile-name {{ font-size: 1.2rem; font-weight: bold; }}
        .profile-handle {{ color: var(--text-muted); font-size: 0.9rem; margin-bottom: 12px; }}
        
        .social-links {{ display: flex; justify-content: center; gap: 10px; margin-top: 10px; }}
        .social-btn {{ color: var(--text-muted); text-decoration: none; font-size: 0.85rem; padding: 4px 10px; border: 1px solid var(--border-color); border-radius: 15px; transition: 0.2s; }}
        .social-btn:hover {{ background-color: var(--bg-hover); color: var(--accent-blue); border-color: var(--accent-blue); }}

        .nav-menu {{ display: flex; flex-direction: column; gap: 8px; flex-grow: 1; }}
        .nav-item {{ display: flex; align-items: center; gap: 12px; padding: 12px 16px; color: var(--text-main); text-decoration: none; border-radius: 25px; font-weight: 600; cursor: pointer; transition: 0.2s; }}
        .nav-item:hover, .nav-item.active {{ background-color: var(--bg-hover); color: var(--accent-blue); }}

        /* Main Content */
        .main-content {{ margin-left: 280px; flex-grow: 1; padding: 30px; max-width: 1000px; }}
        .tab-panel {{ display: none; }}
        .tab-panel.active {{ display: block; animation: fadeIn 0.3s ease; }}

        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        .card {{ background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 16px; padding: 24px; margin-bottom: 20px; }}
        h1, h2, h3 {{ margin-bottom: 15px; }}
        p {{ color: var(--text-muted); line-height: 1.6; margin-bottom: 15px; }}
        code {{ background-color: #10171e; color: var(--accent-blue); padding: 3px 8px; border-radius: 6px; font-family: monospace; font-size: 0.9rem; }}

        /* Buttons & Badges */
        .btn-primary {{ display: inline-block; background-color: var(--accent-blue); color: #fff; text-decoration: none; padding: 12px 24px; border-radius: 25px; font-weight: bold; transition: 0.2s; border: none; cursor: pointer; }}
        .btn-primary:hover {{ background-color: var(--accent-blue-hover); }}
        .badge {{ padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }}
        .badge-cat {{ background-color: #253341; color: var(--accent-blue); }}
        .badge-ver {{ background-color: #193a32; color: var(--accent-green); }}

        /* Tables */
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--border-color); }}
        th {{ background-color: var(--bg-card); color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; }}
        tr:hover {{ background-color: var(--bg-hover); }}
        .btn-download-sm {{ color: var(--accent-blue); text-decoration: none; font-weight: bold; }}
        .btn-download-sm:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>

    <!-- Sidebar -->
    <div class="sidebar">
        <div class="profile-card">
            <img src="{AVATAR_URL}" alt="Profile" class="profile-img">
            <div class="profile-name">nexgen999</div>
            <div class="profile-handle">@nexgen999</div>
            <p style="font-size: 0.8rem; margin-bottom: 0;">PS5 Scene & Homebrew Automation</p>
            <div class="social-links">
                <a href="https://github.com/{USERNAME}" target="_blank" class="social-btn">GitHub</a>
                <a href="https://x.com" target="_blank" class="social-btn">X</a>
            </div>
        </div>

        <nav class="nav-menu">
            <div class="nav-item active" onclick="switchTab('home')">🏠 Accueil</div>
            <div class="nav-item" onclick="switchTab('json-info')">📄 payloads.json</div>
            <div class="nav-item" onclick="switchTab('aio-package')">📦 Package AIO</div>
            <div class="nav-item" onclick="switchTab('payloads-list')">🛠️ Payloads ELF ({len(payloads_data)})</div>
            <div class="nav-item" onclick="switchTab('credits')">🤝 Crédits</div>
            <div class="nav-item" onclick="switchTab('about')">ℹ️ À Propos</div>
        </nav>
    </div>

    <!-- Main Content -->
    <div class="main-content">

        <!-- Panel: Accueil -->
        <div id="home" class="tab-panel active">
            <div class="card">
                <h1>🎮 PS5 Payload Manager & Store</h1>
                <p>Bienvenue sur le hub automatisé de gestion de payloads pour la scène PS5 jailbreak.</p>
                <p><strong>Dernière synchronisation :</strong> <code>{now_str}</code></p>
                <div style="display: flex; gap: 15px; margin-top: 20px;">
                    <a href="{LATEST_ZIP_URL}" class="btn-primary">📦 Télécharger AIO Latest (.zip)</a>
                    <button class="btn-primary" style="background-color: var(--bg-hover);" onclick="switchTab('json-info')">⚙️ Configurer le JSON</button>
                </div>
            </div>
        </div>

        <!-- Panel: payloads.json -->
        <div id="json-info" class="tab-panel">
            <div class="card">
                <h2>📄 Configuration du fichier JSON central</h2>
                <p>Utilisez cette URL directement dans votre application PS5 pour alimenter votre liste de payloads en temps réel :</p>
                <p><code>{JSON_URL}</code></p>
                <h3>📌 Instructions d'installation :</h3>
                <ol style="margin-left: 20px; color: var(--text-muted); line-height: 1.8;">
                    <li>Ouvrez l'application Payload Manager / Store sur votre PS5.</li>
                    <li>Accédez aux paramètres de source distante.</li>
                    <li>Ajoutez l'URL exacte du fichier <code>payloads.json</code> indiquée ci-dessus.</li>
                    <li>Validez pour charger la liste dynamique des payloads.</li>
                </ol>
            </div>
        </div>

        <!-- Panel: Package AIO -->
        <div id="aio-package" class="tab-panel">
            <div class="card">
                <h2>📦 Package All-In-One (AIO) Hors-ligne</h2>
                <p>Ce package est régénéré automatiquement à chaque mise à jour du dépôt. Il regroupe la totalité des fichiers ELF dans une seule archive ZIP.</p>
                <p><strong>URL Fixe Permanent (Latest) :</strong></p>
                <p><code>{LATEST_ZIP_URL}</code></p>
                <br>
                <a href="{LATEST_ZIP_URL}" class="btn-primary">Télécharger le Dernier Package (.zip)</a>
            </div>
        </div>

        <!-- Panel: Liste Payloads -->
        <div id="payloads-list" class="tab-panel">
            <div class="card">
                <h2>🛠️ Payloads ELF disponibles</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Nom</th>
                            <th>Catégorie</th>
                            <th>Version</th>
                            <th>Checksum</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {payload_rows_html if payload_rows_html else '<tr><td colspan="5">Aucun payload répertorié.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Panel: Crédits -->
        <div id="credits" class="tab-panel">
            <div class="card">
                <h2>🤝 Remerciements & Crédits</h2>
                <p>Un grand merci à l'ensemble des développeurs et chercheurs de la scène PS5 homebrew dont les travaux alimentent ce magasin automatisé.</p>
            </div>
        </div>

        <!-- Panel: À Propos -->
        <div id="about" class="tab-panel">
            <div class="card">
                <h2>ℹ️ À Propos</h2>
                <p>Projet développé et maintenu par <strong>nexgen999</strong>.</p>
                <p>Ce système utilise GitHub Actions pour surveiller les dépôts sources, extraire et renommer les binaires ELF, puis distribuer les mises à jour en continu via GitHub Pages et Releases.</p>
            </div>
        </div>

    </div>

    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }}
    </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as out:
        out.write(html_content)

    print(f"🌐 Page web générée avec succès : {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_html()
