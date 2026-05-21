from __future__ import annotations

import os
import sys


def debug(*args: object) -> None:
    if not os.getenv("BREK_DEBUG"):
        return

    print("[BREK][DEBUG]", *args, file=sys.stdout)
