from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory
from dataloader import Dataloader
from split import Splitter
from embedding import Embed
from vectorestor import VectorStore
from llm import LLM
from chains import Chain
import os
import json
from flask_cors import CORS

# Serve React build files
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

data_dir = "./backend/data"
db_dir = "./backend/db"
embedding_model = "sentence-transformers/all-mpnet-base-v2"
llm_model = "groq:llama-3.1-8b-instant"
k_docs = 3
rag_chain = None 

def initialize_rag():
    global rag_chain
    dataloader = Dataloader(data_dir)
    splitter = Splitter(dataloader.documents)
    embedder = Embed(embedding_model)
    vectorstore = VectorStore(splitter.chunks, embedder.embed, db_dir)
    llm = LLM(llm_model)
    retriever = vectorstore.vectorstore.as_retriever(search_kwargs={"k": k_docs})
    rag_chain = Chain(retriever, llm.llm)
    return True

@app.route('/api/anime', methods=['POST'])
def query_endpoint():
    try:
        global rag_chain
        data = request.json
        query = data['input_']
        print("Received query:", query)
        if rag_chain is None:
            initialize_rag()
        response = rag_chain.invoke(query=query)
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        print("QUERY ERROR:", e, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/anime_stream', methods=['GET'])
def query_stream():
    try:
        global rag_chain
        query = request.args.get('q', '')
        print("Received query for streaming:", query)
        if rag_chain is None:
            initialize_rag()
        
        def generate():
            response = rag_chain.invoke(query=query)
            for word in response.split():
                yield f"data: {word} \n\n"
            yield "data: [END] \n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
        )
    except Exception as e:
        print("STREAM ERROR:", e, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/initialize', methods=['POST'])
def init_endpoint():
    try:
        config = request.json
        global data_dir, db_dir, embedding_model, llm_model, k_docs
        if 'data_dir' in config:
            data_dir = config['data_dir']
        if 'db_dir' in config:
            db_dir = config['db_dir']
        if 'embedding_model' in config:
            embedding_model = config['embedding_model']
        if 'llm_model' in config:
            llm_model = config['llm_model']
        if 'k_docs' in config:
            k_docs = int(config['k_docs'])
        initialize_rag()
        return jsonify({"status": "success", "message": "RAG system initialized successfully"})
    except Exception as e:
        print("INIT ERROR:", e, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

# Serve React app
@app.route('/')
def serve_react():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
#    initialize_rag()
    app.run(host='0.0.0.0', port=5000)
