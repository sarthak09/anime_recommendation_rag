# tests/test_app_import.py
import os
import sys

# Make sure the backend module is importable no matter where pytest is run from
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import backend  # type: ignore  # noqa: E402


def test_app_imports_and_has_routes():
    """Sanity check that the Flask app imports and basic routing works."""
    assert backend.app is not None

    backend.app.config["TESTING"] = True
    with backend.app.test_client() as client:
        # There is no "/" route, so we expect a 404 from root
        resp = client.get("/")
        assert resp.status_code == 404
