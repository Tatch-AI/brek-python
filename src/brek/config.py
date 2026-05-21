from __future__ import annotations

from threading import RLock
from typing import Any

from .debug import debug
from .default_loaders import default_loaders
from .env import get_env_arguments
from .jsonutil import read_json_file, write_json_file
from .loader import LoaderDict
from .merge import load_conf_from_files, merge_confs
from .paths import config_json_path
from .resolve import resolve_conf

_cache_lock = RLock()
_loaders_lock = RLock()
_cached_config: dict[str, Any] | None = None
_custom_loaders: LoaderDict = {}


def clone_loaders(loaders: LoaderDict | None) -> LoaderDict:
    return dict(loaders or {})


def set_loaders(loaders: LoaderDict | None) -> None:
    global _custom_loaders
    with _loaders_lock:
        _custom_loaders = clone_loaders(loaders)


def current_loaders() -> LoaderDict:
    with _loaders_lock:
        merged = clone_loaders(default_loaders())
        merged.update(_custom_loaders)
        return merged


def get_config() -> dict[str, Any]:
    global _cached_config

    with _cache_lock:
        if _cached_config is not None:
            debug("get_config: returning cached config")
            return _cached_config

    path = config_json_path()
    if path.exists():
        conf = read_json_file(path)
        debug("get_config: loaded config.json from disk")
        with _cache_lock:
            _cached_config = conf
        return conf

    return load_config()


def load_config() -> dict[str, Any]:
    global _cached_config

    env = get_env_arguments()
    debug("load_config: env", env)

    sources = load_conf_from_files(env)
    debug("load_config: sources", sources)

    merged = merge_confs(sources)
    debug("load_config: merged", merged)

    resolved = resolve_conf(merged, current_loaders())
    debug("load_config: resolved", resolved)

    write_conf_json(resolved)

    with _cache_lock:
        _cached_config = resolved

    return resolved


def write_conf_json(resolved_conf: dict[str, Any]) -> None:
    write_json_file(config_json_path(), resolved_conf)


def delete_conf_json() -> None:
    path = config_json_path()
    debug("delete_conf_json:", path)
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def run(args: list[str]) -> dict[str, Any] | None:
    if not args:
        raise ValueError("usage: brek load-config")

    if args[0].strip() == "load-config":
        return load_config()

    raise ValueError("usage: brek load-config")


SetLoaders = set_loaders
GetConfig = get_config
LoadConfig = load_config
WriteConfJSON = write_conf_json
DeleteConfJSON = delete_conf_json
Run = run
