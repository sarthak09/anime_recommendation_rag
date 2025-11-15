import streamlit as st
import requests
import json
import os

# Read API URL from environment variable (set by docker-compose)
API_URL = os.getenv("API_URL", "http://localhost:5000")

st.set_page_config(page_title="RAG System", layout="wide")
st.title("RAG Question Answering System")

with st.sidebar:
    st.header("Configuration")
    data_dir = st.text_input("Data Directory", value="./data")
    db_dir = st.text_input("Vector Database Directory", value="./db")
    embedding_model = st.selectbox(
        "Embedding Model",
        ["sentence-transformers/all-mpnet-base-v2", "sentence-transformers/all-MiniLM-L6-v2"]
    )
    llm_model = st.text_input("LLM Model", value="groq:llama-3.1-8b-instant")
    k_docs = st.number_input("Documents to retrieve", min_value=1, max_value=10, value=3)
    
    if st.button("Initialize System"):
        config = {
            "data_dir": data_dir,
            "db_dir": db_dir,
            "embedding_model": embedding_model,
            "llm_model": llm_model,
            "k_docs": k_docs
        }
        
        with st.spinner("Initializing RAG system..."):
            try:
                response = requests.post(f"{API_URL}/initialize", json=config)
                if response.status_code == 200:
                    st.success("System initialized successfully!")
                else:
                    st.error(f"Error: {response.json().get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

st.header("Ask a Question")

query = st.text_input("Enter your question:")

if st.button("Submit"):
    if not query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating answer..."):
            try:
                payload = {"query": query}
                response = requests.post(f"{API_URL}/query", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    st.header("Answer")
                    st.markdown(data["response"])
                else:
                    st.error(f"Error: {response.json().get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

st.markdown("---")
