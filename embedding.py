from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

class Embed:
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        self.embed = HuggingFaceEmbeddings(model=model_name)

    def test_embedding(self, sample_text="Hello world"):
        print(self.embed.embed_query(sample_text))

# Embedder = Embed("sentence-transformers/all-mpnet-base-v2")
# Embedder.test_embedding("Hello world")