import React, { useState, useRef } from "react";

const Anime = () => {
  const [inputText, setInputText] = useState("");
  const [responseText, setResponseText] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const abortControllerRef = useRef(null);

  const handleStandardSubmit = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    setResponseText("");
    setStatusMessage("Processing...");
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch("/api/anime", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_: inputText }),
        signal: abortControllerRef.current.signal
      });

      const json = await response.json();

      if (json.status === "success") {
        setResponseText(json.response);
        setInputText("");
      }
    } catch (err) {
      setStatusMessage(err.name === "AbortError" ? "Cancelled" : "Error");
    } finally {
      setLoading(false);
      setStatusMessage("");
    }
  };

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setLoading(false);
    setStatusMessage("");
  };

  const handleReset = () => {
    handleCancel();
    setInputText("");
    setResponseText("");
  };

  return (
    <div className="container mt-4">
      <h2 className="mb-3">Anime Q&A</h2>

      <div className="mb-3">
        <textarea
          className="form-control"
          rows="6"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type your question here..."
          disabled={loading}
        />
      </div>

      {statusMessage && (
        <div className="alert alert-info">{statusMessage}</div>
      )}

      <div className="mb-3 d-flex gap-2">
        <button
          onClick={handleStandardSubmit}
          className="btn btn-success"
          disabled={loading || !inputText.trim()}
        >
          Standard
        </button>

        <button
          onClick={handleCancel}
          className="btn btn-warning"
          disabled={!loading}
        >
          Cancel
        </button>

        <button
          onClick={handleReset}
          className="btn btn-secondary"
        >
          Reset
        </button>
      </div>

      {responseText && (
        <div className="mb-3">
          <label className="form-label">Response</label>
          <textarea
            className="form-control"
            rows="10"
            value={responseText}
            readOnly
          />
        </div>
      )}
    </div>
  );
};

export default Anime;
