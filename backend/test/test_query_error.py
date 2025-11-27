# tests/test_query_error.py
import os
import sys
import json

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import backend  # type: ignore  # noqa: E402


def test_query_endpoint_missing_input_key():
    """
    POST /anime without 'input_' key should hit the error path
    and return status='error' with a 500.
    """
    # Make sure we don't accidentally invoke a heavy initialize
    backend.rag_chain = None

    backend.app.config["TESTING"] = True
    with backend.app.test_client() as client:
        # Missing 'input_' on purpose
        payload = {"not_input": "Something"}
        resp = client.post(
            "/anime",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert resp.status_code == 500
        data = resp.get_json()
        assert data["status"] == "error"
        # The exact message may vary, but it should exist
        assert "message" in data
