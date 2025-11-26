import React, { useState } from "react";

const Anime = () => {
  const [inputText, setInputText] = useState("");
  const [responseText, setResponseText] = useState("");
  const [showResponse, setShowResponse] = useState(false);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);

  // Normal (non-streaming) submit - optional
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputText.trim()) {
      alert("Please enter a question.");
      return;
    }

    setLoading(true);
    setShowResponse(false);
    setResponseText("");

    try {
      const res = await fetch("/api/anime", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_: inputText }),
      });

      if (!res.ok) {
        console.error("Backend status:", res.status);
        const text = await res.text().catch(() => "");
        console.error("Backend body:", text);
        alert("Backend error. Check logs.");
        return;
      }

      const json = await res.json();
      if (json.status === "success") {
        setResponseText(json.response || "");
        setShowResponse(true);
        setInputText("");
      } else {
        alert(json.message || json.error || "Unknown error from backend.");
      }
    } catch (err) {
      console.error("Network error:", err);
      alert("Network error. Is backend running?");
    } finally {
      setLoading(false);
    }
  };

  // Streaming version
  const handleStream = (e) => {
    e.preventDefault();

    if (!inputText.trim()) {
      alert("Please enter a question.");
      return;
    }

    setResponseText("");
    setShowResponse(true);
    setStreaming(true);

    // SSE only supports GET, so we pass query as ?q=
    const url = `/api/anime_stream?q=${encodeURIComponent(inputText)}`;
    const es = new EventSource(url);

    es.onmessage = (event) => {
      const chunk = event.data;
      if (chunk === "[END]") {
        es.close();
        setStreaming(false);
        setInputText("");
      } else {
        setResponseText((prev) => (prev ? prev + " " + chunk : chunk));
      }
    };

    es.onerror = (err) => {
      console.error("SSE error:", err);
      es.close();
      setStreaming(false);
      alert("Streaming connection error. Check backend.");
    };
  };

  const handleReset = (e) => {
    e.preventDefault();
    setInputText("");
    setResponseText("");
    setShowResponse(false);
    setLoading(false);
    setStreaming(false);
  };

  return (
    <div className="container mt-4">
      <h2 className="mb-3">Anime Q&A</h2>

      <form onSubmit={handleSubmit}>
        {/* Input textarea */}
        <div className="mb-3">
          <label htmlFor="input_" className="form-label">
            Ask something about Anime
          </label>
          <textarea
            className="form-control"
            rows="6"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            id="input_"
            placeholder="Type your question here..."
          ></textarea>
        </div>

        {/* Buttons row */}
        <div className="mb-3 d-flex justify-content-between align-items-center">
          <div>
            <button
              type="submit"
              className="btn btn-success me-2"
              disabled={loading || streaming}
            >
              {loading ? "Thinking..." : "Submit (full)"}
            </button>

            <button
              type="button"
              className="btn btn-primary"
              onClick={handleStream}
              disabled={loading || streaming}
            >
              {streaming ? "Streaming..." : "Stream answer"}
            </button>
          </div>

          <button
            type="button"
            onClick={handleReset}
            className="btn btn-secondary"
            disabled={loading || streaming}
          >
            Reset
          </button>
        </div>

        {/* Response textarea */}
        {showResponse && (
          <div className="mb-3">
            <label htmlFor="response_" className="form-label">
              Response
            </label>
            <textarea
              className="form-control"
              rows="8"
              value={responseText}
              readOnly
              id="response_"
            ></textarea>
          </div>
        )}
      </form>
    </div>
  );
};

export default Anime;
