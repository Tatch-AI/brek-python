from __future__ import annotations

from typing import Sequence


class InvalidConf(Exception):
    def __init__(self, validation_errors: Sequence[str]):
        self.validation_errors = list(validation_errors)
        super().__init__(str(self))

    def __str__(self) -> str:
        return "INVALID_CONF: " + ", ".join(self.validation_errors)


class ConfNotLoaded(Exception):
    def __str__(self) -> str:
        return "CONF_NOT_LOADED"


class LoaderNotFound(Exception):
    def __init__(self, loader_name: str, available: Sequence[str] | None):
        self.loader_name = loader_name
        self.available = list(available or [])
        super().__init__(str(self))

    def __str__(self) -> str:
        available = ", ".join(self.available) if self.available else "none"
        return f'LOADER_NOT_FOUND: "{self.loader_name}". Available loaders: {available}'


class ConfigPathNotFound(Exception):
    def __init__(self, path: Sequence[str]):
        self.path = list(path)
        super().__init__(str(self))

    def __str__(self) -> str:
        return f'CONFIG_PATH_NOT_FOUND: {".".join(self.path)}'
