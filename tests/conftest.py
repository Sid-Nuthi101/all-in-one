import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"{name} must be set to run live Firestore tests")
    return value


@pytest.fixture(scope="session")
def firestore_client():
    firestore = pytest.importorskip("google.cloud.firestore")
    project_id = _require_env("FIREBASE_PROJECT_ID")
    return firestore.Client(project=project_id)


@pytest.fixture()
def test_apple_sub():
    return _require_env("FIREBASE_TEST_APPLE_SUB")
