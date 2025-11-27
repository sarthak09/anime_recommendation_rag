# tests/test_initialize_and_stream.py
import os
import sys
import json
import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import backend  # type: ignore  # noqa: E402


def test_initialize_endpoint(monkeypatch):
    """POST /initialize should update config variables and call initialize_rag."""
    called = {"init": False}

    def fake_init():
        called["init"] = True
        # Do not perform real heavy initialization
        backend.rag_chain = None
        return True

    # Replace the real initialize_rag with our fake
    monkeypatch.setattr(backend, "initialize_rag", fake_init)

    backend.app.config["TESTING"] = True
    with backend.app.test_client() as client:
        payload = {
            "data_dir": "./my_data",
            "db_dir": "./my_db",
            "embedding_model": "my-embed-model",
            "llm_model": "my-llm-model",
            "k_docs": 5,
        }
        resp = client.post(
            "/initialize",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert called["init"] is True

        # Check that the globals were updated
        assert backend.data_dir == "./my_data"
        assert backend.db_dir == "./my_db"
        assert backend.embedding_model == "my-embed-model"
        assert backend.llm_model == "my-llm-model"
        assert backend.k_docs == 5


class DummyLCEL:
    def stream(self, query):
        # Simulate streaming two text chunks
        for token in ["hello", "world"]:
            yield token


class DummyRagChain:
    def __init__(self):
        self.rag_chain_lcel = DummyLCEL()


def test_query_stream_endpoint(monkeypatch):
    """POST /anime/stream should return SSE text with our dummy chunks."""
    # Plug in dummy streaming RAG chain
    backend.rag_chain = DummyRagChain()

    backend.app.config["TESTING"] = True
    with backend.app.test_client() as client:
        payload = {"input_": "stream something"}
        resp = client.post(
            "/anime/stream",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert resp.status_code == 200
        assert resp.mimetype == "text/event-stream"

        # Join all chunks from the streaming response
        body = b"".join(resp.response).decode("utf-8")

        # We expect SSE-style "data: ..." lines that contain our dummy tokens
        assert "data:" in body
        assert "hello" in body
        assert "world" in body
