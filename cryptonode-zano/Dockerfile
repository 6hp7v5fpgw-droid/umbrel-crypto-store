# syntax=docker/dockerfile:1
#
# Basiert auf dem offiziellen Zano-Node-Image (zanoproject/zano-full-node),
# ergaenzt nur torsocks, damit der P2P-Verkehr ueber Umbrels Tor-Proxy laeuft.
# Kein Kompilieren aus Quellcode mehr noetig.
#
FROM zanoproject/zano-full-node:2.2.1.502

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
      torsocks ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=zano:zano docker-entrypoint.sh /home/zano/docker-entrypoint.sh
RUN chmod +x /home/zano/docker-entrypoint.sh

USER zano:zano
WORKDIR /home/zano

ENTRYPOINT ["/home/zano/docker-entrypoint.sh"]
