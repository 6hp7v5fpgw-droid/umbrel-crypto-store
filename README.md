# Crypto Node Store (Umbrel Community App Store)

Ein eigener Umbrel Community App Store mit einer App: **Zano Node** - ein
Zano-Vollknoten (zanod), dessen ausgehender P2P-Verkehr per `torsocks` über
Umbrels eingebauten Tor-SOCKS-Proxy läuft.

## Struktur

```
umbrel-app-store.yml            # Store-Manifest (id: cryptonode)
cryptonode-zano/
  umbrel-app.yml                # App-Manifest (Anzeige in der Umbrel-UI)
  docker-compose.yml            # app_proxy + web (Status) + zanod
  Dockerfile                    # baut zanod/simplewallet aus dem Zano-Quellcode
  docker-entrypoint.sh          # startet zanod ueber torsocks
  status/                       # kleine Flask-Statusseite (Hoehe, Peers, Tor)
  data/zano/.gitkeep            # persistentes Blockchain-/Log-Verzeichnis
.github/workflows/build-images.yml  # baut & pusht Multi-Arch-Images nach ghcr.io
```

## Setup (einmalig)

1. **Repo auf GitHub erstellen** und diesen Ordnerinhalt hochladen (siehe
   Befehle unten).
2. In **Settings → Actions → General → Workflow permissions**: *"Read and
   write permissions"* aktivieren, damit die Actions nach `ghcr.io` (GitHub
   Container Registry) pushen dürfen.
3. **Zano-Version prüfen**: Auf https://github.com/hyle-team/zano/releases
   den aktuellen Tag nachsehen. Falls er von `v2.1.17.469` abweicht, in
   `.github/workflows/build-images.yml` (Default von `zano_ref`) und in
   `cryptonode-zano/umbrel-app.yml` (`version:`) anpassen.
4. **Workflow einmal manuell starten**: Tab *Actions* → *Build & publish app
   images* → *Run workflow*. Baut zwei Images:
   - `ghcr.io/<owner>/<repo>/zano-node` (amd64 + arm64, ca. 15-30 Min. Bauzeit
     durch das Kompilieren aus dem Quellcode)
   - `ghcr.io/<owner>/<repo>/zano-status` (wenige Minuten)
5. In GitHub unter *Packages* die beiden neuen Packages auf **Public**
   stellen (sonst kann Umbrel sie nicht pullen, da kein Registry-Login
   konfigurierbar ist).
6. In `cryptonode-zano/docker-compose.yml` alle drei Vorkommen von
   `OWNER/REPO` durch deinen tatsächlichen `github-nutzername/repo-name`
   ersetzen, committen und pushen.

```bash
cd umbrel-community-store
git init
git add .
git commit -m "Initial commit: Crypto Node Store mit Zano-Node (Tor)"
git branch -M main
git remote add origin https://github.com/<DEIN-NUTZERNAME>/<REPO-NAME>.git
git push -u origin main
```

## App in Umbrel installieren

In der Umbrel-Oberfläche: **App Store → "..." → Community App Stores → App
Store hinzufügen** und die GitHub-URL deines Repos eintragen
(`https://github.com/<DEIN-NUTZERNAME>/<REPO-NAME>`). Danach erscheint
"Zano Node" im Store.

## Design-Entscheidungen (Tor)

- **Ausgehend über Tor**: `docker-entrypoint.sh` setzt `TORSOCKS_TOR_ADDRESS`
  / `TORSOCKS_TOR_PORT` auf Umbrels bereitgestellte `TOR_PROXY_IP` /
  `TOR_PROXY_PORT` und startet `zanod` unter `torsocks`. `torsocks` hängt sich
  per `LD_PRELOAD` in alle ausgehenden Verbindungen ein - das funktioniert
  unabhängig davon, ob Zano selbst einen `--proxy`-Schalter hätte (im
  Zano-Quellcode wurde keine native SOCKS/Tor-Proxy-CLI-Option für den P2P-Teil
  gefunden, daher dieser bewährte, app-unabhängige Ansatz).
- **Kein eingehender P2P-Verkehr**: `--p2p-bind-ip=127.0.0.1` und
  `--hide-my-port` sorgen dafür, dass der Knoten keine eingehenden
  Peer-Verbindungen akzeptiert. Das ist bewusst konservativ - der Knoten ist
  für deine eigene Wallet gedacht, nicht als öffentlicher Relay. Wer das
  ändern möchte, kann `--p2p-bind-ip=0.0.0.0` setzen und den P2P-Port in
  `docker-compose.yml` per `ports:` veröffentlichen.
- **Fernzugriff per .onion**: Die Status-Seite läuft (wie jede Umbrel-App)
  hinter `app_proxy`. Wenn du in den Umbrel-Einstellungen *Remote Tor Access*
  für diese App aktivierst, bekommt sie automatisch eine `.onion`-Adresse -
  dafür ist keine zusätzliche Konfiguration in diesem Repo nötig.
- **RPC bleibt intern**: Der RPC-Port (11211) wird nicht auf den Host
  published, sondern ist nur für den `web`-Statusdienst im Docker-Netz
  erreichbar. Für Wallet-Zugriff von außen müsstest du bewusst einen weiteren
  Weg (z.B. SSH-Tunnel oder eigener Service) einrichten.

## Bekannte Einschränkungen

- Der Zano-Daemon wird bei jedem Image-Build **komplett aus dem Quellcode
  kompiliert** (kein offizielles Docker-Image verfügbar). Das dauert auf den
  GitHub-Actions-Runnern ca. 15-30 Minuten pro Architektur.
- Passe `ZANO_REF` an, sobald ein neuer Zano-Release erscheint, und starte den
  Workflow erneut, um das Image zu aktualisieren.
- Dies ist ein privater Node für die eigene Wallet - kein offizieller,
  geprüfter Umbrel-App-Store-Eintrag. Für eine Einreichung in den offiziellen
  Store gelten strengere Vorgaben (siehe `AGENTS.md`/`.claude/skills` im
  [offiziellen umbrel-apps Repo](https://github.com/getumbrel/umbrel-apps)).
