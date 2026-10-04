import contextlib
import io
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import setup


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ArgumentTests(unittest.TestCase):
    def setUp(self):
        self.parser = setup.build_parser()

    def parse_error(self, arguments):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                self.parser.parse_args(arguments)
        self.assertEqual(raised.exception.code, 2)

    def test_zero_anticheat_is_valid(self):
        args = self.parser.parse_args(["-a", "0", "-c", "4222", "-t", "3"])

        self.assertEqual(args.anticheat, 0)
        self.assertEqual(args.client, 4222)
        self.assertEqual(args.threads, 3)

    def test_zero_threads_is_rejected(self):
        self.parse_error(["-t", "0"])

    def test_unsupported_client_is_rejected(self):
        self.parse_error(["-c", "9999"])

    def test_compatibility_cleanup_modes_work(self):
        self.assertEqual(setup.resolve_action(self.parser.parse_args(["-m", "4"]), self.parser), "ccache")
        self.assertEqual(setup.resolve_action(self.parser.parse_args(["-m", "5"]), self.parser), "docker")

    def test_reset_mode_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                setup.resolve_action(self.parser.parse_args(["-m", "3"]), self.parser)

    def test_build_only_is_exclusive_with_update(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                setup.resolve_action(self.parser.parse_args(["--build-only", "--update"]), self.parser)


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.template = self.root / ".env.example"
        self.environment = self.root / ".env"
        self.template.write_text((PROJECT_ROOT / ".env.example").read_text(encoding="utf-8"), encoding="utf-8")

    def arguments(self, **overrides):
        values = {"client": None, "realm_address": None, "anticheat": None}
        values.update(overrides)
        return SimpleNamespace(**values)

    def prepare(self, arguments):
        with mock.patch.object(setup, "ENV_TEMPLATE", self.template), mock.patch.object(
            setup, "ENV_FILE", self.environment
        ):
            return setup.prepare_local_config(arguments)

    def test_missing_env_is_created_with_private_permissions(self):
        values = self.prepare(self.arguments())

        self.assertEqual(values["VMANGOS_CLIENT_BUILD"], "5875")
        self.assertEqual(stat.S_IMODE(self.environment.stat().st_mode), 0o600)

    def test_new_defaults_are_merged_into_existing_env(self):
        content = self.template.read_text(encoding="utf-8")
        content = "\n".join(line for line in content.splitlines() if not line.startswith("TZ=")) + "\n"
        self.environment.write_text(content, encoding="utf-8")

        values = self.prepare(self.arguments())

        self.assertEqual(values["TZ"], "Etc/UTC")

    def test_cli_values_update_env_without_rewriting_compose(self):
        self.environment.write_text(self.template.read_text(encoding="utf-8"), encoding="utf-8")

        values = self.prepare(
            self.arguments(client=4222, realm_address="realm.example.org", anticheat=0)
        )

        self.assertEqual(values["VMANGOS_CLIENT_BUILD"], "4222")
        self.assertEqual(values["VMANGOS_REALM_ADDRESS"], "realm.example.org")
        self.assertEqual(values["VMANGOS_ANTICHEAT"], "0")
        self.assertNotIn(":ro:ro", (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8"))

    def test_invalid_port_is_rejected(self):
        values = setup.load_env(self.template)
        values["VMANGOS_REALM_PORT"] = "70000"

        with self.assertRaisesRegex(setup.SetupError, "between 1 and 65535"):
            setup.validate_env(values)

    def test_invalid_env_line_has_a_line_number(self):
        broken = self.root / "broken.env"
        broken.write_text("GOOD=value\nnot-an-assignment\n", encoding="utf-8")

        with self.assertRaisesRegex(setup.SetupError, r"broken.env:2"):
            setup.load_env(broken)


class WorkflowTests(unittest.TestCase):
    def test_submodule_update_stays_on_pinned_revisions(self):
        with mock.patch.object(setup, "run") as run:
            setup.update_submodules(4)

        command = run.call_args.args[0]
        self.assertIn("--recursive", command)
        self.assertNotIn("--remote", command)

    def test_dependency_failure_is_actionable(self):
        responses = [
            subprocess.CompletedProcess(("git", "--version"), 0, "git version 2.0", ""),
            subprocess.CompletedProcess(("docker", "version"), 1, "", "permission denied"),
        ]
        with mock.patch.object(setup.shutil, "which", return_value="/usr/bin/tool"), mock.patch.object(
            setup, "run", side_effect=responses
        ):
            with self.assertRaisesRegex(setup.SetupError, "Docker daemon is unavailable: permission denied"):
                setup.check_dependencies()

    def test_database_wait_retries_until_authenticated(self):
        failures = [subprocess.CompletedProcess((), 1, "", "") for _ in range(2)]
        success = subprocess.CompletedProcess((), 0, "1", "")
        with mock.patch.object(setup, "compose", side_effect=[*failures, success]) as compose, mock.patch.object(
            setup.time, "sleep"
        ), mock.patch.object(setup.time, "monotonic", side_effect=[0, 0, 1, 2]):
            setup.wait_for_database(timeout=10)

        self.assertEqual(compose.call_count, 3)


class RuntimeTemplateTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.secret = self.root / "password"
        self.secret.write_text("0123456789abcdef" * 4 + "\n", encoding="utf-8")

    def render(self, client, anticheat=1):
        output = self.root / f"mangosd-{client}.conf"
        environment = os.environ.copy()
        environment.update(
            {
                "VMANGOS_CONFIG_TEMPLATE": str(PROJECT_ROOT / "config/mangosd.conf"),
                "VMANGOS_CONFIG_PATH": str(output),
                "VMANGOS_DB_HOST": "db.example",
                "VMANGOS_DB_PORT": "3307",
                "VMANGOS_DB_USER": "app",
                "VMANGOS_DB_PASSWORD_FILE": str(self.secret),
                "VMANGOS_REALM_ID": "7",
                "VMANGOS_CLIENT_BUILD": str(client),
                "VMANGOS_ANTICHEAT": str(anticheat),
            }
        )
        subprocess.run(
            (str(PROJECT_ROOT / "docker/server-entrypoint.sh"), "true"),
            check=True,
            cwd=PROJECT_ROOT,
            env=environment,
        )
        return output

    def test_every_supported_client_renders_the_matching_patch(self):
        for client, patch in setup.CLIENT_PATCHES.items():
            with self.subTest(client=client):
                output = self.render(client, anticheat=0)
                content = output.read_text(encoding="utf-8")
                self.assertIn(f"WowPatch = {patch}", content)
                self.assertIn("RealmID = 7", content)
                self.assertIn("Anticheat.Enable = 0", content)
                self.assertNotIn("__VMANGOS_", content)
                self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

    def test_connection_delimiters_are_rejected(self):
        environment = os.environ.copy()
        environment.update(
            {
                "VMANGOS_CONFIG_TEMPLATE": str(PROJECT_ROOT / "config/mangosd.conf"),
                "VMANGOS_CONFIG_PATH": str(self.root / "bad.conf"),
                "VMANGOS_DB_HOST": "db;injected",
                "VMANGOS_DB_PASSWORD_FILE": str(self.secret),
            }
        )

        result = subprocess.run(
            (str(PROJECT_ROOT / "docker/server-entrypoint.sh"), "true"),
            cwd=PROJECT_ROOT,
            env=environment,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported character", result.stderr)


class UpstreamConfigTests(unittest.TestCase):
    def apply_replacements(self, source, replacements):
        for original, replacement in replacements:
            self.assertIn(original, source)
            source = source.replace(original, replacement, 1)
        return source.rstrip("\n")

    def test_mangos_template_matches_the_pinned_core(self):
        source = (PROJECT_ROOT / "src/core/src/mangosd/mangosd.conf.dist.in").read_text(encoding="utf-8")
        expected = self.apply_replacements(
            source,
            (
                ("RealmID = 1", "RealmID = __VMANGOS_REALM_ID__"),
                ("LogsDir = \"\"", "LogsDir = \"/var/log/vmangos\""),
                (
                    'LoginDatabase.Info = "127.0.0.1;3306;mangos;mangos;realmd"',
                    'LoginDatabase.Info = "__VMANGOS_DB_HOST__;__VMANGOS_DB_PORT__;'
                    '__VMANGOS_DB_USER__;__VMANGOS_DB_PASSWORD__;realmd"',
                ),
                (
                    'WorldDatabase.Info = "127.0.0.1;3306;mangos;mangos;mangos"',
                    'WorldDatabase.Info = "__VMANGOS_DB_HOST__;__VMANGOS_DB_PORT__;'
                    '__VMANGOS_DB_USER__;__VMANGOS_DB_PASSWORD__;mangos"',
                ),
                (
                    'CharacterDatabase.Info = "127.0.0.1;3306;mangos;mangos;characters"',
                    'CharacterDatabase.Info = "__VMANGOS_DB_HOST__;__VMANGOS_DB_PORT__;'
                    '__VMANGOS_DB_USER__;__VMANGOS_DB_PASSWORD__;characters"',
                ),
                (
                    'LogsDatabase.Info = "127.0.0.1;3306;mangos;mangos;logs"',
                    'LogsDatabase.Info = "__VMANGOS_DB_HOST__;__VMANGOS_DB_PORT__;'
                    '__VMANGOS_DB_USER__;__VMANGOS_DB_PASSWORD__;logs"',
                ),
                ("WowPatch = 10", "WowPatch = __VMANGOS_WOW_PATCH__"),
                ("Anticheat.Enable = 0", "Anticheat.Enable = __VMANGOS_ANTICHEAT__"),
            ),
        )

        actual = (PROJECT_ROOT / "config/mangosd.conf").read_text(encoding="utf-8").rstrip("\n")
        self.assertEqual(actual, expected)

    def test_realmd_template_matches_the_pinned_core(self):
        source = (PROJECT_ROOT / "src/core/src/realmd/realmd.conf.dist.in").read_text(encoding="utf-8")
        expected = self.apply_replacements(
            source,
            (
                (
                    'LoginDatabaseInfo = "127.0.0.1;3306;mangos;mangos;realmd"',
                    'LoginDatabaseInfo = "__VMANGOS_DB_HOST__;__VMANGOS_DB_PORT__;'
                    '__VMANGOS_DB_USER__;__VMANGOS_DB_PASSWORD__;realmd"',
                ),
                ("LogsDir = \"\"", "LogsDir = \"/var/log/vmangos\""),
            ),
        )

        actual = (PROJECT_ROOT / "config/realmd.conf").read_text(encoding="utf-8").rstrip("\n")
        self.assertEqual(actual, expected)


class SecretGenerationTests(unittest.TestCase):
    def test_generated_secrets_are_private_and_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            secret_directory = Path(directory) / "secrets"
            environment = os.environ.copy()
            environment["VMANGOS_SECRETS_DIR"] = str(secret_directory)
            command = (str(PROJECT_ROOT / "scripts/generate-secrets.sh"),)

            subprocess.run(command, check=True, cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True)
            before = {path.name: path.read_text(encoding="utf-8") for path in secret_directory.iterdir()}
            subprocess.run(command, check=True, cwd=PROJECT_ROOT, env=environment, capture_output=True, text=True)
            after = {path.name: path.read_text(encoding="utf-8") for path in secret_directory.iterdir()}

            self.assertEqual(before, after)
            self.assertEqual(set(before), {"mariadb_root_password", "vmangos_db_password"})
            self.assertNotEqual(before["mariadb_root_password"], before["vmangos_db_password"])
            self.assertEqual(stat.S_IMODE(secret_directory.stat().st_mode), 0o700)
            for path in secret_directory.iterdir():
                self.assertRegex(path.read_text(encoding="utf-8").strip(), r"^[0-9a-f]{64}$")
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o644)

    def test_existing_private_secrets_become_container_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            secret_directory = Path(directory) / "secrets"
            secret_directory.mkdir()
            existing = secret_directory / "vmangos_db_password"
            existing.write_text("0123456789abcdef" * 4 + "\n", encoding="utf-8")
            existing.chmod(0o600)
            environment = os.environ.copy()
            environment["VMANGOS_SECRETS_DIR"] = str(secret_directory)

            subprocess.run(
                (str(PROJECT_ROOT / "scripts/generate-secrets.sh"),),
                check=True,
                cwd=PROJECT_ROOT,
                env=environment,
                capture_output=True,
                text=True,
            )

            self.assertEqual(existing.read_text(encoding="utf-8"), "0123456789abcdef" * 4 + "\n")
            self.assertEqual(stat.S_IMODE(existing.stat().st_mode), 0o644)


if __name__ == "__main__":
    unittest.main()
