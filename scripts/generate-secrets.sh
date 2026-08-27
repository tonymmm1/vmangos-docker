#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
secret_dir=${VMANGOS_SECRETS_DIR:-"$project_root/secrets"}

mkdir -p "$secret_dir"
chmod 700 "$secret_dir"

create_secret() {
    secret_path=$1

    if [ -s "$secret_path" ]; then
        return
    fi

    umask 077
    python3 -c 'import secrets; print(secrets.token_hex(32))' > "$secret_path"
    chmod 600 "$secret_path"
    printf 'Created %s\n' "$secret_path"
}

create_secret "$secret_dir/mariadb_root_password"
create_secret "$secret_dir/vmangos_db_password"
