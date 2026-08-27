FROM ubuntu:noble-20260810

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 vmangos \
    && useradd \
        --uid 10001 \
        --gid 10001 \
        --home-dir /opt/vmangos \
        --no-create-home \
        --shell /usr/sbin/nologin \
        vmangos \
    && install -d -o vmangos -g vmangos /opt/vmangos/bin /var/log/vmangos

COPY --chown=vmangos:vmangos vmangos/ /opt/vmangos/
COPY docker/server-entrypoint.sh /usr/local/bin/vmangos-entrypoint

RUN chmod 0755 /usr/local/bin/vmangos-entrypoint \
    && test -x /opt/vmangos/bin/realmd

WORKDIR /opt/vmangos/bin
USER 10001:10001

EXPOSE 3724

ENTRYPOINT ["/usr/local/bin/vmangos-entrypoint"]
CMD ["./realmd", "-c", "/run/vmangos/realmd.conf"]
