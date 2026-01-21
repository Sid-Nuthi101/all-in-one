from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class FileSessionStore:
    def __init__(self, path: Path):
        self._path = path

    def get(self) -> Optional[Dict[str, Any]]:
        if not self._path.exists():
            return None
        with self._path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def set(self, session: Dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(session, handle)
