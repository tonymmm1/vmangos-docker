#!/bin/sh
set -eu

die() {
    printf 'vmangos-build: %s\n' "$*" >&2
    exit 1
}

case ${THREADS:-} in
    ''|0|*[!0-9]*) die "THREADS must be a positive integer" ;;
esac

case ${CLIENT:-} in
    4222|4297|4375|4449|4544|4695|4878|5086|5302|5464|5875) ;;
    *) die "unsupported CLIENT build: ${CLIENT:-unset}" ;;
esac

cmake \
    -S "$VMANGOS_SRC" \
    -B "$VMANGOS_SRC/build" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_COMPILER_LAUNCHER=ccache \
    -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
    -DCMAKE_INSTALL_PREFIX="$VMANGOS_BIN" \
    -DSUPPORTED_CLIENT_BUILD="$CLIENT" \
    -DBUILD_EXTRACTORS="$EXTRACTORS" \
    -DUSE_SCRIPTS="$SCRIPTS" \
    -DENABLE_MAILSENDER="$MAILSENDER" \
    -DBUILD_FOR_HOST_CPU=OFF \
    -DDEBUG_SYMBOLS=OFF

if [ "$VMANGOS_REVISION" != unknown ]; then
    sed -i \
        -e "s|#define REVISION_HASH.*|#define REVISION_HASH \"$VMANGOS_REVISION\"|" \
        -e "s|#define REVISION_DATE.*|#define REVISION_DATE \"$VMANGOS_REVISION_DATE\"|" \
        "$VMANGOS_SRC/src/shared/revision.h"
fi

cmake --build "$VMANGOS_SRC/build" --parallel "$THREADS"
cmake --install "$VMANGOS_SRC/build"

install -d /vmangos "$VMANGOS_BIN/data" "$VMANGOS_BIN/logs"
cp -a "$VMANGOS_BIN/." /vmangos/

archive="/database/$WORLD_DB.7z"
[ -f "$archive" ] || die "world database archive not found: $archive"
7z e -y "$archive" -o/database
