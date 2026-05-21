from __future__ import annotations

import os
from typing import Any

from .errors import InvalidConf
from .env import is_environment_variable
from .errors import LoaderNotFound
from .loader import LoaderDict, available_loader_names, is_loader, loader_name


def resolve_conf(value: Any, loaders: LoaderDict) -> Any:
    return _resolve_any(value, loaders)


def _resolve_any(value: Any, loaders: LoaderDict) -> Any:
    if isinstance(value, dict):
        if is_loader(value):
            return _resolve_loader(value, loaders)
        return _resolve_map(value, loaders)

    if isinstance(value, list):
        out: list[Any] = []
        for item in value:
            if isinstance(item, (dict, list)):
                out.append(_resolve_any(item, loaders))
            else:
                out.append(item)
        return out

    if isinstance(value, str) and is_environment_variable(value):
        name = value[2:-1]
        env_value = os.getenv(name)
        if env_value is None or env_value == "":
            raise InvalidConf([f'environment variable "{name}" is not set'])
        return env_value

    return value


def _resolve_map(value: dict[str, Any], loaders: LoaderDict) -> dict[str, Any]:
    return {key: _resolve_any(value[key], loaders) for key in sorted(value)}


def _resolve_loader(prop: dict[str, Any], loaders: LoaderDict) -> Any:
    name = loader_name(prop)
    loader = loaders.get(name)
    if loader is None:
        raise LoaderNotFound(name, available_loader_names(loaders))

    params = next(iter(prop.values()))
    return loader(params)


ResolveConf = resolve_conf
