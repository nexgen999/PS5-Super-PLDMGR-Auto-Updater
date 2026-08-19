// pkg.js - Logique de chargement et d'installation des Packages PKG

function handlePkgSourceChange() {
  const select = document.getElementById('pkg-source-select');
  const customGroup = document.getElementById('pkg-custom-url-group');
  
  if (select.value === 'CUSTOM') {
    customGroup.style.display = 'flex';
  } else {
    customGroup.style.display = 'none';
    loadPkgSource(select.value);
  }
}

async function loadPkgSource(url) {
  const targetUrl = formatRawUrl(url);
  if (!targetUrl) return log("URL de source PKG invalide.", "error");

  try {
    log(`Chargement de la liste PKG : ${targetUrl}...`, "info");
    const res = await fetch(targetUrl);
    if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
    const data = await res.json();
    
    const select = document.getElementById('pkg-select');
    select.innerHTML = '';

    let items = Array.isArray(data) ? data : (data.packages || Object.keys(data).map(key => ({ key, ...data[key] })));

    items.forEach(item => {
      const opt = document.createElement('option');
      opt.value = item.url || item.download_url || item.file || item.path;
      const name = item.display_name || item.name || item.title || item.filename || item.key || item.url;
      opt.textContent = name;
      if (opt.value) select.appendChild(opt);
    });

    log(`Liste PKG chargée (${select.options.length} package(s)).`, "success");
  } catch (e) {
    log(`Échec du chargement du JSON PKG`, "error", `Détail : ${e.message}`);
  }
}

async function sendPkg() {
  const ip = document.getElementById('ps5-ip').value.trim();
  const port = document.getElementById('pkg-port').value.trim();
  const pkgUrl = document.getElementById('pkg-select').value;

  if (!ip) return log("L'adresse IP n'est pas renseignée.", "error");
  if (!pkgUrl) return log("Aucun PKG sélectionné.", "error");

  const endpoint = `http://${ip}:${port}/api/install`;
  log(`Envoi de l'ordre d'installation PKG à http://${ip}:${port}...`, "info");

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: "direct", url: pkgUrl })
    });

    if (response.ok) {
      log("Commande PKG transmise avec succès !", "success");
    } else {
      log(`Réponse PS5 : HTTP ${response.status}`, "warning");
    }
  } catch (err) {
    log(`Échec d'envoi du PKG`, "error", `Détails : ${err.message}`);
  }
}
