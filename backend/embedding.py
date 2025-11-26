# embedding.py
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

class Embed:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        self.embed = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"}
        )
    
    def test_embedding(self, text="hello world"):
        print(self.embed.embed_query(text))
