#!/bin/sh
set -eu

die() {
    printf 'database-init: %s\n' "$*" >&2
    exit 1
}

read_secret() {
    secret_path=$1
    [ -r "$secret_path" ] || die "cannot read secret file $secret_path"
    secret=$(cat "$secret_path")
    [ -n "$secret" ] || die "secret file $secret_path is empty"
    printf '%s' "$secret"
}

validate_text() {
    value=$1
    name=$2
    pattern=$3
    printf '%s' "$value" | grep -Eq "$pattern" || die "$name contains unsupported characters"
}

validate_number() {
    validate_text "$1" "$2" '^[0-9]+$'
}

root_password=$(read_secret "${MARIADB_ROOT_PASSWORD_FILE:-/run/secrets/mariadb_root_password}")
db_password=$(read_secret "${VMANGOS_DB_PASSWORD_FILE:-/run/secrets/vmangos_db_password}")

realm_id=${VMANGOS_REALM_ID:-1}
realm_name=${VMANGOS_REALM_NAME:-VMaNGOS}
realm_address=${VMANGOS_REALM_ADDRESS:-127.0.0.1}
realm_port=${VMANGOS_REALM_PORT:-8085}
realm_icon=${VMANGOS_REALM_ICON:-1}
realm_flags=${VMANGOS_REALM_FLAGS:-0}
realm_timezone=${VMANGOS_REALM_TIMEZONE:-1}
realm_security_level=${VMANGOS_REALM_SECURITY_LEVEL:-0}
realm_population=${VMANGOS_REALM_POPULATION:-0}
client_build=${VMANGOS_CLIENT_BUILD:-5875}
realm_flag=${VMANGOS_REALM_FLAG:-2}
db_user=${VMANGOS_DB_USER:-mangos}

validate_text "$db_password" VMANGOS_DB_PASSWORD '^[A-Za-z0-9._~-]+$'
validate_text "$db_user" VMANGOS_DB_USER '^[A-Za-z0-9_.-]+$'
validate_text "$realm_name" VMANGOS_REALM_NAME '^[A-Za-z0-9_. -]+$'
validate_text "$realm_address" VMANGOS_REALM_ADDRESS '^[A-Za-z0-9.:-]+$'
validate_number "$realm_id" VMANGOS_REALM_ID
validate_number "$realm_port" VMANGOS_REALM_PORT
validate_number "$realm_icon" VMANGOS_REALM_ICON
validate_number "$realm_flags" VMANGOS_REALM_FLAGS
validate_number "$realm_timezone" VMANGOS_REALM_TIMEZONE
validate_number "$realm_security_level" VMANGOS_REALM_SECURITY_LEVEL
validate_number "$realm_population" VMANGOS_REALM_POPULATION
validate_number "$client_build" VMANGOS_CLIENT_BUILD
validate_number "$realm_flag" VMANGOS_REALM_FLAG

mariadb_root() {
    mariadb --protocol=socket --user=root --password="$root_password" "$@"
}

printf 'Configuring application database account\n'
mariadb_root <<SQL
CREATE USER IF NOT EXISTS '$db_user'@'%' IDENTIFIED BY '$db_password';
ALTER USER '$db_user'@'%' IDENTIFIED BY '$db_password';
GRANT ALL PRIVILEGES ON realmd.* TO '$db_user'@'%';
GRANT ALL PRIVILEGES ON characters.* TO '$db_user'@'%';
GRANT ALL PRIVILEGES ON mangos.* TO '$db_user'@'%';
GRANT ALL PRIVILEGES ON logs.* TO '$db_user'@'%';
FLUSH PRIVILEGES;
SQL

printf 'Importing databases\n'
mariadb_root realmd < /opt/vmangos/sql/logon.sql
mariadb_root logs < /opt/vmangos/sql/logs.sql
mariadb_root characters < /opt/vmangos/sql/characters.sql
mariadb_root mangos < "/opt/vmangos/sql/database/$WORLD.sql"

printf 'Importing migrations\n'
mariadb_root mangos < /opt/vmangos/sql/migrations/world_db_updates.sql
mariadb_root characters < /opt/vmangos/sql/migrations/characters_db_updates.sql
mariadb_root realmd < /opt/vmangos/sql/migrations/logon_db_updates.sql
mariadb_root logs < /opt/vmangos/sql/migrations/logs_db_updates.sql

printf 'Upgrading MariaDB system tables\n'
mariadb-upgrade --user=root --password="$root_password"

printf 'Configuring default realm\n'
mariadb_root <<SQL
INSERT INTO realmd.realmlist
    (id, name, address, port, icon, realmflags, timezone, allowedSecurityLevel,
     population, gamebuild_min, gamebuild_max, flag, realmbuilds)
VALUES
    ($realm_id, '$realm_name', '$realm_address', $realm_port, $realm_icon,
     $realm_flags, $realm_timezone, $realm_security_level, $realm_population,
     $client_build, $client_build, $realm_flag, '')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    address = VALUES(address),
    port = VALUES(port),
    icon = VALUES(icon),
    realmflags = VALUES(realmflags),
    timezone = VALUES(timezone),
    allowedSecurityLevel = VALUES(allowedSecurityLevel),
    population = VALUES(population),
    gamebuild_min = VALUES(gamebuild_min),
    gamebuild_max = VALUES(gamebuild_max),
    flag = VALUES(flag);
SQL

printf 'Database creation is complete\n'
