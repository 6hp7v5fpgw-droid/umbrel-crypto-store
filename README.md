# Crypto Node Store (Umbrel Community App Store)

Ein eigener Umbrel Community App Store mit einer App: **Zano Node** - ein
Zano-Vollknoten, gebaut auf Basis des offiziellen `zanoproject/zano-full-node`
Docker-Images, dessen ausgehender P2P-Verkehr per `torsocks` über Umbrels
eingebauten Tor-SOCKS-Proxy läuft.

Repo: `https://github.com/6hp7v5fpgw-droid/umbrel-crypto-store`

## Struktur

```
umbrel-app-store.yml            # Store-Manifest (id: cryptonode)
cryptonode-zano/
  umbrel-app.yml                # App-Manifest (Anzeige in der Umbrel-UI)
  docker-compose.yml            # app_proxy + web (Status) + zanod
  Dockerfile                    # FROM zanoproject/zano-full-node + torsocks
  docker-entrypoint.sh          # startet zanod ueber torsocks
  status/                       # kleine Flask-Statusseite (Hoehe, Peers, Tor)
  data/zano/.gitkeep            # persistentes Blockchain-/Log-Verzeichnis
.github/workflows/build-images.yml  # baut & pusht Images nach ghcr.io
```

## Setup (einmalig)

1. **Diese Dateien ins bestehende Repo hochladen** (überschreibt den alten
   Quellcode-Build-Ansatz).
2. In **Settings → Actions → General → Workflow permissions**: *"Read and
   write permissions"* aktivieren (falls noch nicht geschehen), damit die
   Actions nach `ghcr.io` pushen dürfen.
3. **Workflow einmal manuell starten**: Tab *Actions* → *Build & publish app
   images* → *Run workflow*. Baut zwei Images:
   - `ghcr.io/6hp7v5fpgw-droid/umbrel-crypto-store/zano-node` (amd64, nur
     wenige Sekunden Bauzeit, da nur torsocks auf das fertige offizielle
     Image installiert wird)
   - `ghcr.io/6hp7v5fpgw-droid/umbrel-crypto-store/zano-status` (amd64 +
     arm64, wenige Minuten)
4. In GitHub unter *Packages* die beiden Packages auf **Public** stellen
   (sonst kann Umbrel sie nicht pullen).
5. Falls das offizielle Zano-Image aktualisiert wird: in
   `cryptonode-zano/Dockerfile` (FROM-Zeile), `cryptonode-zano/docker-compose.yml`
   (Image-Tag) und `cryptonode-zano/umbrel-app.yml` (`version:`) die neue
   Versionsnummer eintragen.

## App in Umbrel installieren / aktualisieren

Store ist bereits unter **App Store → "..." → Community App Stores**
eingetragen. Nach dem Push einfach die Store-Seite neu laden und "Zano Node"
installieren.

## Design-Entscheidungen

- **Offizielles Basis-Image**: Kein Kompilieren aus Quellcode mehr - das
  Dockerfile nimmt `zanoproject/zano-full-node` (vom Zano-Team gepflegt) und
  installiert nur `torsocks` obendrauf. Nachteil: aktuell nur **amd64**
  verfügbar (kein Raspberry Pi/arm64).
- **Ausgehend über Tor**: `docker-entrypoint.sh` setzt `TORSOCKS_TOR_ADDRESS`
  / `TORSOCKS_TOR_PORT` auf Umbrels bereitgestellte `TOR_PROXY_IP` /
  `TOR_PROXY_PORT` und startet `zanod` unter `torsocks`. `torsocks` hängt sich
  per `LD_PRELOAD` in alle ausgehenden Verbindungen ein - das funktioniert
  unabhängig davon, ob Zano selbst einen `--proxy`-Schalter hätte.
- **Kein eingehender P2P-Verkehr**: `--p2p-bind-ip=127.0.0.1` und
  `--hide-my-port` sorgen dafür, dass der Knoten keine eingehenden
  Peer-Verbindungen akzeptiert. Der Knoten ist für deine eigene Wallet
  gedacht, nicht als öffentlicher Relay.
- **Fernzugriff per .onion**: Die Status-Seite läuft hinter `app_proxy`. Wenn
  du in den Umbrel-Einstellungen *Remote Tor Access* für diese App aktivierst,
  bekommt sie automatisch eine `.onion`-Adresse.
- **RPC bleibt intern**: Der RPC-Port (11211) wird nicht auf den Host
  published, sondern ist nur für den `web`-Statusdienst im Docker-Netz
  erreichbar.

## Bekannte Einschränkungen

- Nur **amd64** (x86) - kein Raspberry Pi/arm64, solange das offizielle
  Zano-Image keine arm64-Variante anbietet.
- Dies ist ein privater Node für die eigene Wallet - kein offizieller,
  geprüfter Umbrel-App-Store-Eintrag.
