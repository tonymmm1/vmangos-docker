# vmangos-docker

[![CI](https://github.com/tonymmm1/vmangos-docker/actions/workflows/vmangos-docker.yml/badge.svg)](https://github.com/tonymmm1/vmangos-docker/actions/workflows/vmangos-docker.yml)

## Release: 0.5.3

Build and run the [VMaNGOS](https://github.com/vmangos/core) login, world, and
MariaDB services with Docker Compose. The default configuration supports local
play, a public IP address, or a DNS name without editing Compose or the database
by hand.

The base stack publishes only the game ports. MariaDB stays on an internal
Docker network, configuration is read from an ignored `.env` file, and database
passwords are generated into ignored secret files.

## Requirements

- A 64-bit x86 Linux host (the current upstream runtime package is amd64)
- Git
- Docker Engine with the Docker Compose v2 plugin (`docker compose`)
- Python 3
- Enough memory for compilation; use `--threads 2` on a host with 4 GB or less
- Client-derived DBC, map, vmap, and mmap data for the client build you select

## Quick start

Clone the repository and its pinned submodules:

```sh
git clone --recurse-submodules https://github.com/tonymmm1/vmangos-docker.git
cd vmangos-docker
```

Create your local settings file:

```sh
cp .env.example .env
chmod 600 .env
```

Edit `.env`. For a server reached through `play.example.com`, the important
setting is:

```dotenv
VMANGOS_REALM_ADDRESS=play.example.com
```

`VMANGOS_REALM_ADDRESS` is the IP address or DNS name advertised to game
clients. `VMANGOS_PUBLIC_BIND_ADDRESS=0.0.0.0` makes the game ports listen on all
host interfaces; use a specific host address if that is more appropriate.

Place the extracted client data in these directories, replacing `5875` when a
different `VMANGOS_CLIENT_BUILD` is selected:

```text
src/data/
├── 5875/
│   └── dbc/
├── maps/
├── mmaps/
└── vmaps/
```

Build and start the stack:

```sh
./setup.py --threads 2
```

The setup command creates `.env` from `.env.example` when needed, generates the
password files, builds the pinned VMaNGOS revision, initializes MariaDB, and
starts the services. Use `./setup.py --help` to see every option.

## Internet and LAN servers

No Compose edits are needed for a non-local server:

1. Set `VMANGOS_REALM_ADDRESS` to the address clients can reach.
2. Keep `VMANGOS_PUBLIC_BIND_ADDRESS=0.0.0.0`, or set it to the host's intended
   LAN/public interface address.
3. Allow TCP ports `3724` and `8085` through the host firewall.
4. When the host is behind a router or NAT gateway, forward those two TCP ports
   to the Docker host.

The externally published ports can be changed with `VMANGOS_REALMD_PORT` and
`VMANGOS_REALM_PORT`. The realm advertises `VMANGOS_REALM_PORT`, so any NAT rule
must preserve that externally visible port.

## Configuration and credentials

`.env` is for ordinary deployment settings such as addresses, ports, realm
metadata, timezone, client build, and the database username. It is intentionally
ignored by Git. `.env.example` is the safe, tracked template.

Database passwords do not belong in `.env` or `docker-compose.yml`. On the first
setup, `scripts/generate-secrets.sh` creates these files with private
permissions:

```text
secrets/
├── mariadb_root_password
└── vmangos_db_password
```

The files are mounted into the containers as Docker file secrets. Keep them with
the database backup and never commit them. Do not delete or regenerate the
secret files while reusing an existing database volume: MariaDB retains the
credentials stored in that volume.

Command-line settings update `.env`, so this is also valid:

```sh
./setup.py --realm-address play.example.com --client 5875 --anticheat 1
```

## Database administration

MariaDB has no host port in the base stack. For local administration, add the
optional overlay:

```sh
docker compose \
  --file docker-compose.yml \
  --file docker-compose.admin.yml \
  up --detach vmangos_database
```

The default `VMANGOS_DB_BIND_ADDRESS=127.0.0.1` makes this port available only
on the Docker host. An SSH tunnel is preferable for remote administration. If
you deliberately publish MariaDB on another interface, also restrict it with a
firewall and use an encrypted connection.

## Operations

Show service state and logs:

```sh
docker compose ps
docker compose logs --follow vmangos_database
docker compose logs --follow vmangos_realmd vmangos_mangos
```

Attach to the world-server console (detach with `Ctrl-p`, `Ctrl-q`):

```sh
docker compose attach vmangos_mangos
```

Stop and start the stack without deleting data:

```sh
docker compose down
docker compose up --detach
```

Rebuild the current checkout and apply database migrations:

```sh
git pull --ff-only
./setup.py --update
```

Build without starting containers, clean the compiler cache, or remove this
project's containers and locally built images:

```sh
./setup.py --build-only
./setup.py --ccache
./setup.py --docker
```

`--docker` preserves the named database and log volumes. In contrast,
`docker compose down --volumes` deletes persistent database data; use it only
after making and verifying a backup.

## Backup and restore

Create a logical backup of the four game databases:

```sh
docker compose exec -T vmangos_database sh -ec \
  'export MYSQL_PWD="$(cat "$VMANGOS_DB_PASSWORD_FILE")"; \
   exec mariadb-dump --protocol=tcp --host=127.0.0.1 \
   --user="$VMANGOS_DB_USER" --single-transaction \
   --databases realmd characters mangos logs' > vmangos-backup.sql
```

The backup contains account data and should be protected. To restore it, stop
the game services, import the file, and start them again:

```sh
docker compose stop vmangos_realmd vmangos_mangos
docker compose exec -T vmangos_database sh -ec \
  'export MYSQL_PWD="$(cat "$VMANGOS_DB_PASSWORD_FILE")"; \
   exec mariadb --protocol=tcp --host=127.0.0.1 \
   --user="$VMANGOS_DB_USER"' < vmangos-backup.sql
docker compose start vmangos_realmd vmangos_mangos
```

The named `vmangos_database` and `vmangos_logs` volumes persist independently
of the containers.

## Upgrading an existing 0.5.x installation

The credential model changes after 0.5.x, so an old MariaDB volume still knows
the old credentials while the new stack generates new ones. Migrate with a
logical backup rather than deleting the old volume first.

While the old stack is still running, create a backup with its existing root
credential:

```sh
docker exec vmangos_database sh -ec \
  'exec mariadb-dump --user=root --password="$MYSQL_ROOT_PASSWORD" \
   --single-transaction --databases realmd characters mangos logs' \
  > vmangos-0.5-backup.sql
```

Verify that the backup is non-empty and store a second copy. Then switch to the
new release, intentionally remove the old project volume, run `./setup.py`, and
restore the backup using the restore procedure above. Never run
`docker compose down --volumes` until the backup has been verified.

## Supported clients

| Client build | Game version | `WowPatch` |
| ---: | ---: | ---: |
| 4222 | 1.2.4 | 0 |
| 4297 | 1.3.1 | 1 |
| 4375 | 1.4.2 | 2 |
| 4449 | 1.5.1 | 3 |
| 4544 | 1.6.1 | 4 |
| 4695 | 1.7.1 | 5 |
| 4878 | 1.8.4 | 6 |
| 5086 | 1.9.4 | 7 |
| 5302 | 1.10.2 | 8 |
| 5464 | 1.11.2 | 9 |
| 5875 | 1.12.1 | 10 |

Select one in `.env` with `VMANGOS_CLIENT_BUILD`, or pass `--client` to
`setup.py`.
