from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_SESSION_PATH = Path.home() / ".all-in-one" / "session.json"


def _session_path() -> Path:
    override = os.environ.get("AIO_SESSION_PATH")
    if override:
        return Path(override)
    return DEFAULT_SESSION_PATH


def load_user_id() -> Optional[str]:
    path = _session_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    user_id = data.get("user_id") if isinstance(data, dict) else None
    return user_id or None


def save_user_id(user_id: str) -> None:
    path = _session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"user_id": user_id}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
