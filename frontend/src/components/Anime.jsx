import React, { useState } from "react";

// Vite env: must start with VITE_
const API_BASE_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

const Anime = () => {
  const [inputText, setInputText] = useState("");
  const [responseText, setResponseText] = useState("");
  const [showResponse, setShowResponse] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputText.trim()) {
      alert("Please enter a question.");
      return;
    }

    setLoading(true);
    setShowResponse(false);
    setResponseText("");

    // AbortController for manual timeout
    const controller = new AbortController();
    const timeoutMs = 60000; // 60 seconds

    const timeoutId = setTimeout(() => {
      controller.abort();
    }, timeoutMs);

    try {
      const response = await fetch(`${API_BASE_URL}/anime`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ input_: inputText }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.error("Backend HTTP status:", response.status);
        const text = await response.text().catch(() => "");
        console.error("Backend response body:", text);
        alert("Backend error. Check Flask logs.");
        return;
      }

      const json = await response.json();
      console.log("Backend JSON:", json);

      if (json.status === "success") {
        setResponseText(json.response || "");
        setShowResponse(true);
        setInputText(""); // clear user input
      } else {
        alert(json.message || json.error || "Unknown error from backend.");
      }
    } catch (err) {
      clearTimeout(timeoutId);

      if (err.name === "AbortError") {
        console.error("Request timed out after 60 seconds");
        alert("The request took too long (over 60s). Please try again.");
      } else {
        console.error("Network or CORS error:", err);
        alert(
          "Network/CORS error. Check if backend is running, reachable, and CORS is configured."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = (e) => {
    e.preventDefault();
    setInputText("");
    setResponseText("");
    setShowResponse(false);
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
            name="input_"
            id="input_"
            placeholder="Type your question here..."
          ></textarea>
        </div>

        {/* Buttons row */}
        <div className="mb-3 d-flex justify-content-between align-items-center">
          <button type="submit" className="btn btn-success" disabled={loading}>
            {loading ? "Thinking..." : "Submit"}
          </button>

          <button
            type="button"
            onClick={handleReset}
            className="btn btn-secondary"
            disabled={loading}
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
