from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .errors import ConfigPathNotFound


def _normalize_path(path: tuple[str, ...]) -> list[str]:
    if not path:
        raise ValueError("path must not be empty")
    if len(path) == 1 and "." in path[0]:
        parts = [segment for segment in path[0].split(".") if segment]
        if not parts:
            raise ValueError("path must not be empty")
        return parts
    return [segment for segment in path if segment]


def require_path(value: Any, *path: str) -> Any:
    segments = _normalize_path(path)
    current: Any = value
    traversed: list[str] = []

    for segment in segments:
        traversed.append(segment)

        if isinstance(current, Mapping):
            if segment not in current:
                raise ConfigPathNotFound(traversed)
            current = current[segment]
            continue

        if isinstance(current, Sequence) and not isinstance(current, (str, bytes, bytearray)):
            try:
                index = int(segment)
            except ValueError as exc:
                raise ConfigPathNotFound(traversed) from exc

            if index < 0 or index >= len(current):
                raise ConfigPathNotFound(traversed)

            current = current[index]
            continue

        raise ConfigPathNotFound(traversed)

    return current


def optional_path(value: Any, *path: str, default: Any = None) -> Any:
    try:
        return require_path(value, *path)
    except ConfigPathNotFound:
        return default


RequirePath = require_path
OptionalPath = optional_path
