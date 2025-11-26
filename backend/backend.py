from flask import Flask, request, jsonify, Response, stream_with_context
from dataloader import Dataloader
from split import Splitter
from embedding import Embed
from vectorestor import VectorStore
from llm import LLM
from chains import Chain
import os
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

data_dir = "./data"
db_dir = "./db"
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

@app.route('/anime', methods=['POST'])
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

@app.route('/anime/stream', methods=['POST'])
def query_stream():
    try:
        global rag_chain
        
        data = request.json
        query = data['input_']
        
        print("Received query for streaming:", query)
        if rag_chain is None:
            initialize_rag()
        
        def generate():
            yield f"data: {json.dumps({'type': 'status', 'message': 'Processing your request...'})}\n\n"
            
            response_text = ""
            for chunk in rag_chain.rag_chain_lcel.stream(query):
                if chunk:
                    response_text += chunk
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done', 'full_response': response_text})}\n\n"
            
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    except Exception as e:
        print("STREAM ERROR:", e, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/initialize', methods=['POST'])
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

if __name__ == '__main__':
    initialize_rag()
    app.run(host='0.0.0.0', port=5000)