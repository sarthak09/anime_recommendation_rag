from flask import Flask, request, jsonify
from dataloader import Dataloader
from split import Splitter
from embedding import Embed
from vectorestor import VectorStore
from llm import LLM
from chains import Chain
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data_dir = "./data"
db_dir = "./db"
embedding_model = "sentence-transformers/all-mpnet-base-v2"
llm_model = "groq:llama-3.1-8b-instant"
k_docs = 3

def initialize_rag():
    global rag_chain
    dataloader = Dataloader(data_dir)
    splitter = Splitter(dataloader.documents)
    embedder = Embed(embedding_model)
    vectorstore = VectorStore(splitter.chunks, embedder.embed, db_dir)
    llm = LLM(llm_model)
    retriever = vectorstore.vectorstore.as_retriever(search_kwarg={"k": k_docs})
    rag_chain = Chain(retriever, llm.llm)
    return True

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
            
        success = initialize_rag()
        return jsonify({"status": "success", "message": "RAG system initialized successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/query', methods=['POST'])
def query_endpoint():
    try:
        data = request.json
        query = data['query']
        
        if not hasattr(app, 'rag_chain'):
            initialize_rag()
            
        response = rag_chain.invoke(query=query)
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    initialize_rag()
    app.run(host='0.0.0.0', port=5000)