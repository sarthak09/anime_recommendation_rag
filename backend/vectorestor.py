from langchain_community.vectorstores import Chroma

class VectorStore:
    def __init__(self, chunks, embedding, persist_directory="./db"):
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding,
            persist_directory=persist_directory,
            collection_name="rag_collection"
        )

    def info(self):
        print(f"Vector store created with {self.vectorstore._collection.count()} vectors")



# vectorstore = VectorStore(splitter.chunks, Embedder.embed, "./db")
# vectorstore.info()