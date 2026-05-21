from __future__ import annotations

from typing import Any, Callable

Loader = Callable[[Any], str]
LoaderDict = dict[str, Loader]


def is_loader(prop: dict[str, Any]) -> bool:
    if len(prop) != 1:
        return False

    key = next(iter(prop))
    return key.startswith("[") and key.endswith("]")


def loader_name(prop: dict[str, Any]) -> str:
    if not prop:
        return ""
    key = next(iter(prop))
    return key[1:-1]


def available_loader_names(loaders: LoaderDict | None) -> list[str] | None:
    if not loaders:
        return None
    return sorted(loaders)


IsLoader = is_loader
LoaderName = loader_name
AvailableLoaderNames = available_loader_names
