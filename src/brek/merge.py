from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .env import EnvArguments
from .errors import InvalidConf
from .jsonutil import read_json_file
from .loader import is_loader
from .paths import config_dir


@dataclass(slots=True)
class ConfSources:
    default: dict[str, Any]
    environment: dict[str, Any]
    deployment: dict[str, Any]
    user: dict[str, Any]
    overrides: dict[str, Any]


def load_conf_from_files(env: EnvArguments) -> ConfSources:
    default_conf = load_conf_file("default.json")

    environment: dict[str, Any] = {}
    if env.environment:
        environment = load_conf_file("environments", f"{env.environment}.json")

    deployment: dict[str, Any] = {}
    if env.deployment:
        deployment = load_conf_file("deployments", f"{env.deployment}.json")

    user: dict[str, Any] = {}
    if env.user:
        user = load_conf_file("users", f"{env.user}.json")

    return ConfSources(
        default=default_conf,
        environment=environment,
        deployment=deployment,
        user=user,
        overrides=env.overrides,
    )


def load_conf_file(*parts: str) -> dict[str, Any]:
    path = Path(config_dir(), *parts)
    try:
        path.read_bytes()
    except OSError:
        return {}

    try:
        return read_json_file(path)
    except InvalidConf:
        raise


def merge_confs(sources: ConfSources) -> dict[str, Any]:
    configs = [
        sources.default,
        sources.environment,
        sources.deployment,
        sources.user,
        sources.overrides,
    ]

    merged: dict[str, Any] = {}
    for config in configs:
        merged = _merge_configs(merged, config)
    return merged


def _merge_configs(left: dict[str, Any] | None, right: dict[str, Any] | None) -> dict[str, Any]:
    left = left or {}
    right = right or {}

    merged = dict(left)
    merged.update(right)

    for key, left_value in left.items():
        right_value = right.get(key)
        if right_value is None:
            continue

        if not isinstance(left_value, dict) or not isinstance(right_value, dict):
            continue

        if is_loader(left_value) or is_loader(right_value):
            continue

        merged[key] = _merge_configs(left_value, right_value)

    return merged


LoadConfFromFiles = load_conf_from_files
LoadConfFile = load_conf_file
MergeConfs = merge_confs
