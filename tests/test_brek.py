from __future__ import annotations

import base64
import json
import os
import pathlib
import sys
import types
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) in sys.path:
    sys.path.remove(str(SRC))
sys.path.insert(0, str(SRC))

import brek
import brek.config as config_module
from brek import (
    AvailableLoaderNames,
    ConfNotLoaded,
    ConfigPathNotFound,
    ConfigDir,
    ConfigJSONPath,
    DefaultLoaders,
    DeleteConfJSON,
    GetEnvArguments,
    GetEnvOverrides,
    GetConfig,
    InvalidConf,
    IsEnvironmentVariable,
    IsLoader,
    LoadConfig,
    LoadConfFile,
    LoadConfFromFiles,
    LoaderNotFound,
    MergeConfs,
    Run,
    SetLoaders,
    OptionalPath,
    RequirePath,
    WriteConfJSON,
    available_loader_names,
    config_dir,
    config_json_path,
    delete_conf_json,
    env,
    get_config,
    get_env_arguments,
    get_env_overrides,
    is_environment_variable,
    is_loader,
    load_conf_file,
    load_conf_from_files,
    load_config,
    loader_name,
    merge_confs,
    optional_path,
    resolve_conf,
    run,
    require_path,
    set_loaders,
    write_conf_json,
)
from brek.loaders.awssecret import Loader as AwsSecretLoader, Params


def write_test_json(base_dir: pathlib.Path, rel: str, value: object) -> None:
    path = base_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2))


def read_test_json(path: pathlib.Path) -> dict[str, object]:
    return json.loads(path.read_text())


def reset_state() -> None:
    config_module._cached_config = None
    SetLoaders(None)


class BrekTestCase(unittest.TestCase):
    def tearDown(self) -> None:
        reset_state()


class TestHelpers(BrekTestCase):
    def test_path_helpers(self) -> None:
        with mock.patch.dict(os.environ, {
            "BREK_CONFIG_DIR": "/tmp/brek-config",
            "BREK_WRITE_DIR": "/tmp/brek-write",
            "BREK_LOADERS_FILE_PATH": "/tmp/loaders.py",
        }, clear=False):
            self.assertEqual(ConfigDir(), "/tmp/brek-config")
            self.assertEqual(brek.WriteDir(), "/tmp/brek-write")
            self.assertEqual(brek.LoadersFilePath(), "/tmp/loaders.py")
            self.assertEqual(ConfigJSONPath(), pathlib.Path("/tmp/brek-write/config.json"))

    def test_defaults(self) -> None:
        with mock.patch.dict(os.environ, {
            "BREK_CONFIG_DIR": "",
            "BREK_WRITE_DIR": "",
            "BREK_LOADERS_FILE_PATH": "",
        }, clear=False):
            self.assertEqual(config_dir(), "config")
            self.assertEqual(brek.write_dir(), "config")
            self.assertEqual(brek.loaders_file_path(), "brek.loaders.js")

    def test_loader_detection(self) -> None:
        self.assertTrue(IsLoader({"[foo]": "bar"}))
        self.assertFalse(IsLoader({"foo": "bar"}))
        self.assertFalse(IsLoader({}))
        self.assertFalse(IsLoader({"[foo]": "bar", "[bar]": "baz"}))
        self.assertEqual(loader_name({"[foo]": "bar"}), "foo")
        self.assertEqual(AvailableLoaderNames(None), None)
        self.assertEqual(available_loader_names({"b": lambda _: "" , "a": lambda _: ""}), ["a", "b"])

    def test_env_variable_detection(self) -> None:
        self.assertTrue(IsEnvironmentVariable("${FOO}"))
        self.assertFalse(IsEnvironmentVariable("${1FOO}"))

    def test_errors(self) -> None:
        self.assertEqual(str(InvalidConf(["a", "b"])), "INVALID_CONF: a, b")
        self.assertEqual(str(ConfNotLoaded()), "CONF_NOT_LOADED")
        self.assertEqual(str(LoaderNotFound("x", ["a", "b"])), 'LOADER_NOT_FOUND: "x". Available loaders: a, b')


class TestEnv(BrekTestCase):
    def test_get_env_arguments_and_overrides(self) -> None:
        with mock.patch.dict(os.environ, {
            "ENVIRONMENT": "prod",
            "NODE_ENV": "dev",
            "DEPLOYMENT": "blue",
            "USER": "alice",
            "BREK": '{"nested":{"count":3}}',
        }, clear=False):
            args = GetEnvArguments()
            self.assertEqual(args.environment, "prod")
            self.assertEqual(args.deployment, "blue")
            self.assertEqual(args.user, "alice")
            self.assertEqual(args.overrides, {"nested": {"count": 3}})

        with mock.patch.dict(os.environ, {"BREK": "", "OVERRIDE": '{"via":"override"}'}, clear=False):
            overrides = GetEnvOverrides()
            self.assertEqual(overrides, {"via": "override"})

    def test_invalid_overrides(self) -> None:
        with mock.patch.dict(os.environ, {"BREK": "{broken"}, clear=False):
            with self.assertRaises(InvalidConf):
                GetEnvArguments()

    def test_non_object_overrides(self) -> None:
        with mock.patch.dict(os.environ, {"BREK": "[]"}, clear=False):
            with self.assertRaises(InvalidConf):
                GetEnvOverrides()


