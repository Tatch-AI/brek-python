from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .errors import InvalidConf


def read_json_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    data = file_path.read_bytes()
    if not data.strip():
        raise InvalidConf([f"{file_path} is not valid JSON"])

    try:
        decoded = json.loads(data)
    except json.JSONDecodeError as exc:
        raise InvalidConf([f"{file_path} is not valid JSON"]) from exc

    if not isinstance(decoded, dict):
        raise InvalidConf([f"{file_path} is not valid JSON"])

    return decoded


def write_json_file(path: str | Path, value: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=file_path.parent,
        delete=False,
    ) as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)

    os.replace(tmp_path, file_path)


ReadJSONFile = read_json_file
WriteJSONFile = write_json_file
