#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="/home/zano/.Zano"
RPC_PORT="${ZANO_RPC_PORT:-11211}"
P2P_PORT="${ZANO_P2P_PORT:-11121}"

RUNNER=()

if [ -n "${TOR_PROXY_IP:-}" ] && [ -n "${TOR_PROXY_PORT:-}" ]; then
  export TORSOCKS_TOR_ADDRESS="${TOR_PROXY_IP}"
  export TORSOCKS_TOR_PORT="${TOR_PROXY_PORT}"
  RUNNER=(torsocks)
  echo "[zano] Route ausgehenden P2P-Verkehr ueber Tor: ${TOR_PROXY_IP}:${TOR_PROXY_PORT}"
else
  echo "[zano] WARNUNG: TOR_PROXY_IP/TOR_PROXY_PORT nicht gesetzt - laeuft OHNE Tor (Klarnetz)."
fi

# p2p-bind bewusst auf localhost: dieser Knoten nimmt keine eingehenden
# P2P-Verbindungen an (privater Knoten, kein oeffentlicher Relay).
exec "${RUNNER[@]}" /home/zano/zanod \
  --data-dir="${DATA_DIR}" \
  --rpc-bind-ip=0.0.0.0 \
  --rpc-bind-port="${RPC_PORT}" \
  --p2p-bind-ip=127.0.0.1 \
  --p2p-bind-port="${P2P_PORT}" \
  --hide-my-port \
  --disable-upnp \
  --log-level=1 \
  "$@"
