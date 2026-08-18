/**
 * PS5 Payload Injector pour WebKit / GitHub Pages
 */

async function injectPayloadToPS5(payloadUrl, targetIp = '127.0.0.1', targetPort = 9021) {
  console.log(`[PS5-Injector] Récupération du payload : ${payloadUrl}`);
  
  // 1. Téléchargement du binaire ELF
  let arrayBuffer;
  try {
    const response = await fetch(payloadUrl);
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
    arrayBuffer = await response.arrayBuffer();
    console.log(`[PS5-Injector] Payload téléchargé (${arrayBuffer.byteLength} octets).`);
  } catch (err) {
    throw new Error(`Impossible de télécharger l'ELF : ${err.message}`);
  }

  // Détection de l'hôte local si exécuté directement sur PS5
  const isPS5Browser = window.location.hostname === '127.0.0.1' || 
                       window.location.hostname === 'localhost' || 
                       navigator.userAgent.includes('PlayStation 5');
  
  const finalIp = isPS5Browser ? '127.0.0.1' : targetIp;
  const rawBytes = new Uint8Array(arrayBuffer);

  // 2. Tentative d'injection via WebSocket (méthode privilégiée par WebKit PS5)
  return new Promise((resolve, reject) => {
    let wsSuccess = false;
    
    try {
      const ws = new WebSocket(`ws://${finalIp}:${targetPort}`);
      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        console.log(`[PS5-Injector] Connecté via WebSocket à ${finalIp}:${targetPort}`);
        ws.send(rawBytes);
        wsSuccess = true;
        setTimeout(() => {
          ws.close();
          resolve({ status: 'success', method: 'WebSocket' });
        }, 300);
      };

      ws.onerror = () => {
        if (!wsSuccess) {
          // Fallback sur fetch raw/no-cors si le serveur n'est pas un WebSocket
          fallbackFetchSend(finalIp, targetPort, rawBytes)
            .then(resolve)
            .catch(reject);
        }
      };
    } catch (e) {
      fallbackFetchSend(finalIp, targetPort, rawBytes)
        .then(resolve)
        .catch(reject);
    }
  });
}

/**
 * Fallback via Fetch binaire direct pour les récepteurs TCP simples
 */
async function fallbackFetchSend(ip, port, dataBytes) {
  console.log(`[PS5-Injector] Tentative via Raw Fetch POST vers ${ip}:${port}...`);
  try {
    await fetch(`http://${ip}:${port}`, {
      method: 'POST',
      mode: 'no-cors',
      headers: {
        'Content-Type': 'application/octet-stream'
      },
      body: dataBytes
    });
    return { status: 'success', method: 'Fetch (no-cors)' };
  } catch (err) {
    throw new Error(`Échec de l'envoi réseau vers la PS5 : ${err.message}`);
  }
}
