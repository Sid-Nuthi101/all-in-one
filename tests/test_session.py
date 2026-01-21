import os

import session


def test_session_save_and_load_roundtrip(tmp_path, monkeypatch):
    session_path = tmp_path / "session.json"
    monkeypatch.setenv("AIO_SESSION_PATH", str(session_path))

    assert session.load_user_id() is None

    session.save_user_id("user-123")
    assert session.load_user_id() == "user-123"

    os.environ.pop("AIO_SESSION_PATH", None)
