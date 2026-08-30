FROM ubuntu:noble-20260810

ARG DEBIAN_FRONTEND=noninteractive
ARG VMANGOS_REVISION=unknown
ARG VMANGOS_REVISION_DATE="1970-01-01 00:00:00 +0000"

ENV VMANGOS_SRC=/opt/core \
    VMANGOS_BIN=/opt/vmangos \
    WORLD_DB=world_full_14_june_2021 \
    THREADS=2 \
    CLIENT=5875 \
    EXTRACTORS=1 \
    SCRIPTS=1 \
    MAILSENDER=1 \
    VMANGOS_REVISION=${VMANGOS_REVISION} \
    VMANGOS_REVISION_DATE=${VMANGOS_REVISION_DATE}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        ccache \
        cmake \
        git \
        libcurl4-openssl-dev \
        libmysqlclient-dev \
        libssl-dev \
        make \
        patchelf \
        p7zip-full \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/core/ /opt/core/
COPY docker/build/build.sh /usr/local/bin/vmangos-build

RUN chmod 0755 /usr/local/bin/vmangos-build

ENTRYPOINT ["/usr/local/bin/vmangos-build"]