class TestJsonAndMerge(BrekTestCase):
    def test_read_json_file_invalid(self) -> None:
        with mock.patch.dict(os.environ, {"BREK_CONFIG_DIR": self._tmp_dir()}, clear=False):
            base = pathlib.Path(config_dir())
            base.mkdir(parents=True, exist_ok=True)
            (base / "broken.json").write_text("{broken")
            with self.assertRaises(InvalidConf):
                LoadConfFile("broken.json")

    def test_merge_and_load(self) -> None:
        with mock.patch.dict(os.environ, {"BREK_CONFIG_DIR": self._tmp_dir()}, clear=False):
            base = pathlib.Path(config_dir())
            write_test_json(base, "default.json", {
                "port": 3000,
                "db": {
                    "host": "localhost",
                    "password": "base",
                },
                "arr": [1, 2],
            })
            write_test_json(base, "environments/prod.json", {
                "db": {
                    "password": "prod",
                }
            })
            write_test_json(base, "users/alice.json", {
                "db": {
                    "user": "alice",
                }
            })

            sources = LoadConfFromFiles(env.EnvArguments("prod", "", "alice", {"override": True}))
            merged = MergeConfs(sources)
            self.assertEqual(merged["db"], {"host": "localhost", "password": "prod", "user": "alice"})
            self.assertEqual(merged["override"], True)

    def test_load_conf_file_ignores_missing(self) -> None:
        with mock.patch.dict(os.environ, {"BREK_CONFIG_DIR": self._tmp_dir()}, clear=False):
            self.assertEqual(LoadConfFile("missing.json"), {})

    def _tmp_dir(self) -> str:
        return tempfile.mkdtemp(prefix="brek-python-")


class TestResolve(BrekTestCase):
    def test_resolve_env_and_loaders(self) -> None:
        with mock.patch.dict(os.environ, {"FOO": "env-value"}, clear=False):
            loaders = {"demo": lambda params: f"demo:{params}"}
            value = {
                "plain": "${FOO}",
                "nested": {
                    "a": 1,
                    "secret": {"[demo]": "x"},
                },
                "items": ["${FOO}", {"inner": "${FOO}"}],
            }
            resolved = resolve_conf(value, loaders)
            self.assertEqual(resolved["plain"], "env-value")
            self.assertEqual(resolved["nested"]["secret"], "demo:x")
            self.assertEqual(resolved["items"][0], "${FOO}")
            self.assertEqual(resolved["items"][1]["inner"], "env-value")

    def test_missing_loader(self) -> None:
        with self.assertRaises(LoaderNotFound):
            resolve_conf({"[missing]": "x"}, {})

    def test_missing_env_raises(self) -> None:
        with self.assertRaises(InvalidConf):
            resolve_conf({"secret": "${MISSING_ENV}"}, {})


class TestConfig(BrekTestCase):
    def test_load_get_delete_and_cache(self) -> None:
        with mock.patch.dict(os.environ, {"BREK_CONFIG_DIR": self._tmp_dir(), "BREK_WRITE_DIR": self._tmp_dir(), "USER": ""}, clear=False):
            base = pathlib.Path(config_dir())
            write_test_json(base, "default.json", {
                "port": 3000,
                "secret": {
                    "[demo]": "x"
                }
            })

            SetLoaders({"demo": lambda params: f"value:{params}"})

            resolved = LoadConfig()
            self.assertEqual(resolved["secret"], "value:x")

            cached = GetConfig()
            self.assertIs(cached, resolved)

            config_path = config_json_path()
            self.assertTrue(config_path.exists())
            self.assertEqual(read_test_json(config_path), resolved)

            DeleteConfJSON()
            self.assertFalse(config_path.exists())

    def test_run_usage(self) -> None:
        with self.assertRaises(ValueError):
            Run([])

    def _tmp_dir(self) -> str:
        return tempfile.mkdtemp(prefix="brek-python-")


class TestAccess(BrekTestCase):
    def test_require_path(self) -> None:
        value = {
            "integrations": {
                "google": {
                    "apiKey": "secret",
                }
            },
            "items": [{"name": "alpha"}],
        }

        self.assertEqual(require_path(value, "integrations.google.apiKey"), "secret")
        self.assertEqual(RequirePath(value, "items", "0", "name"), "alpha")

    def test_optional_path(self) -> None:
        value = {"foo": {"bar": 1}}

        self.assertEqual(optional_path(value, "foo.bar"), 1)
        self.assertEqual(OptionalPath(value, "missing.path", default="fallback"), "fallback")

    def test_missing_path_raises(self) -> None:
        with self.assertRaises(ConfigPathNotFound):
            require_path({"foo": {}}, "foo.bar")


class TestAwsSecretLoader(BrekTestCase):
    def test_loader_returns_secret_string(self) -> None:
        fake_client = types.SimpleNamespace(
            get_secret_value=lambda SecretId: {"SecretString": f"secret:{SecretId}"}
        )
        fake_boto3 = types.SimpleNamespace(
            client=lambda service_name, region_name=None: fake_client
        )
        with mock.patch.dict(sys.modules, {"boto3": fake_boto3}):
            self.assertEqual(AwsSecretLoader({"key": "demo", "region": "us-west-2"}), "secret:demo")

    def test_loader_returns_binary_secret(self) -> None:
        fake_client = types.SimpleNamespace(
            get_secret_value=lambda SecretId: {"SecretBinary": b"hello"}
        )
        fake_boto3 = types.SimpleNamespace(
            client=lambda service_name, region_name=None: fake_client
        )
        with mock.patch.dict(sys.modules, {"boto3": fake_boto3}):
            self.assertEqual(AwsSecretLoader({"key": "demo", "region": "us-west-2"}), base64.b64encode(b"hello").decode("ascii"))

    def test_loader_requires_params(self) -> None:
        with self.assertRaises(ValueError):
            AwsSecretLoader({"key": "", "region": "us-west-2"})


if __name__ == "__main__":
    unittest.main()
