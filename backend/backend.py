from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dataloader import Dataloader
from split import Splitter
from embedding import Embed
from vectorestor import VectorStore
from llm import LLM
from chains import Chain
import traceback
import time

app = Flask(__name__)

# You technically don't need CORS if using Vite proxy, but it's still fine to keep:
CORS(app)

# ---- RAG CONFIG ----
data_dir = "./data"
db_dir = "./db"
embedding_model = "sentence-transformers/all-mpnet-base-v2"
llm_model = "groq:llama-3.1-8b-instant"
k_docs = 3

rag_chain = None  # global instance


def initialize_rag():
    """Initialize RAG pipeline and store in global rag_chain."""
    global rag_chain, data_dir, db_dir, embedding_model, llm_model, k_docs

    try:
        print("Initializing RAG pipeline...", flush=True)

        dataloader = Dataloader(data_dir)
        splitter = Splitter(dataloader.documents)
        embedder = Embed(embedding_model)
        vectorstore = VectorStore(splitter.chunks, embedder.embed, db_dir)

        llm = LLM(llm_model)

        # adjust search_kwargs if your VectorStore wrapper needs something else
        retriever = vectorstore.vectorstore.as_retriever(
            search_kwargs={"k": k_docs}
        )

        rag_chain = Chain(retriever, llm.llm)

        print("RAG pipeline initialized.", flush=True)
    except Exception as e:
        print("ERROR during RAG init:", e, flush=True)
        traceback.print_exc()
        rag_chain = None
        raise


def run_rag_query(query: str) -> str:
    """Helper to run the chain and return a plain string answer."""
    global rag_chain
    if rag_chain is None:
        initialize_rag()

    raw = rag_chain.invoke(query=query)
    print("Raw chain result:", raw, flush=True)

    if isinstance(raw, dict):
        answer = (
            raw.get("answer")
            or raw.get("output_text")
            or raw.get("result")
            or str(raw)
        )
    else:
        answer = str(raw)

    print("Final answer:", answer, flush=True)
    return answer


@app.route("/api/anime", methods=["POST"])
def query_endpoint():
    """Non-streaming endpoint."""
    try:
        data = request.get_json(force=True) or {}
        query = (data.get("input_", "") or "").strip()
        print("Received query:", query, flush=True)

        if not query:
            return jsonify(
                {"status": "error", "message": "input_ field is required"}
            ), 400

        answer = run_rag_query(query)
        return jsonify({"status": "success", "response": answer}), 200

    except Exception as e:
        print("QUERY ERROR:", e, flush=True)
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/anime_stream", methods=["GET"])
def query_stream_endpoint():
    """
    Streaming endpoint.
    For simplicity, we:
      1) Run the RAG once to get the full answer
      2) Stream it back in smaller chunks

    Later you can replace (1) with a truly streaming LLM/RAG.
    """
    try:
        query = (request.args.get("q", "") or "").strip()
        print("Received streaming query:", query, flush=True)

        if not query:
            return jsonify(
                {"status": "error", "message": "Missing q query parameter"}
            ), 400

        # Run RAG (this part can take ~20s)
        answer = run_rag_query(query)

        def generate():
            # Fake streaming: word-by-word; adjust as you like
            for word in answer.split():
                # SSE format: "data: <payload>\n\n"
                yield f"data: {word} \n\n"
                time.sleep(0.05)  # small delay to simulate streaming

            # Signal end of stream if you want:
            yield "data: [END] \n\n"

        # Server-Sent Events (SSE)
        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
        )

    except Exception as e:
        print("STREAM QUERY ERROR:", e, flush=True)
        traceback.print_exc()
        # Even for errors, SSE responses are tricky; here we just return JSON
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/initialize", methods=["POST"])
def init_endpoint():
    """Optional config endpoint, like before."""
    try:
        config = request.get_json(force=True) or {}
        global data_dir, db_dir, embedding_model, llm_model, k_docs

        if "data_dir" in config:
            data_dir = config["data_dir"]
        if "db_dir" in config:
            db_dir = config["db_dir"]
        if "embedding_model" in config:
            embedding_model = config["embedding_model"]
        if "llm_model" in config:
            llm_model = config["llm_model"]
        if "k_docs" in config:
            k_docs = int(config["k_docs"])

        initialize_rag()
        return jsonify(
            {"status": "success", "message": "RAG system initialized successfully"}
        ), 200
    except Exception as e:
        print("INIT ERROR:", e, flush=True)
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    try:
        initialize_rag()
    except Exception:
        pass

    app.run(host="0.0.0.0", port=5000, debug=True)
