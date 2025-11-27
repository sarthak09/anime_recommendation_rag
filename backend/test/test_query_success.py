# tests/test_query_success.py
import os
import sys
import json

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import backend  # type: ignore  # noqa: E402


class DummyChain:
    def invoke(self, query):
        # Simulate a simple RAG response
        return f"dummy response for: {query}"


def test_query_endpoint_success():
    """POST /anime with valid input_ should return a success JSON."""
    # Use dummy RAG so backend.initialize_rag is not called
    backend.rag_chain = DummyChain()

    backend.app.config["TESTING"] = True
    with backend.app.test_client() as client:
        payload = {"input_": "Recommend some anime"}
        resp = client.post(
            "/anime",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert "dummy response for: Recommend some anime" in data["response"]
