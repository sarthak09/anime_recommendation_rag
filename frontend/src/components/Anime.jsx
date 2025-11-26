import React, { useState, useRef } from "react";

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

const Anime = () => {
  const [inputText, setInputText] = useState("");
  const [responseText, setResponseText] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const abortControllerRef = useRef(null);

  const handleStreamSubmit = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    setResponseText("");
    setStatusMessage("Connecting...");
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${API_BASE_URL}/anime/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_: inputText }),
        signal: abortControllerRef.current.signal
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      console.log("Started reading stream");
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value);
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6));

            if (data.type === "status") {
              setStatusMessage(data.message);
            } else if (data.type === "token") {
              setResponseText(prev => prev + data.content);
            } else if (data.type === "done") {
              setInputText("");
              setStatusMessage("");
            }
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setStatusMessage("Error: Try standard method");
      }
    } finally {
      setLoading(false);
      setStatusMessage("");
    }
  };

  const handleStandardSubmit = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    setResponseText("");
    setStatusMessage("Processing...");
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(`${API_BASE_URL}/anime`, {
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
          onClick={handleStreamSubmit}
          className="btn btn-primary"
          disabled={loading || !inputText.trim()}
        >
          Stream
        </button>

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