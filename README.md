# vmangos-docker

[![CI](https://github.com/tonymmm1/vmangos-docker/actions/workflows/vmangos-docker.yml/badge.svg)](https://github.com/tonymmm1/vmangos-docker/actions/workflows/vmangos-docker.yml)

**Release:** 0.5.3

A reproducible Docker Compose deployment for the
[VMaNGOS](https://github.com/vmangos/core) login server, world server, and
MariaDB database. It supports local, LAN, and internet-facing realms without
hard-coded host addresses or database credentials.

[Quick start](#quick-start) · [Remote deployment](#lan-and-internet-deployment) ·
[Configuration](#configuration-reference) · [Operations](#operations) ·
[Backup](#backup-and-restore) · [Troubleshooting](#troubleshooting)

## What it provides

- Pinned VMaNGOS and world-database source revisions
- Support for Vanilla client builds 4222 through 5875
- A tracked `.env.example` and an ignored local `.env`
- Random MariaDB root and application passwords stored as file secrets
- An internal-only database network by default
- Minimal, non-root login and world-server containers
- Health checks, persistent database storage, and persistent logs
- CI checks for tests, Compose validation, and a full image build

## Stack at a glance

| Service | Purpose | Published by default | Persistent data |
| --- | --- | --- | --- |
| `vmangos_realmd` | Client authentication and realm selection | TCP `3724` | Shared log volume |
| `vmangos_mangos` | World server and console | TCP `8085` | Shared log volume; client data is mounted read-only |
| `vmangos_database` | MariaDB for realm, character, world, and log data | Nothing | Database volume |

The login and world servers can reach MariaDB over the internal `backend`
network. MariaDB is not reachable from the host unless the optional
administration overlay is enabled.

## Requirements

- A 64-bit x86 Docker host capable of running Linux containers; native arm64
  builds are not currently supported
- Git
- Docker Engine with the Docker Compose v2 plugin (`docker compose`)
- Python 3
- A legally obtained, supported WoW client from which to extract server data
- Enough memory for compilation; use `--threads 2` on a host with 4 GB or less

This repository does not contain client-derived DBC, map, vmap, or mmap files.

## Quick start

### 1. Clone the pinned source

```sh
git clone --recurse-submodules https://github.com/tonymmm1/vmangos-docker.git
cd vmangos-docker
```

If the repository was cloned without submodules, initialize them with:

```sh
git submodule update --init --recursive
```

### 2. Create the local configuration

```sh
cp .env.example .env
chmod 600 .env
```

For a server that should accept connections only from the Docker host, set both
addresses to loopback:

```dotenv
VMANGOS_PUBLIC_BIND_ADDRESS=127.0.0.1
VMANGOS_REALM_ADDRESS=127.0.0.1
```

For a LAN or public server, keep the public bind on the intended host interface
and set the address that clients can reach:

```dotenv
VMANGOS_REALM_ADDRESS=play.example.com
```

The setup script also creates `.env` automatically when it is missing, but
copying it first makes the configuration explicit before the build starts.

### 3. Provide client data

Place data extracted from the selected client build under `src/data`. For the
default 1.12.1 build, the final layout is:

```text
src/data/
├── 5875/
│   └── dbc/
├── maps/
├── mmaps/
└── vmaps/
```

To build the upstream Linux extraction tools without starting services, run:

```sh
./setup.py --build-only --threads 2
```

The tools are staged in `vmangos/bin/Extractors`. Run the appropriate tools
against the matching client, then copy their output into the layout above. The
[VMaNGOS extraction guide](https://github.com/vmangos/wiki/blob/master/docs/Getting-it-working-Windows.md#1-extracting-data-from-the-client)
documents the required DBC, map, vmap, and mmap outputs.

### 4. Build and start

If client data was already prepared, build and start everything with:

```sh
./setup.py --threads 2
```

If `--build-only` was used in the previous step, start the already-built stack
with:

```sh
docker compose up --detach
```

Check the result:

```sh
docker compose ps
docker compose logs --tail 100 vmangos_database vmangos_realmd vmangos_mangos
```

All three services should become healthy. The world server cannot become ready
until the client data directories contain compatible data.

### 5. Point the client at the server

Set the client's realmlist to the same address used by
`VMANGOS_REALM_ADDRESS`, for example:

```text
set realmlist play.example.com
```

Create the first account from the world-server console:

```sh
docker compose attach vmangos_mangos
```

Then enter the following console commands, substituting a unique account name
and password:

```text
account create ACCOUNT_NAME STRONG_UNIQUE_PASSWORD
account set gmlevel ACCOUNT_NAME 6
```

Detach without stopping the container by pressing `Ctrl-p`, then `Ctrl-q`.

## LAN and internet deployment

These two settings serve different purposes:

| Setting | Meaning |
| --- | --- |
| `VMANGOS_PUBLIC_BIND_ADDRESS` | Host interface on which Docker listens; it is never advertised to clients |
| `VMANGOS_REALM_ADDRESS` | IP address or DNS name sent to clients by the realm server |

A typical public deployment uses:

```dotenv
VMANGOS_PUBLIC_BIND_ADDRESS=0.0.0.0
VMANGOS_REALM_ADDRESS=play.example.com
VMANGOS_REALMD_PORT=3724
VMANGOS_REALM_PORT=8085
```

Also:

1. Allow TCP `3724` and `8085` through the Docker host's firewall.
2. If the host is behind NAT, forward both TCP ports to it.
3. Point the DNS record at the public address.
4. Keep the externally visible world port equal to `VMANGOS_REALM_PORT`, because
   that is the port advertised to clients.

MariaDB remains private in this configuration. Publishing the two game ports
does not publish the database.

## Configuration reference

`.env.example` is the tracked source of defaults. `.env` is the ignored local
copy read by `setup.py` and Docker Compose.

### Public endpoints and runtime

| Variable | Default | Purpose |
| --- | --- | --- |
| `TZ` | `Etc/UTC` | Container timezone |
| `VMANGOS_PUBLIC_BIND_ADDRESS` | `0.0.0.0` | Host address for the two game ports |
| `VMANGOS_REALMD_PORT` | `3724` | Host login-server port |
| `VMANGOS_REALM_ADDRESS` | `127.0.0.1` | Address advertised to clients |
| `VMANGOS_REALM_PORT` | `8085` | Host and advertised world-server port |
| `VMANGOS_REALM_NAME` | `VMaNGOS` | Realm display name |
| `VMANGOS_CLIENT_BUILD` | `5875` | Supported client build and data directory |
| `VMANGOS_ANTICHEAT` | `1` | Movement anticheat: `1` enabled, `0` disabled |

### Realm metadata

| Variable | Default | Database field or purpose |
| --- | --- | --- |
| `VMANGOS_REALM_ID` | `1` | Realm ID used by the database and world server |
| `VMANGOS_REALM_ICON` | `1` | `realmlist.icon` |
| `VMANGOS_REALM_FLAGS` | `0` | `realmlist.realmflags` |
| `VMANGOS_REALM_TIMEZONE` | `1` | `realmlist.timezone` |
| `VMANGOS_REALM_SECURITY_LEVEL` | `0` | Minimum account security level |
| `VMANGOS_REALM_POPULATION` | `0` | Initial displayed population value |
| `VMANGOS_REALM_FLAG` | `2` | `realmlist.flag` |

Realm metadata is written when a new database volume is initialized. Changing
those values later does not rewrite an existing `realmd.realmlist` row. Back up
the database before changing an established realm.

### Database and administration

| Variable | Default | Purpose |
| --- | --- | --- |
| `VMANGOS_DB_HOST` | `vmangos_database` | Database host used by VMaNGOS services |
| `VMANGOS_DB_PORT` | `3306` | Internal database port |
| `VMANGOS_DB_USER` | `mangos` | Restricted application account |
| `VMANGOS_DB_BIND_ADDRESS` | `127.0.0.1` | Host bind used only by the administration overlay |
| `VMANGOS_DB_PUBLISHED_PORT` | `3306` | Host port used only by the administration overlay |
| `VMANGOS_SECRETS_DIR` | `./secrets` | Host directory containing generated password files |

Command-line values update `.env`, so the following is equivalent to editing
the corresponding settings:

```sh
./setup.py --realm-address play.example.com --client 5875 --anticheat 1
```

## Credentials and secrets

Ordinary deployment settings belong in `.env`; passwords do not. On first use,
`scripts/generate-secrets.sh` creates:

```text
secrets/
├── mariadb_root_password
└── vmangos_db_password
```

The directory and files are private, ignored by Git, and mounted into containers
as Compose file secrets. They are host files, not an encrypted secret vault, so
protect them and include a secure copy with your database backups.

Do not delete or regenerate these files while reusing an existing database
volume. MariaDB retains the passwords stored in that volume, and newly generated
files will no longer match them.

## Database administration

The base stack does not publish MariaDB. To make it available on the Docker host
only, enable the optional overlay:

```sh
docker compose \
  --file docker-compose.yml \
  --file docker-compose.admin.yml \
  up --detach vmangos_database
```

With the default bind address, connect to `127.0.0.1:3306` using the username in
`.env` and the password in `secrets/vmangos_db_password`.

For administration from another machine, keep MariaDB bound to loopback and use
an SSH tunnel:

```sh
ssh -L 3307:127.0.0.1:3306 user@docker-host
```

Then connect the local database client to `127.0.0.1:3307`. Avoid binding
MariaDB to `0.0.0.0`; if direct publication is unavoidable, restrict it with a
firewall and require encrypted database connections.

## Operations

| Task | Command |
| --- | --- |
| Show service health | `docker compose ps` |
| Follow all logs | `docker compose logs --follow` |
| Follow world-server logs | `docker compose logs --follow vmangos_mangos` |
| Attach to the world console | `docker compose attach vmangos_mangos` |
| Stop without deleting data | `docker compose down` |
| Start existing services | `docker compose up --detach` |
| Restart one service | `docker compose restart vmangos_mangos` |
| Build without starting | `./setup.py --build-only` |
| Rebuild and apply migrations | `./setup.py --update` |
| Clean compiler cache | `./setup.py --ccache` |
| Remove project containers and local images | `./setup.py --docker` |

For a normal source update:

```sh
git pull --ff-only
./setup.py --update
```

`./setup.py --docker` preserves the named database and log volumes.
`docker compose down --volumes` does not; it permanently deletes persistent
project data.

## Backup and restore

Create a logical backup of all four game databases without putting a password
on the host command line:

```sh
docker compose exec -T vmangos_database sh -ec \
  'export MYSQL_PWD="$(cat "$MARIADB_ROOT_PASSWORD_FILE")"; \
   exec mariadb-dump --protocol=socket --user=root \
   --single-transaction --quick --routines --events \
   --databases realmd characters mangos logs' > vmangos-backup.sql
```

Verify that a file was written and store a protected copy away from the Docker
host:

```sh
test -s vmangos-backup.sql
```

To restore it, stop the game services, import the file, and start them again:

```sh
docker compose stop vmangos_realmd vmangos_mangos
docker compose exec -T vmangos_database sh -ec \
  'export MYSQL_PWD="$(cat "$MARIADB_ROOT_PASSWORD_FILE")"; \
   exec mariadb --protocol=socket --user=root' < vmangos-backup.sql
docker compose start vmangos_realmd vmangos_mangos
```

The `vmangos_database` and `vmangos_logs` named volumes persist independently of
the containers. A volume snapshot is not a substitute for an application-aware
backup unless MariaDB is stopped or the snapshot method guarantees consistency.

## Upgrading from 0.5.x

Version 0.6 replaces the tracked default passwords with generated file secrets.
An existing 0.5.x database volume still contains the old credentials, so it
cannot be attached directly to a fresh 0.6 configuration.

While the 0.5.x stack is still running, create a logical backup using the
credential already present inside its database container:

```sh
docker exec vmangos_database sh -ec \
  'exec mariadb-dump --user=root --password="$MYSQL_ROOT_PASSWORD" \
   --single-transaction --quick --routines --events \
   --databases realmd characters mangos logs' > vmangos-0.5-backup.sql
test -s vmangos-0.5-backup.sql
```

Store and inspect a second copy before continuing. Only after the backup is
verified, stop the old stack and remove its database volume:

```sh
docker compose down --volumes
```

> **Warning:** `--volumes` permanently deletes the old database volume. Do not
> run it until the logical backup has been verified and copied elsewhere.

Check out version 0.6 or newer, run `./setup.py` to create a database with new
credentials, then restore `vmangos-0.5-backup.sql` using the restore procedure
above.

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

Select a build with `VMANGOS_CLIENT_BUILD` in `.env` or pass `--client` to
`setup.py`. The client data under `src/data` must match the selected build.

## Troubleshooting

### Docker daemon is unavailable

Run `docker version`. The server section must succeed for the current user. If
it does not, start Docker and grant the user access according to the Docker
installation method used by the host.

### The world server is unhealthy or restarts

Check `docker compose logs vmangos_mangos`. The most common cause on a new
installation is missing or mismatched DBC, map, vmap, or mmap data under
`src/data`.

### Clients can log in but cannot enter the realm

Confirm that `VMANGOS_REALM_ADDRESS` is reachable from the client, TCP `8085` is
allowed through the firewall, and the NAT rule forwards the same port advertised
by `VMANGOS_REALM_PORT`.

### A host port is already allocated

Change `VMANGOS_REALMD_PORT`, `VMANGOS_REALM_PORT`, or the administration-only
`VMANGOS_DB_PUBLISHED_PORT` in `.env`, then recreate the affected services.

### Database authentication fails after secrets were removed

Restore the original `secrets/` files that belong to the existing database
volume. Generating replacement files does not rotate credentials already stored
inside MariaDB. If the originals are unavailable, recover from a verified
logical backup into a fresh volume.
