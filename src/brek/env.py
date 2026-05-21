from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from .errors import InvalidConf

_env_value_pattern = re.compile(r"^\$\{[a-zA-Z]+.*\}$")


@dataclass(slots=True)
class EnvArguments:
    environment: str
    deployment: str
    user: str
    overrides: dict[str, Any]


def is_environment_variable(value: str) -> bool:
    return bool(_env_value_pattern.match(value))


def os_env_first(*keys: str) -> str:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return ""


def get_env_overrides() -> dict[str, Any]:
    cli_overrides = os_env_first("BREK", "OVERRIDE")
    if not cli_overrides:
        return {}

    try:
        decoded = json.loads(cli_overrides)
    except json.JSONDecodeError as exc:
        raise InvalidConf(["CLI overrides (BREK/OVERRIDE) is not valid JSON"]) from exc

    if not isinstance(decoded, dict):
        raise InvalidConf(["CLI overrides (BREK/OVERRIDE) is not valid JSON"])

    return decoded


def get_env_arguments() -> EnvArguments:
    return EnvArguments(
        environment=os_env_first("ENVIRONMENT", "NODE_ENV"),
        deployment=os.getenv("DEPLOYMENT", ""),
        user=os.getenv("USER", ""),
        overrides=get_env_overrides(),
    )


IsEnvironmentVariable = is_environment_variable
GetEnvOverrides = get_env_overrides
GetEnvArguments = get_env_arguments
