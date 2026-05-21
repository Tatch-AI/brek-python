from __future__ import annotations

import base64
import importlib
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Params:
    key: str = ""
    region: str = ""


def Loader(params: Any) -> str:
    parsed = parse_params(params)
    boto3 = _import_boto3()
    client = boto3.client("secretsmanager", region_name=parsed.region)
    response = client.get_secret_value(SecretId=parsed.key)

    if isinstance(response, dict):
        secret_string = response.get("SecretString")
        secret_binary = response.get("SecretBinary")
    else:
        secret_string = getattr(response, "SecretString", None)
        secret_binary = getattr(response, "SecretBinary", None)

    if secret_string is not None:
        return str(secret_string)

    if secret_binary:
        if isinstance(secret_binary, str):
            secret_binary = secret_binary.encode("utf-8")
        return base64.b64encode(bytes(secret_binary)).decode("ascii")

    raise ValueError(f'awsSecret: secret "{parsed.key}" returned empty value')


def parse_params(params: Any) -> Params:
    if isinstance(params, Params):
        return validate_params(params)

    if isinstance(params, dict):
        return validate_params(
            Params(
                key=string_from_map(params, "key"),
                region=string_from_map(params, "region"),
            )
        )

    raise ValueError("awsSecret: params must be an object with key and region")


def validate_params(params: Params) -> Params:
    params.key = params.key.strip()
    params.region = params.region.strip()
    if not params.key or not params.region:
        raise ValueError("awsSecret: params must include key and region")
    return params


def string_from_map(value: dict[str, Any], key: str) -> str:
    item = value.get(key, "")
    if isinstance(item, str):
        return item
    return str(item) if item not in (None, "") else ""


def _import_boto3():
    try:
        return importlib.import_module("boto3")
    except ModuleNotFoundError as exc:
        raise RuntimeError("awsSecret loader requires boto3 to be installed") from exc
