#!/bin/sh
set -eu

die() {
    printf 'vmangos-entrypoint: %s\n' "$*" >&2
    exit 1
}

read_secret() {
    secret_path=$1
    [ -r "$secret_path" ] || die "cannot read secret file $secret_path"
    secret=$(cat "$secret_path")
    [ -n "$secret" ] || die "secret file $secret_path is empty"
    printf '%s' "$secret"
}

escape_replacement() {
    printf '%s' "$1" | sed 's/[\\&|]/\\&/g'
}

validate_connection_value() {
    value=$1
    name=$2

    printf '%s' "$value" | grep -Eq '^[^;[:cntrl:]]+$' || \
        die "$name contains an unsupported character"
}

template=${VMANGOS_CONFIG_TEMPLATE:?VMANGOS_CONFIG_TEMPLATE is required}
config=${VMANGOS_CONFIG_PATH:?VMANGOS_CONFIG_PATH is required}
db_host=${VMANGOS_DB_HOST:-vmangos_database}
db_port=${VMANGOS_DB_PORT:-3306}
db_user=${VMANGOS_DB_USER:-mangos}
db_password=$(read_secret "${VMANGOS_DB_PASSWORD_FILE:-/run/secrets/vmangos_db_password}")

validate_connection_value "$db_host" VMANGOS_DB_HOST
validate_connection_value "$db_port" VMANGOS_DB_PORT
validate_connection_value "$db_user" VMANGOS_DB_USER
validate_connection_value "$db_password" VMANGOS_DB_PASSWORD

db_host=$(escape_replacement "$db_host")
db_port=$(escape_replacement "$db_port")
db_user=$(escape_replacement "$db_user")
db_password=$(escape_replacement "$db_password")

umask 077
mkdir -p "$(dirname -- "$config")"
sed \
    -e "s|__VMANGOS_DB_HOST__|$db_host|g" \
    -e "s|__VMANGOS_DB_PORT__|$db_port|g" \
    -e "s|__VMANGOS_DB_USER__|$db_user|g" \
    -e "s|__VMANGOS_DB_PASSWORD__|$db_password|g" \
    "$template" > "$config"

exec "$@"
