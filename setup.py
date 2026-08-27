#!/usr/bin/env python3
"""Build, configure, and run the VMaNGOS Docker stack."""

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_TEMPLATE = PROJECT_ROOT / ".env.example"
ENV_FILE = PROJECT_ROOT / ".env"
COMPOSE = ("docker", "compose", "--env-file", str(ENV_FILE))

CLIENT_PATCHES = {
    4222: 0,
    4297: 1,
    4375: 2,
    4449: 3,
    4544: 4,
    4695: 5,
    4878: 6,
    5086: 7,
    5302: 8,
    5464: 9,
    5875: 10,
}

REQUIRED_ENV = (
    "TZ",
    "VMANGOS_PUBLIC_BIND_ADDRESS",
    "VMANGOS_REALMD_PORT",
    "VMANGOS_REALM_ADDRESS",
    "VMANGOS_REALM_PORT",
    "VMANGOS_REALM_NAME",
    "VMANGOS_REALM_ID",
    "VMANGOS_REALM_ICON",
    "VMANGOS_REALM_FLAGS",
    "VMANGOS_REALM_TIMEZONE",
    "VMANGOS_REALM_SECURITY_LEVEL",
    "VMANGOS_REALM_POPULATION",
    "VMANGOS_CLIENT_BUILD",
    "VMANGOS_REALM_FLAG",
    "VMANGOS_ANTICHEAT",
    "VMANGOS_DB_HOST",
    "VMANGOS_DB_PORT",
    "VMANGOS_DB_USER",
    "VMANGOS_DB_BIND_ADDRESS",
    "VMANGOS_DB_PUBLISHED_PORT",
    "VMANGOS_SECRETS_DIR",
)


class SetupError(RuntimeError):
    """An actionable setup failure."""


