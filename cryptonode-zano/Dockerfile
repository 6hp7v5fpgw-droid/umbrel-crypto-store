# syntax=docker/dockerfile:1
#
# Baut zanod + simplewallet aus dem offiziellen hyle-team/zano Repo.
# ZANO_REF MUSS vor dem ersten Build gegen den aktuellen Release-Tag auf
# https://github.com/hyle-team/zano/releases geprueft/aktualisiert werden.
#
FROM ubuntu:24.04 AS builder

ARG ZANO_REF=v2.2.1.502
ENV DEBIAN_FRONTEND=noninteractive

# Ubuntu 24.04 liefert Boost 1.83 und OpenSSL 3.0.x - beides liegt innerhalb
# der von Zano getesteten/unterstuetzten Versionsspannen (min. Boost 1.75,
# OpenSSL bis 3.4 getestet). Dadurch koennen wir apt statt eines manuellen
# Boost/OpenSSL-Builds nutzen, was den Build deutlich vereinfacht.
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential g++ git cmake ca-certificates pkg-config \
      libboost-all-dev libssl-dev libicu-dev libbz2-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --recursive --depth 1 --branch "${ZANO_REF}" \
      https://github.com/hyle-team/zano.git zano

WORKDIR /src/zano/build
# Nur Server-Binaries (Daemon + CLI-Wallet), keine Qt-GUI - haelt das Image
# klein und headless-tauglich.
RUN cmake .. -DCMAKE_BUILD_TYPE=Release \
    && make -j"$(nproc)" daemon simplewallet

# Binaries robust einsammeln, unabhaengig vom genauen Ausgabe-Unterordner.
RUN mkdir -p /out \
    && find /src/zano/build -maxdepth 4 -type f -name daemon -exec cp {} /out/zanod \; \
    && find /src/zano/build -maxdepth 4 -type f -name simplewallet -exec cp {} /out/zano-simplewallet \; \
    && test -x /out/zanod && test -x /out/zano-simplewallet

# ---------------------------------------------------------------------------

FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      libboost-all-dev libssl-dev libicu-dev libbz2-dev zlib1g-dev \
      torsocks ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -u 1000 -m -s /usr/sbin/nologin zano \
    && mkdir -p /data && chown -R 1000:1000 /data

COPY --from=builder /out/zanod /usr/local/bin/zanod
COPY --from=builder /out/zano-simplewallet /usr/local/bin/zano-simplewallet
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER 1000:1000
VOLUME ["/data"]
EXPOSE 11121 11211
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
