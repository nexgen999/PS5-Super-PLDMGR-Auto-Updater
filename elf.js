// elf.js - Logique de chargement et d'injection des Payloads ELF
let allPayloads = []; 
let currentFilteredPayloads = [];

function handleElfSourceChange() {
  const select = document.getElementById('elf-source-select');
  const customGroup = document.getElementById('elf-custom-url-group');
  
  if (select.value === 'CUSTOM') {
    customGroup.style.display = 'flex';
  } else {
    customGroup.style.display = 'none';
    loadElfSource(select.value);
  }
}

async function loadElfSource(url) {
  const targetUrl = formatRawUrl(url);
  if (!targetUrl) return log("URL de source ELF invalide.", "error");

  try {
    log(`Téléchargement de la liste ELF : ${targetUrl}...`, "info");
    const res = await fetch(targetUrl);
    if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
    const data = await res.json();
    
    allPayloads = parsePayloadsData(data);
    populateElfCategories();
    log(`Liste ELF chargée (${allPayloads.length} payload(s)).`, "success");
  } catch (e) {
    log(`Échec du chargement du JSON ELF`, "error", `Détail : ${e.message}`);
  }
}

function parsePayloadsData(data) {
  let rawItems = [];

  if (Array.isArray(data)) {
    rawItems = data;
  } else if (typeof data === 'object' && data !== null) {
    if (Array.isArray(data.payloads)) {
      rawItems = data.payloads;
    } else {
      Object.keys(data).forEach(catName => {
        const content = data[catName];
        if (Array.isArray(content)) {
          content.forEach(item => rawItems.push({ ...item, category: item.category || catName }));
        }
      });
    }
  }

  return rawItems.map((item, index) => {
    const cat = item.category || item.cat || item.group || item.folder || "Non classé";
    const desc = item.description || item.desc || item.info || "Aucune description disponible pour ce payload.";
    const url = item.url || item.download_url || item.file || item.path || item.direct_url || "";
    const name = item.name || item.display_name || item.title || item.filename || `Payload #${index + 1}`;

    return {
      id: index,
      name: name,
      version: item.version || "",
      category: cat.trim(),
      description: desc.trim(),
      url: url
    };
  });
}

function populateElfCategories() {
  const catSelect = document.getElementById('elf-category');
  catSelect.innerHTML = '';

  const categories = [...new Set(allPayloads.map(p => p.category))].sort((a, b) => a.localeCompare(b));

  const defaultOpt = document.createElement('option');
  defaultOpt.value = "ALL";
  defaultOpt.textContent = "-- Toutes les catégories --";
  catSelect.appendChild(defaultOpt);

  categories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat;
    catSelect.appendChild(opt);
  });

  filterPayloads();
}

function filterPayloads() {
  const selectedCat = document.getElementById('elf-category').value;
  const elfSelect = document.getElementById('elf-select');
  elfSelect.innerHTML = '';

  currentFilteredPayloads = (selectedCat === "ALL" || !selectedCat) 
    ? allPayloads 
    : allPayloads.filter(p => p.category === selectedCat);

  currentFilteredPayloads.sort((a, b) => a.name.localeCompare(b.name));

  if (currentFilteredPayloads.length === 0) {
    elfSelect.innerHTML = '<option value="">Aucun payload disponible</option>';
    updateElfDescription();
    return;
  }

  currentFilteredPayloads.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item.id;
    const verText = item.version ? ` (${item.version})` : '';
    const catText = selectedCat === "ALL" ? ` [${item.category}]` : '';
    opt.textContent = `${item.name}${verText}${catText}`;
    elfSelect.appendChild(opt);
  });

  updateElfDescription();
}

function updateElfDescription() {
  const elfSelect = document.getElementById('elf-select');
  const descBox = document.getElementById('elf-description');

  const selectedId = elfSelect.value;
  const payload = currentFilteredPayloads.find(p => p.id == selectedId);

  if (payload && payload.description) {
    descBox.textContent = payload.description;
    descBox.classList.remove('empty');
  } else {
    descBox.textContent = "Aucune description disponible pour ce payload.";
    descBox.classList.add('empty');
  }
}

async function sendElf() {
  const ip = document.getElementById('ps5-ip').value.trim();
  const port = document.getElementById('elf-port').value.trim();
  const selectedId = document.getElementById('elf-select').value;

  const payload = currentFilteredPayloads.find(p => p.id == selectedId);

  if (!ip) return log("L'adresse IP n'est pas renseignée.", "error");
  if (!payload || !payload.url) return log("Aucun payload sélectionné.", "error");

  log(`[Étape 1/2] Téléchargement du fichier ELF (${payload.name})...`, "info");

  let buffer;
  try {
    const response = await fetch(payload.url);
    if (!response.ok) throw new Error(`Code HTTP ${response.status}`);
    buffer = await response.arrayBuffer();
    log(`Fichier récupéré (${buffer.byteLength} octets).`, "success");
  } catch (err) {
    return log(`Erreur téléchargement ELF`, "error", `Détails : ${err.message}`);
  }

  log(`[Étape 2/2] Envoi au socket TCP (http://${ip}:${port})...`, "warning");

  try {
    await fetch(`http://${ip}:${port}`, {
      method: 'POST',
      mode: 'no-cors',
      body: buffer
    });

    log(`Payload "${payload.name}" transmis !`, "success");
  } catch (err) {
    log(`Échec de l'envoi`, "error", `Détails : ${err.message}`);
  }
}
