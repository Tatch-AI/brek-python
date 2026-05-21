from __future__ import annotations

import os
from pathlib import Path


def env_or(key: str, fallback: str) -> str:
    value = os.getenv(key)
    return value if value else fallback


def config_dir() -> str:
    return env_or("BREK_CONFIG_DIR", "config")


def write_dir() -> str:
    value = os.getenv("BREK_WRITE_DIR")
    return value if value else config_dir()


def loaders_file_path() -> str:
    return env_or("BREK_LOADERS_FILE_PATH", "brek.loaders.js")


def config_json_path() -> Path:
    return Path(write_dir()) / "config.json"


def config_lock_path() -> Path:
    return Path(write_dir()) / "config.lock"


ConfigDir = config_dir
WriteDir = write_dir
LoadersFilePath = loaders_file_path
ConfigJSONPath = config_json_path
ConfigLockPath = config_lock_path