def positive_integer(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def build_parser():
    parser = argparse.ArgumentParser(description="Build and run VMaNGOS with Docker")
    parser.add_argument(
        "-m",
        "--mode",
        type=int,
        default=0,
        help="Compatibility mode: 0=setup, 4=clean ccache, 5=clean project containers",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Rebuild the current checkout and apply database migrations",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build the server and service images without starting containers",
    )
    parser.add_argument("-t", "--threads", type=positive_integer, default=2, help="Compiler jobs (default: 2)")
    parser.add_argument(
        "-c",
        "--client",
        type=int,
        choices=tuple(CLIENT_PATCHES),
        help="Supported client build (default comes from .env)",
    )
    parser.add_argument(
        "-a",
        "--anticheat",
        type=int,
        choices=(0, 1),
        help="Enable movement anticheat: 0=disabled, 1=enabled (default comes from .env)",
    )
    parser.add_argument(
        "--realm-address",
        help="Public IP address or DNS name advertised to game clients",
    )
    cleanup = parser.add_mutually_exclusive_group()
    cleanup.add_argument("--ccache", action="store_true", help="Remove this project's compiler cache")
    cleanup.add_argument(
        "--docker",
        action="store_true",
        help="Stop this project and remove its locally built images",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show commands as they run")
    return parser


def run(command, *, verbose=False, check=True, capture_output=False, env=None, cwd=PROJECT_ROOT):
    if verbose:
        print("+", shlex.join(str(part) for part in command))
    return subprocess.run(
        [str(part) for part in command],
        cwd=cwd,
        env=env,
        check=check,
        text=True,
        capture_output=capture_output,
    )


def compose(arguments, *, verbose=False, check=True, capture_output=False):
    return run(
        (*COMPOSE, *arguments),
        verbose=verbose,
        check=check,
        capture_output=capture_output,
    )


def check_dependencies(verbose=False):
    for command in ("git", "docker"):
        if shutil.which(command) is None:
            raise SetupError(f"required command not found: {command}")

    checks = (
        (("git", "--version"), "Git"),
        (("docker", "version", "--format", "{{.Server.Version}}"), "Docker daemon"),
        (("docker", "compose", "version"), "Docker Compose v2"),
    )
    for command, label in checks:
        result = run(command, verbose=verbose, check=False, capture_output=True)
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "command failed"
            raise SetupError(f"{label} is unavailable: {detail}")


def decode_env_value(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value


def load_env(path):
    values = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise SetupError(f"{path.name}:{line_number}: expected KEY=value")
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise SetupError(f"{path.name}:{line_number}: invalid variable name {key!r}")
        values[key] = decode_env_value(value)
    return values


def update_env(path, updates):
    lines = path.read_text(encoding="utf-8").splitlines()
    remaining = dict(updates)
    updated = []

    for line in lines:
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=", line)
        if match and match.group(1) in remaining:
            key = match.group(1)
            value = str(remaining.pop(key))
            if "\n" in value or "\r" in value:
                raise SetupError(f"{key} cannot contain a newline")
            updated.append(f"{key}={value}")
        else:
            updated.append(line)

    if remaining:
        updated.append("")
        updated.extend(f"{key}={value}" for key, value in remaining.items())

    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text("\n".join(updated) + "\n", encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def validate_port(values, name):
    try:
        port = int(values[name])
    except ValueError as error:
        raise SetupError(f"{name} must be a number") from error
    if not 1 <= port <= 65535:
        raise SetupError(f"{name} must be between 1 and 65535")


def validate_env(values):
    missing = [name for name in REQUIRED_ENV if not values.get(name)]
    if missing:
        raise SetupError(f".env is missing required values: {', '.join(missing)}")

    for name in ("VMANGOS_REALMD_PORT", "VMANGOS_REALM_PORT", "VMANGOS_DB_PORT", "VMANGOS_DB_PUBLISHED_PORT"):
        validate_port(values, name)

    for name in (
        "VMANGOS_REALM_ID",
        "VMANGOS_REALM_ICON",
        "VMANGOS_REALM_FLAGS",
        "VMANGOS_REALM_TIMEZONE",
        "VMANGOS_REALM_SECURITY_LEVEL",
        "VMANGOS_REALM_POPULATION",
        "VMANGOS_REALM_FLAG",
    ):
        if not values[name].isdigit():
            raise SetupError(f"{name} must be a non-negative integer")

    try:
        client = int(values["VMANGOS_CLIENT_BUILD"])
    except ValueError as error:
        raise SetupError("VMANGOS_CLIENT_BUILD must be a number") from error
    if client not in CLIENT_PATCHES:
        supported = ", ".join(str(build) for build in CLIENT_PATCHES)
        raise SetupError(f"unsupported VMANGOS_CLIENT_BUILD; choose one of: {supported}")

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", values["VMANGOS_DB_USER"]):
        raise SetupError("VMANGOS_DB_USER contains unsupported characters")
    if not re.fullmatch(r"[A-Za-z0-9_. -]+", values["VMANGOS_REALM_NAME"]):
        raise SetupError("VMANGOS_REALM_NAME contains unsupported characters")
    if not re.fullmatch(r"[A-Za-z0-9.:-]+", values["VMANGOS_REALM_ADDRESS"]):
        raise SetupError("VMANGOS_REALM_ADDRESS must be an IP address or DNS name")
    if values["VMANGOS_ANTICHEAT"] not in ("0", "1"):
        raise SetupError("VMANGOS_ANTICHEAT must be 0 or 1")


def prepare_local_config(args):
    if not ENV_FILE.exists():
        shutil.copyfile(ENV_TEMPLATE, ENV_FILE)
        ENV_FILE.chmod(0o600)
        print("Created .env from .env.example")

    defaults = load_env(ENV_TEMPLATE)
    existing = load_env(ENV_FILE)
    new_defaults = {name: value for name, value in defaults.items() if name not in existing}
    if new_defaults:
        update_env(ENV_FILE, new_defaults)
        print(f"Added {len(new_defaults)} new default value(s) to .env")

    updates = {}
    if args.client is not None:
        updates["VMANGOS_CLIENT_BUILD"] = args.client
    if args.realm_address is not None:
        updates["VMANGOS_REALM_ADDRESS"] = args.realm_address
    if args.anticheat is not None:
        updates["VMANGOS_ANTICHEAT"] = args.anticheat
    if updates:
        update_env(ENV_FILE, updates)

    values = load_env(ENV_FILE)
    validate_env(values)
    return values


def generate_secrets(values, verbose=False):
    environment = os.environ.copy()
    environment.update(values)
    run((PROJECT_ROOT / "scripts/generate-secrets.sh",), verbose=verbose, env=environment)


def update_submodules(threads, verbose=False):
    run(
        ("git", "submodule", "update", "--init", "--recursive", "--jobs", str(threads)),
        verbose=verbose,
    )
    if verbose:
        run(("git", "submodule", "status", "--recursive"), verbose=True)


def build_server(values, args):
    print("Building the VMaNGOS server")
    for directory in (PROJECT_ROOT / "vmangos", PROJECT_ROOT / "src/ccache"):
        directory.mkdir(parents=True, exist_ok=True)

    revision = run(
        ("git", "-C", "src/core", "rev-parse", "HEAD"),
        verbose=args.verbose,
        capture_output=True,
    ).stdout.strip()
    revision_date = run(
        ("git", "-C", "src/core", "show", "-s", "--format=%ci", "HEAD"),
        verbose=args.verbose,
        capture_output=True,
    ).stdout.strip()
    run(
        (
            "docker",
            "build",
            "--tag",
            "vmangos_build",
            "--file",
            "docker/build/Dockerfile",
            "--build-arg",
            f"VMANGOS_REVISION={revision}",
            "--build-arg",
            f"VMANGOS_REVISION_DATE={revision_date}",
            ".",
        ),
        verbose=args.verbose,
    )
    run(
        (
            "docker",
            "run",
            "--rm",
            "--volume",
            f"{PROJECT_ROOT / 'vmangos'}:/vmangos",
            "--volume",
            f"{PROJECT_ROOT / 'src/database'}:/database",
            "--volume",
            f"{PROJECT_ROOT / 'src/ccache'}:/ccache",
            "--env",
            "CCACHE_DIR=/ccache",
            "--env",
            f"THREADS={args.threads}",
            "--env",
            f"CLIENT={values['VMANGOS_CLIENT_BUILD']}",
            "vmangos_build",
        ),
        verbose=args.verbose,
    )


def merge_migrations(verbose=False):
    migration_directory = PROJECT_ROOT / "src/core/sql/migrations"
    merge_script = migration_directory / "merge.sh"
    if not merge_script.is_file():
        raise SetupError(f"migration script not found: {merge_script}")
    run(("bash", "merge.sh"), cwd=migration_directory, verbose=verbose)


def wait_for_database(verbose=False, timeout=180):
    deadline = time.monotonic() + timeout
    probe = (
        "sh",
        "-ec",
        'export MYSQL_PWD="$(cat "$VMANGOS_DB_PASSWORD_FILE")"; '
        'exec mariadb --protocol=tcp --host=127.0.0.1 --user="$VMANGOS_DB_USER" '
        "--skip-column-names --execute 'SELECT 1'",
    )

    while time.monotonic() < deadline:
        result = compose(
            ("exec", "-T", "vmangos_database", *probe),
            verbose=verbose,
            check=False,
            capture_output=True,
        )
        if result.returncode == 0:
            return
        time.sleep(2)
    raise SetupError("MariaDB did not become ready within 180 seconds; inspect docker compose logs vmangos_database")


def apply_migrations(verbose=False):
    migrations = (
        ("mangos", "/opt/vmangos/sql/migrations/world_db_updates.sql"),
        ("characters", "/opt/vmangos/sql/migrations/characters_db_updates.sql"),
        ("realmd", "/opt/vmangos/sql/migrations/logon_db_updates.sql"),
        ("logs", "/opt/vmangos/sql/migrations/logs_db_updates.sql"),
    )
    client = (
        "sh",
        "-ec",
        'export MYSQL_PWD="$(cat "$VMANGOS_DB_PASSWORD_FILE")"; '
        'exec mariadb --protocol=tcp --host=127.0.0.1 --user="$VMANGOS_DB_USER" "$1" < "$2"',
        "sh",
    )

    for database, sql_path in migrations:
        print(f"Applying {database} migrations")
        compose(("exec", "-T", "vmangos_database", *client, database, sql_path), verbose=verbose)


def clean_ccache():
    cache = PROJECT_ROOT / "src/ccache"
    if cache.exists():
        shutil.rmtree(cache)
        print(f"Removed {cache}")
    else:
        print("Compiler cache is already clean")


def clean_docker(verbose=False):
    compose(("down", "--remove-orphans", "--rmi", "local"), verbose=verbose)
    result = run(
        ("docker", "image", "rm", "vmangos_build"),
        verbose=verbose,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0 and "No such image" not in result.stderr:
        raise SetupError(f"could not remove vmangos_build: {result.stderr.strip()}")


def build_images(values, args):
    compose(("config", "--quiet"), verbose=args.verbose)
    update_submodules(args.threads, args.verbose)
    build_server(values, args)
    merge_migrations(args.verbose)
    compose(("build",), verbose=args.verbose)


def setup_stack(values, args):
    build_images(values, args)
    compose(("up", "--detach"), verbose=args.verbose)
    compose(("ps",), verbose=args.verbose)
    print("Setup complete")


def update_stack(values, args):
    print("Updating the VMaNGOS stack")
    build_images(values, args)
    compose(("down", "--remove-orphans"), verbose=args.verbose)
    compose(("up", "--detach", "vmangos_database"), verbose=args.verbose)
    wait_for_database(args.verbose)
    apply_migrations(args.verbose)
    compose(("up", "--detach"), verbose=args.verbose)
    compose(("ps",), verbose=args.verbose)
    print("Update complete")


def resolve_action(args, parser):
    if args.mode not in (0, 4, 5):
        parser.error("--mode accepts 0 (setup), 4 (clean ccache), or 5 (clean project containers)")
    if args.update and (args.build_only or args.mode != 0 or args.ccache or args.docker):
        parser.error("--update cannot be combined with --build-only or a cleanup action")
    if args.build_only and (args.mode != 0 or args.ccache or args.docker):
        parser.error("--build-only cannot be combined with a cleanup action")
    if args.ccache or args.mode == 4:
        return "ccache"
    if args.docker or args.mode == 5:
        return "docker"
    if args.update:
        return "update"
    if args.build_only:
        return "build"
    return "setup"


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    action = resolve_action(args, parser)

    try:
        if action == "ccache":
            clean_ccache()
            return 0

        values = prepare_local_config(args)
        check_dependencies(args.verbose)

        if action == "docker":
            clean_docker(args.verbose)
            return 0

        generate_secrets(values, args.verbose)
        if action == "build":
            build_images(values, args)
            print("Build complete")
        elif action == "update":
            update_stack(values, args)
        else:
            setup_stack(values, args)
        return 0
    except SetupError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"error: command failed with exit code {error.returncode}: {shlex.join(error.cmd)}", file=sys.stderr)
        return error.returncode or 1


if __name__ == "__main__":
    sys.exit(main())
