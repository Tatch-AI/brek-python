from __future__ import annotations

import sys

from .config import run


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        run(args)
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0
