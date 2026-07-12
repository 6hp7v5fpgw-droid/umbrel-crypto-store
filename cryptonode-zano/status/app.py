import os

import requests
from flask import Flask, jsonify, render_template_string

RPC_HOST = os.environ.get("ZANO_RPC_HOST", "zanod")
RPC_PORT = os.environ.get("ZANO_RPC_PORT", "11211")
RPC_URL = f"http://{RPC_HOST}:{RPC_PORT}/json_rpc"
TOR_ACTIVE = bool(os.environ.get("TOR_PROXY_IP"))

app = Flask(__name__)

PAGE = """
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Zano Node</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background:#0f1115; color:#eee; margin:0; padding:2rem; }
    .card { background:#1b1e26; border-radius:12px; padding:1.5rem 2rem; max-width:640px; margin:0 auto; box-shadow:0 4px 24px rgba(0,0,0,.3); }
    h1 { font-size:1.3rem; margin:0 0 1rem 0; }
    dl { display:grid; grid-template-columns: 1fr 1fr; gap:.5rem 1rem; margin:0; }
    dt { color:#9aa0ac; }
    dd { margin:0; font-weight:600; }
    .ok { color:#4ade80; }
    .bad { color:#f87171; }
    .hint { color:#9aa0ac; font-size:.85rem; margin-top:1.5rem; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Zano Node</h1>
    <dl id="stats"><dt>Status</dt><dd id="status">wird geladen…</dd></dl>
    <p class="hint">Reiner Statusmonitor, keine Wallet. Verbinde deine Zano-Wallet
    intern ueber den RPC-Port dieses Knotens.</p>
  </div>
  <script>
    async function refresh() {
      const dl = document.getElementById('stats');
      try {
        const r = await fetch('/api/status');
        const d = await r.json();
        dl.innerHTML = '';
        const rows = {
          'Status': d.ok ? 'online' : 'nicht erreichbar',
          'Hoehe': d.height ?? '-',
          'Ausgehende Peers': d.outgoing_connections_count ?? '-',
          'Netzwerk': d.testnet ? 'Testnet' : 'Mainnet',
          'Version': d.version ?? '-',
          'Tor (P2P)': d.tor ? 'aktiv, nur ausgehend' : 'inaktiv',
          'RPC (intern)': d.rpc ?? '-',
        };
        for (const [k, v] of Object.entries(rows)) {
          const dt = document.createElement('dt'); dt.textContent = k;
          const dd = document.createElement('dd'); dd.textContent = v;
          if (k === 'Status') dd.className = d.ok ? 'ok' : 'bad';
          dl.appendChild(dt); dl.appendChild(dd);
        }
      } catch (e) {
        dl.innerHTML = '<dt>Status</dt><dd class="bad">Fehler</dd>';
      }
    }
    refresh();
    setInterval(refresh, 10000);
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/api/status")
def status():
    try:
        resp = requests.post(
            RPC_URL,
            json={"jsonrpc": "2.0", "id": "0", "method": "getinfo"},
            timeout=4,
        )
        resp.raise_for_status()
        result = resp.json().get("result", {})
        return jsonify(
            {
                "ok": True,
                "height": result.get("height"),
                "outgoing_connections_count": result.get("outgoing_connections_count"),
                "testnet": result.get("testnet"),
                "version": result.get("version"),
                "tor": TOR_ACTIVE,
                "rpc": f"{RPC_HOST}:{RPC_PORT}",
            }
        )
    except Exception as exc:  # noqa: BLE001 - reported to the UI, not raised
        return jsonify({"ok": False, "error": str(exc), "tor": TOR_ACTIVE}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
